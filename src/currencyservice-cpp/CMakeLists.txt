cmake_minimum_required(VERSION 3.16)
project(currencyservice CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---------------------------------------------------------------------------
# Dependencies
#
# macOS (Homebrew):
#   brew install grpc protobuf nlohmann-json
#   cmake -B build -DCMAKE_PREFIX_PATH=$(brew --prefix)
#
# Ubuntu / Debian (apt):
#   apt-get install -y libgrpc++-dev libprotobuf-dev \
#                      protobuf-compiler-grpc nlohmann-json3-dev
#   cmake -B build
#
# gRPC: try CMake CONFIG mode first (Homebrew / vcpkg install the cmake
# config files in a standard search path).  On Debian/Ubuntu the config
# files live in /usr/lib/<multiarch>/cmake/grpc/, which is NOT on CMake's
# default search path, so we fall back to pkg-config there.
# ---------------------------------------------------------------------------

find_package(gRPC CONFIG QUIET)
if(gRPC_FOUND)
    message(STATUS "gRPC ${gRPC_VERSION} found via CMake config")
    set(GRPC_LINK_TARGET gRPC::grpc++)
    get_target_property(GRPC_CPP_PLUGIN gRPC::grpc_cpp_plugin LOCATION)
else()
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(GRPCPP REQUIRED IMPORTED_TARGET grpc++)
    message(STATUS "gRPC ${GRPCPP_VERSION} found via pkg-config")
    set(GRPC_LINK_TARGET PkgConfig::GRPCPP)
    find_program(GRPC_CPP_PLUGIN grpc_cpp_plugin REQUIRED)
endif()

# Protobuf
find_package(Protobuf REQUIRED)
if(NOT Protobuf_PROTOC_EXECUTABLE)
    find_program(Protobuf_PROTOC_EXECUTABLE protoc REQUIRED)
endif()
message(STATUS "protoc: ${Protobuf_PROTOC_EXECUTABLE}")
message(STATUS "grpc_cpp_plugin: ${GRPC_CPP_PLUGIN}")

# nlohmann_json — header-only; both Homebrew and apt provide the cmake config
find_package(nlohmann_json REQUIRED)

# ---------------------------------------------------------------------------
# Proto code generation
# ---------------------------------------------------------------------------

# Can be overridden at configure time:
#   cmake -DPROTO_SRC_DIR=/absolute/path/to/proto ...
if(NOT DEFINED PROTO_SRC_DIR)
    set(PROTO_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../currencyservice/proto")
endif()
message(STATUS "Proto source dir: ${PROTO_SRC_DIR}")
set(PROTO_GEN_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")

file(MAKE_DIRECTORY
    "${PROTO_GEN_DIR}"
    "${PROTO_GEN_DIR}/grpc/health/v1"
)

add_custom_command(
    OUTPUT
        "${PROTO_GEN_DIR}/demo.pb.cc"
        "${PROTO_GEN_DIR}/demo.pb.h"
        "${PROTO_GEN_DIR}/demo.grpc.pb.cc"
        "${PROTO_GEN_DIR}/demo.grpc.pb.h"
    COMMAND "${Protobuf_PROTOC_EXECUTABLE}"
        "--proto_path=${PROTO_SRC_DIR}"
        "--cpp_out=${PROTO_GEN_DIR}"
        "--grpc_out=${PROTO_GEN_DIR}"
        "--plugin=protoc-gen-grpc=${GRPC_CPP_PLUGIN}"
        "demo.proto"
    DEPENDS "${PROTO_SRC_DIR}/demo.proto"
    COMMENT "Generating C++ stubs for demo.proto"
    VERBATIM
)

add_custom_command(
    OUTPUT
        "${PROTO_GEN_DIR}/grpc/health/v1/health.pb.cc"
        "${PROTO_GEN_DIR}/grpc/health/v1/health.pb.h"
        "${PROTO_GEN_DIR}/grpc/health/v1/health.grpc.pb.cc"
        "${PROTO_GEN_DIR}/grpc/health/v1/health.grpc.pb.h"
    COMMAND "${Protobuf_PROTOC_EXECUTABLE}"
        "--proto_path=${PROTO_SRC_DIR}"
        "--cpp_out=${PROTO_GEN_DIR}"
        "--grpc_out=${PROTO_GEN_DIR}"
        "--plugin=protoc-gen-grpc=${GRPC_CPP_PLUGIN}"
        "grpc/health/v1/health.proto"
    DEPENDS "${PROTO_SRC_DIR}/grpc/health/v1/health.proto"
    COMMENT "Generating C++ stubs for health.proto"
    VERBATIM
)

# ---------------------------------------------------------------------------
# Server binary
# ---------------------------------------------------------------------------

add_executable(server
    server.cc
    "${PROTO_GEN_DIR}/demo.pb.cc"
    "${PROTO_GEN_DIR}/demo.grpc.pb.cc"
    "${PROTO_GEN_DIR}/grpc/health/v1/health.pb.cc"
    "${PROTO_GEN_DIR}/grpc/health/v1/health.grpc.pb.cc"
)

target_include_directories(server PRIVATE "${PROTO_GEN_DIR}")

target_link_libraries(server PRIVATE
    ${GRPC_LINK_TARGET}
    protobuf::libprotobuf
    nlohmann_json::nlohmann_json
)
