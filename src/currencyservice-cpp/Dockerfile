# Multi-stage build for the C++ currencyservice reimplementation.
#
# Build context must be the src/ directory so both service directories
# are available:
#   docker build -t currencyservice-cpp \
#     -f src/currencyservice-cpp/Dockerfile src/

# ---------------------------------------------------------------------------
# Stage 1: build
# ---------------------------------------------------------------------------
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        pkg-config \
        libgrpc++-dev \
        libprotobuf-dev \
        protobuf-compiler-grpc \
        nlohmann-json3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Proto files come from the Node.js service directory (shared source of truth)
COPY currencyservice/proto/       proto/currencyservice/proto/

# Currency data and C++ sources
COPY currencyservice/data/        data/
COPY currencyservice-cpp/CMakeLists.txt \
     currencyservice-cpp/server.cc \
     ./

RUN cmake -B build -DCMAKE_BUILD_TYPE=Release \
    -DPROTO_SRC_DIR=/build/proto/currencyservice/proto \
    && cmake --build build --parallel "$(nproc)"

# ---------------------------------------------------------------------------
# Stage 2: runtime — minimal image with only what's needed to run
# ---------------------------------------------------------------------------
FROM ubuntu:22.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgrpc++1 \
        libprotobuf23 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /build/build/server   /usr/local/bin/server
COPY --from=builder /build/data/          /app/data/

EXPOSE 7000

ENV PORT=7000

ENTRYPOINT ["/usr/local/bin/server"]
