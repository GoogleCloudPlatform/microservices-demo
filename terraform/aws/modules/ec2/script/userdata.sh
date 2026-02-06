#!/bin/bash
set -euo pipefail

# Install Docker
yum update -y
yum install -y docker
systemctl enable docker
systemctl start docker

# Install docker-compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create working directory
mkdir -p /opt/online-boutique
cd /opt/online-boutique

# Generate docker-compose.yml with all microservices
# Services communicate via the compose internal network using container ports.
# Only the frontend is exposed on the host (port 80) for ALB access.
cat > docker-compose.yml <<'EOF'
version: "3.9"

services:
  redis-cart:
    image: redis:alpine
    restart: always

  adservice:
    image: gcr.io/google-samples/microservices-demo/adservice:v0.9.0
    environment:
      - PORT=9555
    restart: always

  cartservice:
    image: gcr.io/google-samples/microservices-demo/cartservice:v0.9.0
    environment:
      - REDIS_ADDR=redis-cart:6379
    depends_on:
      - redis-cart
    restart: always

  checkoutservice:
    image: gcr.io/google-samples/microservices-demo/checkoutservice:v0.9.0
    environment:
      - PORT=5050
      - PRODUCT_CATALOG_SERVICE_ADDR=productcatalogservice:3550
      - SHIPPING_SERVICE_ADDR=shippingservice:50051
      - PAYMENT_SERVICE_ADDR=paymentservice:50051
      - EMAIL_SERVICE_ADDR=emailservice:8080
      - CURRENCY_SERVICE_ADDR=currencyservice:7000
      - CART_SERVICE_ADDR=cartservice:7070
    depends_on:
      - productcatalogservice
      - shippingservice
      - paymentservice
      - emailservice
      - currencyservice
      - cartservice
    restart: always

  currencyservice:
    image: gcr.io/google-samples/microservices-demo/currencyservice:v0.9.0
    environment:
      - PORT=7000
      - DISABLE_PROFILER=1
    restart: always

  emailservice:
    image: gcr.io/google-samples/microservices-demo/emailservice:v0.9.0
    environment:
      - PORT=8080
      - DISABLE_PROFILER=1
    restart: always

  frontend:
    image: gcr.io/google-samples/microservices-demo/frontend:v0.9.0
    environment:
      - PORT=8080
      - PRODUCT_CATALOG_SERVICE_ADDR=productcatalogservice:3550
      - CURRENCY_SERVICE_ADDR=currencyservice:7000
      - CART_SERVICE_ADDR=cartservice:7070
      - RECOMMENDATION_SERVICE_ADDR=recommendationservice:8080
      - SHIPPING_SERVICE_ADDR=shippingservice:50051
      - CHECKOUT_SERVICE_ADDR=checkoutservice:5050
      - AD_SERVICE_ADDR=adservice:9555
      - ENABLE_PROFILER=0
    ports:
      - "80:8080"
    depends_on:
      - productcatalogservice
      - currencyservice
      - cartservice
      - recommendationservice
      - shippingservice
      - checkoutservice
      - adservice
    restart: always

  paymentservice:
    image: gcr.io/google-samples/microservices-demo/paymentservice:v0.9.0
    environment:
      - PORT=50051
      - DISABLE_PROFILER=1
    restart: always

  productcatalogservice:
    image: gcr.io/google-samples/microservices-demo/productcatalogservice:v0.9.0
    environment:
      - PORT=3550
      - DISABLE_PROFILER=1
    restart: always

  recommendationservice:
    image: gcr.io/google-samples/microservices-demo/recommendationservice:v0.9.0
    environment:
      - PORT=8080
      - PRODUCT_CATALOG_SERVICE_ADDR=productcatalogservice:3550
      - DISABLE_PROFILER=1
    depends_on:
      - productcatalogservice
    restart: always

  shippingservice:
    image: gcr.io/google-samples/microservices-demo/shippingservice:v0.9.0
    environment:
      - PORT=50051
      - DISABLE_PROFILER=1
    restart: always
EOF

# Pull images and start all services
/usr/local/bin/docker-compose up -d
