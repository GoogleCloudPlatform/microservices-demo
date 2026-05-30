// C++ reimplementation of currencyservice.
//
// Spec: src/currencyservice/currencyservice-spec.md
// Contract tests: src/currencyservice/tests/test_currency_contract.py
//
// Behaviour differences from the Node.js original (all documented as xfail
// in the test suite — they will flip to xpass here):
//   - Unknown currency codes return INVALID_ARGUMENT instead of silent zeros.
//   - Negative Money amounts produce the mathematically correct result because
//     the carry() helper uses trunc() instead of floor(), which correctly
//     handles negative intermediate values without double-subtracting the
//     fractional part (§6.5 of the spec).

#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>

#include <grpcpp/grpcpp.h>
#include <nlohmann/json.hpp>

// Generated proto headers (produced by CMake custom commands)
#include "demo.grpc.pb.h"
#include "demo.pb.h"
#include "grpc/health/v1/health.grpc.pb.h"
#include "grpc/health/v1/health.pb.h"

using grpc::InsecureServerCredentials;
using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using grpc::StatusCode;

using hipstershop::CurrencyConversionRequest;
using hipstershop::CurrencyService;
using hipstershop::Empty;
using hipstershop::GetSupportedCurrenciesResponse;
using hipstershop::Money;

using grpc::health::v1::Health;
using grpc::health::v1::HealthCheckRequest;
using grpc::health::v1::HealthCheckResponse;

// ---------------------------------------------------------------------------
// Exchange-rate table — loaded once at startup from currency_conversion.json.
// Keys are ISO 4217 codes; values are EUR-based rates (1 EUR = N units).
// ---------------------------------------------------------------------------

static std::map<std::string, double> g_rates;

static void LoadRates(const std::string& path) {
    std::ifstream f(path);
    if (!f.is_open()) {
        throw std::runtime_error("cannot open currency data file: " + path);
    }
    nlohmann::json j;
    f >> j;
    for (auto& [key, val] : j.items()) {
        g_rates[key] = std::stod(val.get<std::string>());
    }
    std::clog << "[currencyservice] loaded " << g_rates.size()
              << " currency rates from " << path << "\n";
}

// ---------------------------------------------------------------------------
// Two-step EUR-pivot conversion algorithm (§3.2, §3.3 of spec).
//
// Intermediate values are IEEE 754 doubles, matching V8's arithmetic.
//
// KEY DIFFERENCE FROM NODE.JS:
//   The original _carry() uses Math.floor() which for negative inputs rounds
//   toward −∞, causing the fractional part to be subtracted twice from units.
//   Here we use std::trunc() which rounds toward zero for both positive and
//   negative values.  For positive amounts trunc == floor, so all existing
//   passing contract tests continue to pass.  For negative amounts the result
//   is mathematically correct (spec §6.5 bug fixed).
//
//   std::fmod() is used throughout to replicate JavaScript's % operator, which
//   also has sign-of-dividend semantics (same as C's fmod).
// ---------------------------------------------------------------------------

struct Intermediate { double units = 0.0, nanos = 0.0; };

static Intermediate Carry(Intermediate m) {
    constexpr double kFS = 1e9;
    m.nanos += std::fmod(m.units, 1.0) * kFS;                  // fractional units → nanos
    m.units  = std::trunc(m.units) + std::trunc(m.nanos / kFS); // carry overflow
    m.nanos  = std::fmod(m.nanos, kFS);                          // keep remainder
    return m;
}

// Throws std::invalid_argument for unknown currency codes.
static Money ConvertMoney(const Money& from, const std::string& to_code) {
    auto it_from = g_rates.find(from.currency_code());
    if (it_from == g_rates.end()) {
        throw std::invalid_argument("unknown source currency: " + from.currency_code());
    }
    auto it_to = g_rates.find(to_code);
    if (it_to == g_rates.end()) {
        throw std::invalid_argument("unknown target currency: " + to_code);
    }
    const double rate_from = it_from->second;
    const double rate_to   = it_to->second;

    // Step 1: source currency → EUR
    Intermediate euros;
    euros.units = static_cast<double>(from.units()) / rate_from;
    euros.nanos = static_cast<double>(from.nanos()) / rate_from;
    euros = Carry(euros);
    euros.nanos = std::round(euros.nanos);  // Math.round after step 1 (§3.3)

    // Step 2: EUR → target currency
    Intermediate result;
    result.units = euros.units * rate_to;
    result.nanos = euros.nanos * rate_to;
    result = Carry(result);

    Money out;
    out.set_units(static_cast<int64_t>(std::trunc(result.units)));
    out.set_nanos(static_cast<int32_t>(std::trunc(result.nanos)));
    out.set_currency_code(to_code);
    return out;
}

// ---------------------------------------------------------------------------
// gRPC service implementations
// ---------------------------------------------------------------------------

class CurrencyServiceImpl final : public CurrencyService::Service {
public:
    Status GetSupportedCurrencies(ServerContext*,
                                   const Empty*,
                                   GetSupportedCurrenciesResponse* resp) override {
        for (const auto& [code, _] : g_rates) {
            resp->add_currency_codes(code);
        }
        return Status::OK;
    }

    Status Convert(ServerContext*,
                   const CurrencyConversionRequest* req,
                   Money* resp) override {
        try {
            *resp = ConvertMoney(req->from(), req->to_code());
            return Status::OK;
        } catch (const std::invalid_argument& e) {
            return Status(StatusCode::INVALID_ARGUMENT, e.what());
        } catch (const std::exception& e) {
            return Status(StatusCode::INTERNAL, e.what());
        }
    }
};

// Health check — always returns SERVING (matches Node.js behaviour, §2.3).
class HealthServiceImpl final : public Health::Service {
public:
    Status Check(ServerContext*,
                 const HealthCheckRequest*,
                 HealthCheckResponse* resp) override {
        resp->set_status(HealthCheckResponse::SERVING);
        return Status::OK;
    }
};

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------

int main() {
    const char* port_env = std::getenv("PORT");
    if (!port_env || port_env[0] == '\0') {
        std::cerr << "[currencyservice] PORT environment variable is not set\n";
        return 1;
    }
    const std::string addr = std::string("[::]:") + port_env;

    // Data file: $CURRENCY_DATA_PATH, else "data/currency_conversion.json"
    // relative to the working directory (matches Node.js behaviour when the
    // fixture runs both servers from the currencyservice source directory).
    std::string data_path = "data/currency_conversion.json";
    if (const char* p = std::getenv("CURRENCY_DATA_PATH")) {
        data_path = p;
    }
    try {
        LoadRates(data_path);
    } catch (const std::exception& e) {
        std::cerr << "[currencyservice] " << e.what() << "\n";
        return 1;
    }

    CurrencyServiceImpl currency_svc;
    HealthServiceImpl   health_svc;

    ServerBuilder builder;
    builder.AddListeningPort(addr, InsecureServerCredentials());
    builder.RegisterService(&currency_svc);
    builder.RegisterService(&health_svc);

    std::unique_ptr<Server> server(builder.BuildAndStart());
    if (!server) {
        std::cerr << "[currencyservice] failed to bind on " << addr << "\n";
        return 1;
    }
    std::clog << "[currencyservice] gRPC server listening on " << addr << "\n";
    server->Wait();
}
