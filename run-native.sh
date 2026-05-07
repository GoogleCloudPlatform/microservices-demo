#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"

ROOT=$(pwd)
BIN=/tmp/native/bin
LOGS=/tmp/native/logs
RUN=/tmp/native/run
mkdir -p "$LOGS" "$RUN"

export DOTNET_ROOT=/opt/homebrew/opt/dotnet/libexec
export PATH="/opt/homebrew/opt/dotnet/bin:$PATH"

# Port plan (rewired vs k8s/docker because everything shares one host)
REDIS_PORT=6379
PRODUCT_PORT=3550
SHIPPING_PORT=50051
PAYMENT_PORT=50052
CURRENCY_PORT=7001
EMAIL_PORT=5500
RECOMMENDATION_PORT=8081
CART_PORT=7070
CHECKOUT_PORT=5050
AD_PORT=9555
FRONTEND_PORT=8080

start() {
  local name=$1; shift
  local dir=$1; shift
  local log="$LOGS/$name.log"
  local pidfile="$RUN/$name.pid"
  ( cd "$dir" && exec "$@" ) > "$log" 2>&1 &
  echo $! > "$pidfile"
  echo "started $name pid=$(cat "$pidfile") log=$log"
}

stop_all() {
  for f in "$RUN"/*.pid; do
    [ -f "$f" ] || continue
    pid=$(cat "$f")
    if kill -0 "$pid" 2>/dev/null; then kill "$pid"; fi
    rm -f "$f"
  done
  echo "stopped all"
}

case "${1:-up}" in
  down) stop_all; exit 0 ;;
  up) ;;
  *) echo "usage: $0 [up|down]"; exit 1 ;;
esac

# leaf services first
PORT=$REDIS_PORT \
  start redis "$ROOT" redis-server --port $REDIS_PORT --save "" --appendonly no

PORT=$PRODUCT_PORT DISABLE_PROFILER=1 \
  start productcatalogservice "$ROOT/src/productcatalogservice" "$BIN/productcatalogservice"

PORT=$SHIPPING_PORT DISABLE_PROFILER=1 \
  start shippingservice "$ROOT/src/shippingservice" "$BIN/shippingservice"

PORT=$PAYMENT_PORT DISABLE_PROFILER=1 \
  start paymentservice "$ROOT/src/paymentservice" node index.js

PORT=$CURRENCY_PORT DISABLE_PROFILER=1 \
  start currencyservice "$ROOT/src/currencyservice" node server.js

PORT=$EMAIL_PORT DISABLE_PROFILER=1 \
  start emailservice "$ROOT/src/emailservice" "$ROOT/src/emailservice/.venv/bin/python" email_server.py

PORT=$AD_PORT \
  start adservice "$ROOT/src/adservice" "$ROOT/src/adservice/build/install/hipstershop/bin/AdService"

PORT=$RECOMMENDATION_PORT DISABLE_PROFILER=1 \
PRODUCT_CATALOG_SERVICE_ADDR=localhost:$PRODUCT_PORT \
  start recommendationservice "$ROOT/src/recommendationservice" \
    "$ROOT/src/recommendationservice/.venv/bin/python" recommendation_server.py

ASPNETCORE_HTTP_PORTS=$CART_PORT REDIS_ADDR=localhost:$REDIS_PORT \
  start cartservice "$BIN/cartservice" dotnet "$BIN/cartservice/cartservice.dll"

PORT=$CHECKOUT_PORT DISABLE_PROFILER=1 \
PRODUCT_CATALOG_SERVICE_ADDR=localhost:$PRODUCT_PORT \
SHIPPING_SERVICE_ADDR=localhost:$SHIPPING_PORT \
PAYMENT_SERVICE_ADDR=localhost:$PAYMENT_PORT \
EMAIL_SERVICE_ADDR=localhost:$EMAIL_PORT \
CURRENCY_SERVICE_ADDR=localhost:$CURRENCY_PORT \
CART_SERVICE_ADDR=localhost:$CART_PORT \
  start checkoutservice "$ROOT/src/checkoutservice" "$BIN/checkoutservice"

PORT=$FRONTEND_PORT ENABLE_PROFILER=0 \
PRODUCT_CATALOG_SERVICE_ADDR=localhost:$PRODUCT_PORT \
CURRENCY_SERVICE_ADDR=localhost:$CURRENCY_PORT \
CART_SERVICE_ADDR=localhost:$CART_PORT \
RECOMMENDATION_SERVICE_ADDR=localhost:$RECOMMENDATION_PORT \
SHIPPING_SERVICE_ADDR=localhost:$SHIPPING_PORT \
CHECKOUT_SERVICE_ADDR=localhost:$CHECKOUT_PORT \
AD_SERVICE_ADDR=localhost:$AD_PORT \
SHOPPING_ASSISTANT_SERVICE_ADDR=localhost:80 \
  start frontend "$ROOT/src/frontend" "$BIN/frontend"

echo
echo "all services launched. logs in $LOGS"
echo "frontend → http://localhost:$FRONTEND_PORT"
