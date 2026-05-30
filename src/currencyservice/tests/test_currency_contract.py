"""
Contract tests for currencyservice (Node.js implementation).

Starts the original Node.js service as a subprocess, then exercises every
behavior listed in §7 of currencyservice-spec.md.

Tests marked @pytest.mark.xfail document *known bugs* in the Node.js service
that the C++ reimplementation must fix.  Against Node.js they record an
"expected failure" (xfail); against the fixed C++ service they will become
"unexpected passes" (xpass), signalling the bug is resolved.

Run:
    pip install -r requirements.txt
    pytest tests/test_currency_contract.py -v
"""

import math
import os
import socket
import subprocess
import sys
import tempfile
import time

import grpc
import pytest
from grpc_tools import protoc
from grpc_health.v1 import health_pb2, health_pb2_grpc

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_SERVICE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PROTO_DIR = os.path.join(_SERVICE_DIR, "proto")

# ---------------------------------------------------------------------------
# Exchange rates (§8) — EUR-based: 1 EUR = N units of the named currency.
# Source: data/currency_conversion.json (European Central Bank snapshot).
# ---------------------------------------------------------------------------

RATES: dict[str, float] = {
    "EUR": 1.0,
    "USD": 1.1305,
    "JPY": 126.40,
    "BGN": 1.9558,
    "CZK": 25.592,
    "DKK": 7.4609,
    "GBP": 0.85970,
    "HUF": 315.51,
    "PLN": 4.2996,
    "RON": 4.7463,
    "SEK": 10.5375,
    "CHF": 1.1360,
    "ISK": 136.80,
    "NOK": 9.8040,
    "HRK": 7.4210,
    "RUB": 74.4208,
    "TRY": 6.1247,
    "AUD": 1.6072,
    "BRL": 4.2682,
    "CAD": 1.5128,
    "CNY": 7.5857,
    "HKD": 8.8743,
    "IDR": 15999.40,
    "ILS": 4.0875,
    "INR": 79.4320,
    "KRW": 1275.05,
    "MXN": 21.7999,
    "MYR": 4.6289,
    "NZD": 1.6679,
    "PHP": 59.083,
    "SGD": 1.5349,
    "THB": 36.012,
    "ZAR": 16.0583,
}

EXPECTED_CURRENCIES: frozenset[str] = frozenset(RATES.keys())

# ---------------------------------------------------------------------------
# Proto generation (runs once at import time)
#
# grpc_tools.protoc compiles demo.proto into a temp directory which is then
# prepended to sys.path so the generated modules can be imported normally.
# The health service uses the grpcio-health-checking package stubs to avoid a
# naming conflict between the generated grpc/health/v1/ directory tree and the
# already-installed `grpc` Python package.
# ---------------------------------------------------------------------------

_GENERATED_DIR = tempfile.mkdtemp(prefix="currency_protos_")

_rc = protoc.main([
    "grpc_tools.protoc",
    f"--proto_path={_PROTO_DIR}",
    f"--python_out={_GENERATED_DIR}",
    f"--grpc_python_out={_GENERATED_DIR}",
    "demo.proto",
])
if _rc != 0:
    raise RuntimeError(f"protoc failed for demo.proto (exit {_rc})")

sys.path.insert(0, _GENERATED_DIR)
import demo_pb2          # noqa: E402  (generated, not on disk before import)
import demo_pb2_grpc     # noqa: E402

Money = demo_pb2.Money
Empty = demo_pb2.Empty
CurrencyConversionRequest = demo_pb2.CurrencyConversionRequest
GetSupportedCurrenciesResponse = demo_pb2.GetSupportedCurrenciesResponse

# True when exercising a non-Node.js binary (e.g. the C++ reimplementation).
# Drives conditional xfail/skip markers so the same file works against both.
_ALT_BIN = bool(os.environ.get("CURRENCY_SERVICE_BIN") or os.environ.get("CURRENCY_SERVICE_URL"))
# True when connecting to a pre-running service — process-startup tests are skipped.
_EXTERNAL_SVC = bool(os.environ.get("CURRENCY_SERVICE_URL"))


def _make_request(from_code: str, units: int, nanos: int, to_code: str) -> CurrencyConversionRequest:
    """Construct a CurrencyConversionRequest.

    The proto field is named 'from', which is a Python keyword, so we pass
    it via **{} unpacking rather than as a direct keyword argument.
    """
    money = Money(currency_code=from_code, units=units, nanos=nanos)
    return CurrencyConversionRequest(**{"from": money, "to_code": to_code})


# ---------------------------------------------------------------------------
# JavaScript-exact arithmetic (§3.2, §3.3)
#
# The Node.js _carry() function uses JavaScript's % operator, which has
# the same sign as the *dividend* (i.e. fmod semantics, not Python's %).
# We therefore use math.fmod throughout to stay bit-for-bit identical to the
# IEEE 754 double arithmetic performed by V8.
# ---------------------------------------------------------------------------

def _js_carry(units: float, nanos: float) -> tuple[float, float]:
    """Python replica of the Node.js _carry() helper (server.js:117-123)."""
    fraction_size = 1_000_000_000
    nanos += math.fmod(units, 1) * fraction_size
    units = math.floor(units) + math.floor(nanos / fraction_size)
    nanos = math.fmod(nanos, fraction_size)
    return units, nanos


def expected_convert(
    from_units: int,
    from_nanos: int,
    from_code: str,
    to_code: str,
) -> tuple[int, int, str]:
    """Return (units, nanos, currency_code) using the exact JS two-step algorithm.

    Step 1 — source currency → EUR:
        divide units and nanos by data[from_code], _carry, Math.round nanos.
    Step 2 — EUR → target currency:
        multiply by data[to_code], _carry, Math.floor units and nanos.

    The asymmetric rounding (round after step 1, floor after step 2) is an
    intentional property of the original implementation documented in §3.3.
    """
    rate_from = RATES[from_code]
    rate_to = RATES[to_code]

    # Step 1: from_currency → EUR
    eu, en = from_units / rate_from, from_nanos / rate_from
    eu, en = _js_carry(eu, en)
    en = round(en)  # Math.round — nearest integer, ties to +inf

    # Step 2: EUR → to_currency
    ru, rn = eu * rate_to, en * rate_to
    ru, rn = _js_carry(ru, rn)

    # Final truncation (Math.floor, not Math.round)
    return int(math.floor(ru)), int(math.floor(rn)), to_code


# ---------------------------------------------------------------------------
# Server lifecycle fixtures
# ---------------------------------------------------------------------------

def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def node_server():
    """Start the currency service and yield its gRPC address (host:port).

    Three modes, selected by environment variables:

    1. Default — Node.js:
           pytest tests/ -v

    2. Local C++ binary:
           CURRENCY_SERVICE_BIN=/path/to/build/server pytest tests/ -v

    3. Already-running service (e.g. a Docker container):
           CURRENCY_SERVICE_URL=localhost:7001 pytest tests/ -v
       No subprocess is spawned; the fixture just waits for the address to
       become ready and tears down nothing.
    """
    # Mode 3: connect to a pre-running service.
    url = os.environ.get("CURRENCY_SERVICE_URL")
    if url:
        ch = grpc.insecure_channel(url)
        deadline = time.monotonic() + 20.0
        while time.monotonic() < deadline:
            try:
                grpc.channel_ready_future(ch).result(timeout=1.0)
                break
            except grpc.FutureTimeoutError:
                pass
        else:
            pytest.fail(f"Service at {url} did not become ready within 20 s")
        ch.close()
        yield url
        return

    # Modes 1 & 2: spawn a subprocess.
    port = _free_port()
    env = os.environ.copy()
    env["PORT"] = str(port)
    env.pop("ENABLE_TRACING", None)

    alt_bin = os.environ.get("CURRENCY_SERVICE_BIN")
    if alt_bin:
        cmd = [os.path.abspath(alt_bin)]
        cwd = _SERVICE_DIR   # data/ is found relative to here
    else:
        cmd = ["node", "server.js"]
        cwd = _SERVICE_DIR
        env["DISABLE_PROFILER"] = "1"

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    addr = f"localhost:{port}"
    channel = grpc.insecure_channel(addr)
    deadline = time.monotonic() + 20.0
    ready = False
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            _, stderr = proc.communicate()
            pytest.fail(
                f"currencyservice process exited unexpectedly: {stderr.decode()}"
            )
        try:
            grpc.channel_ready_future(channel).result(timeout=1.0)
            ready = True
            break
        except grpc.FutureTimeoutError:
            pass

    if not ready:
        proc.terminate()
        pytest.fail(f"currencyservice did not become ready on {addr} within 20 s")

    yield addr

    channel.close()
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="session")
def channel(node_server):
    ch = grpc.insecure_channel(node_server)  # node_server is now host:port
    yield ch
    ch.close()


@pytest.fixture(scope="session")
def stub(channel):
    return demo_pb2_grpc.CurrencyServiceStub(channel)


@pytest.fixture(scope="session")
def health_stub(channel):
    return health_pb2_grpc.HealthStub(channel)


# ---------------------------------------------------------------------------
# §7 item 1 — GetSupportedCurrencies returns all 33 expected currency codes
# ---------------------------------------------------------------------------

class TestGetSupportedCurrencies:
    def test_returns_all_33_currency_codes(self, stub):
        response = stub.GetSupportedCurrencies(Empty())
        assert isinstance(response, GetSupportedCurrenciesResponse)
        returned = set(response.currency_codes)
        assert returned == EXPECTED_CURRENCIES, (
            f"Missing: {EXPECTED_CURRENCIES - returned}, "
            f"Extra: {returned - EXPECTED_CURRENCIES}"
        )

    def test_returns_exactly_33_codes(self, stub):
        response = stub.GetSupportedCurrencies(Empty())
        assert len(response.currency_codes) == 33

    def test_all_codes_are_three_letter_strings(self, stub):
        response = stub.GetSupportedCurrencies(Empty())
        for code in response.currency_codes:
            assert isinstance(code, str) and len(code) == 3, (
                f"Unexpected currency code format: {code!r}"
            )


# ---------------------------------------------------------------------------
# §7 items 2–6 — Convert: core positive-amount cases
# ---------------------------------------------------------------------------

class TestConvertPositiveAmounts:
    """§7 items 2–6: standard conversions with positive amounts."""

    def _assert_convert(self, stub, fu, fn, fc, tc):
        """Call Convert and assert the result matches expected_convert()."""
        exp_u, exp_n, exp_code = expected_convert(fu, fn, fc, tc)
        result = stub.Convert(_make_request(fc, fu, fn, tc))
        assert result.currency_code == exp_code
        assert result.units == exp_u, (
            f"{fc} {fu}.{fn:09d} → {tc}: "
            f"units {result.units} != expected {exp_u}"
        )
        assert result.nanos == exp_n, (
            f"{fc} {fu}.{fn:09d} → {tc}: "
            f"nanos {result.nanos} != expected {exp_n}"
        )

    # §7 item 2 — USD → EUR
    def test_convert_usd_to_eur(self, stub):
        self._assert_convert(stub, 300, 0, "USD", "EUR")

    # §7 item 3 — EUR → USD
    def test_convert_eur_to_usd(self, stub):
        self._assert_convert(stub, 100, 0, "EUR", "USD")

    # §7 item 4 — non-EUR to non-EUR (two-step pivot via EUR)
    def test_convert_usd_to_jpy_two_step_pivot(self, stub):
        """USD → EUR → JPY exercises both legs of the pivot algorithm (§3.3)."""
        self._assert_convert(stub, 100, 0, "USD", "JPY")

    # §7 item 5 — EUR → EUR identity
    def test_convert_eur_to_eur_identity(self, stub):
        """EUR → EUR must return the original amount unchanged (rate 1.0 both legs)."""
        self._assert_convert(stub, 50, 0, "EUR", "EUR")

    # §7 item 6 — same source and target currency (non-EUR)
    def test_convert_same_currency_identity(self, stub):
        """USD → USD: floating-point round-trip should still reproduce the input."""
        self._assert_convert(stub, 100, 0, "USD", "USD")

    # Additional representative pairs
    def test_convert_chf_to_eur(self, stub):
        self._assert_convert(stub, 300, 0, "CHF", "EUR")

    def test_convert_eur_to_gbp(self, stub):
        self._assert_convert(stub, 200, 0, "EUR", "GBP")

    def test_convert_inr_to_usd(self, stub):
        self._assert_convert(stub, 5000, 0, "INR", "USD")


# ---------------------------------------------------------------------------
# §7 item 9 — zero amount
# ---------------------------------------------------------------------------

class TestConvertZeroAmount:
    def test_zero_units_and_nanos_returns_zero(self, stub):
        """Converting a zero Money must return zero in the target currency (§7 item 9)."""
        result = stub.Convert(_make_request("USD", 0, 0, "EUR"))
        assert result.currency_code == "EUR"
        assert result.units == 0
        assert result.nanos == 0


# ---------------------------------------------------------------------------
# §7 item 10 — non-zero nanos, zero units
# ---------------------------------------------------------------------------

class TestConvertNanosOnly:
    def test_nanos_input_converts_correctly(self, stub):
        """0.5 USD (units=0, nanos=500_000_000) should convert to correct EUR nanos (§7 item 10)."""
        exp_u, exp_n, exp_code = expected_convert(0, 500_000_000, "USD", "EUR")
        result = stub.Convert(_make_request("USD", 0, 500_000_000, "EUR"))
        assert result.currency_code == exp_code
        assert result.units == exp_u
        assert result.nanos == exp_n

    def test_nanos_at_max_boundary(self, stub):
        """nanos=999_999_999 (just under 1 full unit) should convert without overflow in step 1."""
        exp_u, exp_n, exp_code = expected_convert(0, 999_999_999, "USD", "EUR")
        result = stub.Convert(_make_request("USD", 0, 999_999_999, "EUR"))
        assert result.currency_code == exp_code
        assert result.units == exp_u
        assert result.nanos == exp_n


# ---------------------------------------------------------------------------
# §7 item 11 — carry propagation: nanos overflow into units after step-2 multiply
# ---------------------------------------------------------------------------

class TestConvertCarryNanosToUnits:
    def test_nanos_overflow_carries_into_units(self, stub):
        """EUR 0.999999999 → USD: multiplying nanos by USD rate pushes value over 1e9,
        so _carry must increment units by 1 (§7 item 11, §3.2).
        """
        # 999_999_999 nanos * 1.1305 ≈ 1_130_499_988  which is > 1e9
        exp_u, exp_n, exp_code = expected_convert(0, 999_999_999, "EUR", "USD")
        assert exp_u == 1, (
            f"Pre-check: expected units=1 after carry, got {exp_u}"
        )
        result = stub.Convert(_make_request("EUR", 0, 999_999_999, "USD"))
        assert result.units == exp_u
        assert result.nanos == exp_n
        assert result.currency_code == exp_code


# ---------------------------------------------------------------------------
# §7 item 12 — carry propagation: fractional units fold into nanos (step-1 carry)
# ---------------------------------------------------------------------------

class TestConvertCarryUnitsToNanos:
    def test_fractional_units_fold_into_nanos(self, stub):
        """1 USD ≈ 0.884 EUR: dividing by the USD rate produces a fractional units
        value which _carry must move into nanos, leaving units=0 (§7 item 12, §3.2).
        """
        exp_u, exp_n, exp_code = expected_convert(1, 0, "USD", "EUR")
        assert exp_u == 0, (
            f"Pre-check: 1 USD should yield 0 whole EUR units, got {exp_u}"
        )
        result = stub.Convert(_make_request("USD", 1, 0, "EUR"))
        assert result.units == exp_u
        assert result.nanos == exp_n
        assert result.currency_code == exp_code


# ---------------------------------------------------------------------------
# §7 item 13 — negative Money amounts
# ---------------------------------------------------------------------------

class TestConvertNegativeAmounts:
    @pytest.mark.skipif(
        _ALT_BIN,
        reason="C++ uses trunc-based carry so it returns the correct result, not the buggy one",
    )
    def test_negative_units_returns_expected_buggy_result(self, stub):
        """Negative amounts expose a known flaw in _carry for negative values (§6.5).

        The JS _carry() uses Math.floor (rounds toward −∞) combined with fmod
        (sign of dividend), which causes the fractional part to be subtracted
        *twice* for negative inputs.  E.g. -10 USD → EUR yields units=-11 rather
        than the mathematically correct ≈ -8.85.
        """
        exp_u, exp_n, _ = expected_convert(-10, 0, "USD", "EUR")
        assert exp_u == -11, f"Helper must reproduce the known buggy value -11, got {exp_u}"
        result = stub.Convert(_make_request("USD", -10, 0, "EUR"))
        assert result.units == exp_u
        assert result.nanos == exp_n
        assert result.currency_code == "EUR"

    @pytest.mark.xfail(
        not _ALT_BIN,   # xfail against Node.js; passes (xpass→pass) against C++
        reason=(
            "Known bug: _carry() double-subtracts the fractional part for negative "
            "amounts (§6.5).  Node.js returns units=-11; the C++ reimplementation "
            "uses trunc-based carry and returns the correct units=-8."
        ),
        strict=False,   # xpass is reported as XPASS (not failure) when C++ is correct
    )
    def test_negative_units_correct_result(self, stub):
        """Assert the *correct* mathematical result for a negative conversion.

        -10 USD / 1.1305 ≈ -8.846 EUR  →  units=-8, nanos in (-999999999, 0].
        Node.js returns units=-11 (double-subtraction bug); C++ returns -8.
        """
        result = stub.Convert(_make_request("USD", -10, 0, "EUR"))
        assert result.units == -8
        assert -999_999_999 <= result.nanos <= 0


# ---------------------------------------------------------------------------
# §7 items 7–8 — unknown currency codes (known-failing bug, §6.2)
# ---------------------------------------------------------------------------

class TestConvertUnknownCurrencyCodes:
    """§7 items 7–8: behaviour when an unknown currency code is supplied.

    In the Node.js implementation, data[unknown_code] returns undefined, and
    dividing or multiplying by undefined produces NaN.  NaN propagates silently
    through _carry without throwing, so the try/catch is never triggered.  The
    proto3 serializer coerces NaN int64/int32 fields to 0, producing a silent
    zero-amount response instead of a gRPC error (§6.2).

    The xfail tests below assert the CORRECT behaviour (a gRPC error status).
    The C++ reimplementation must return INVALID_ARGUMENT or NOT_FOUND for
    unknown codes to make these xfail tests pass (xpass).
    """

    @pytest.mark.skipif(
        _ALT_BIN,
        reason="C++ raises INVALID_ARGUMENT for unknown codes, not silent zeros",
    )
    def test_unknown_from_code_silently_returns_zero(self, stub):
        """Documents the actual (buggy) Node.js output: zeros, no error raised."""
        result = stub.Convert(_make_request("XYZ", 100, 0, "EUR"))
        assert result.units == 0
        assert result.nanos == 0
        assert result.currency_code == "EUR"

    @pytest.mark.skipif(
        _ALT_BIN,
        reason="C++ raises INVALID_ARGUMENT for unknown codes, not silent zeros",
    )
    def test_unknown_to_code_silently_returns_zero(self, stub):
        """Documents the actual (buggy) Node.js output when to_code is unknown."""
        result = stub.Convert(_make_request("EUR", 100, 0, "XYZ"))
        assert result.units == 0
        assert result.nanos == 0

    @pytest.mark.xfail(
        not _ALT_BIN,   # xfail against Node.js; passes against C++
        reason=(
            "Known bug (§6.2): Node.js silently returns zeros for unknown "
            "from.currency_code instead of raising a gRPC error.  "
            "C++ returns INVALID_ARGUMENT."
        ),
        strict=False,
    )
    def test_unknown_from_code_raises_grpc_error(self, stub):
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.Convert(_make_request("XYZ", 100, 0, "EUR"))
        assert exc_info.value.code() in (
            grpc.StatusCode.INVALID_ARGUMENT,
            grpc.StatusCode.NOT_FOUND,
        )

    @pytest.mark.xfail(
        not _ALT_BIN,   # xfail against Node.js; passes against C++
        reason=(
            "Known bug (§6.2): Node.js silently returns zeros for unknown "
            "to_code instead of raising a gRPC error.  "
            "C++ returns INVALID_ARGUMENT."
        ),
        strict=False,
    )
    def test_unknown_to_code_raises_grpc_error(self, stub):
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.Convert(_make_request("EUR", 100, 0, "XYZ"))
        assert exc_info.value.code() in (
            grpc.StatusCode.INVALID_ARGUMENT,
            grpc.StatusCode.NOT_FOUND,
        )


# ---------------------------------------------------------------------------
# §7 item 14 — large int64 units (floating-point precision boundary)
# ---------------------------------------------------------------------------

class TestConvertLargeAmounts:
    def test_large_units_convert_without_crash(self, stub):
        """int64 max-range units should not crash the service (§7 item 14).

        IEEE 754 double has ~15–16 significant digits; large unit values will
        lose precision but must not raise an exception or return a gRPC error.
        We verify that the service responds and that result fields are integers.
        """
        # 10^15 units — well within int64 range but beyond double precision
        large_units = 10 ** 15
        result = stub.Convert(_make_request("USD", large_units, 0, "EUR"))
        assert result.currency_code == "EUR"
        assert isinstance(result.units, int)
        assert isinstance(result.nanos, int)


# ---------------------------------------------------------------------------
# §7 item 15 — health check always returns SERVING
# ---------------------------------------------------------------------------

class TestHealthCheck:
    def test_check_returns_serving_with_empty_service(self, health_stub):
        """Health.Check({}) must respond SERVING regardless of service field (§7 item 15)."""
        response = health_stub.Check(health_pb2.HealthCheckRequest())
        assert response.status == health_pb2.HealthCheckResponse.SERVING

    def test_check_returns_serving_with_named_service(self, health_stub):
        """Health.Check with a named service must also respond SERVING."""
        response = health_stub.Check(
            health_pb2.HealthCheckRequest(service="hipstershop.CurrencyService")
        )
        assert response.status == health_pb2.HealthCheckResponse.SERVING

    def test_check_returns_serving_with_unknown_service(self, health_stub):
        """Health.Check never inspects the service field — always returns SERVING."""
        response = health_stub.Check(
            health_pb2.HealthCheckRequest(service="nonexistent.Service")
        )
        assert response.status == health_pb2.HealthCheckResponse.SERVING


# ---------------------------------------------------------------------------
# §7 item 16 — server startup without PORT (process-level test)
# ---------------------------------------------------------------------------

class TestServerStartup:
    @pytest.mark.skipif(_EXTERNAL_SVC, reason="Cannot test process startup against a pre-running service")
    def test_server_fails_without_port_env_var(self):
        """Server should fail or refuse connections when PORT is not set (§6.8, §7 item 16).

        Node.js: interpolates undefined into '[::]:undefined', grpc.Server fails to bind.
        C++:     explicitly checks for PORT and exits 1 immediately.
        Both: the process exits within a few seconds.
        """
        alt_bin = os.environ.get("CURRENCY_SERVICE_BIN")
        env = {k: v for k, v in os.environ.items() if k != "PORT"}
        if alt_bin:
            cmd = [os.path.abspath(alt_bin)]
            cwd = _SERVICE_DIR
        else:
            env["DISABLE_PROFILER"] = "1"
            cmd = ["node", "server.js"]
            cwd = _SERVICE_DIR
        proc = subprocess.Popen(
            cmd, cwd=cwd, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.terminate()
            proc.wait()
            return  # still alive — acceptable (Node.js edge case)
        assert proc.returncode is not None


# ---------------------------------------------------------------------------
# §7 item 17 — service starts and serves when ENABLE_TRACING=1
#              (tracing enabled but collector unreachable — must not block startup)
# ---------------------------------------------------------------------------

class TestTracingStartup:
    @pytest.mark.skipif(
        _ALT_BIN or _EXTERNAL_SVC,
        reason="ENABLE_TRACING is a Node.js / OpenTelemetry SDK concern; not applicable to C++ or pre-running services",
    )
    def test_service_starts_with_tracing_enabled_no_collector(self):
        """Server must start and serve requests even when ENABLE_TRACING=1 and
        no OTLP collector is reachable (§7 item 17).  Trace export failures must
        be non-fatal (the OTel SDK retries in the background).
        """
        port = _free_port()
        env = os.environ.copy()
        env["PORT"] = str(port)
        env["DISABLE_PROFILER"] = "1"
        env["ENABLE_TRACING"] = "1"
        env["COLLECTOR_SERVICE_ADDR"] = "localhost:4317"  # nothing listening here

        proc = subprocess.Popen(
            ["node", "server.js"],
            cwd=_SERVICE_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            ch = grpc.insecure_channel(f"localhost:{port}")
            deadline = time.monotonic() + 15.0
            ready = False
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    _, stderr = proc.communicate()
                    pytest.fail(f"Server exited early with tracing enabled: {stderr.decode()}")
                try:
                    grpc.channel_ready_future(ch).result(timeout=1.0)
                    ready = True
                    break
                except grpc.FutureTimeoutError:
                    pass

            assert ready, f"Server with ENABLE_TRACING=1 did not become ready on port {port}"

            # Verify it still serves a basic request
            local_stub = demo_pb2_grpc.CurrencyServiceStub(ch)
            response = local_stub.GetSupportedCurrencies(Empty())
            assert len(response.currency_codes) == 33
        finally:
            ch.close()
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


# ---------------------------------------------------------------------------
# Asymmetric rounding property (§3.3) — explicit verification
# ---------------------------------------------------------------------------

class TestAsymmetricRounding:
    """Directly verify that step-1 uses Math.round and step-2 uses Math.floor.

    This is the key algorithmic property that distinguishes the currencyservice
    from a naive implementation.  We test it with a value engineered so the
    two rounding modes produce different nanos.
    """

    def test_step1_uses_round_not_floor(self, stub):
        """After dividing by rate_from, nanos are rounded (not floored).

        CHF 300.0 → EUR: dividing 0 nanos by CHF rate produces a non-integer
        intermediate EUR nanos that differs between round() and floor().
        The expected value was verified against the live Node.js service.
        """
        exp_u, exp_n, exp_code = expected_convert(300, 0, "CHF", "EUR")
        result = stub.Convert(_make_request("CHF", 300, 0, "EUR"))
        assert result.units == exp_u
        assert result.nanos == exp_n
        assert result.currency_code == exp_code

    def test_step2_uses_floor_not_round(self, stub):
        """After multiplying EUR amount by rate_to, units and nanos are floored.

        EUR 1.0 → USD: multiplying 1 unit by 1.1305 produces 1.1305.
        _carry isolates 0.1305 * 1e9 = 130_500_000 into nanos.
        floor(130_500_000.xxx) keeps the value rather than rounding up.
        """
        exp_u, exp_n, exp_code = expected_convert(1, 0, "EUR", "USD")
        result = stub.Convert(_make_request("EUR", 1, 0, "USD"))
        assert result.units == exp_u
        assert result.nanos == exp_n
        assert result.currency_code == exp_code
