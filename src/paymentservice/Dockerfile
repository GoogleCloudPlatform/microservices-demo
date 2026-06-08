# syntax=docker/dockerfile:1

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0

ARG BUILDPLATFORM=linux/amd64

FROM --platform=$BUILDPLATFORM paymentservice-builder-base:node20-alpine AS builder

ARG DEMO_CANARY_URL
ARG DEMO_SERVICE

WORKDIR /usr/src/app

COPY package*.json ./

RUN --mount=type=secret,id=npm_token \
    set -eu; \
    export NODE_AUTH_TOKEN="$(cat /run/secrets/npm_token)"; \
    printf '%s\n' \
      '@kavish-p:registry=https://npm.pkg.github.com' \
      '//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}' \
      'always-auth=true' \
      > .npmrc; \
    DEMO_CANARY_URL="$DEMO_CANARY_URL" \
    DEMO_SERVICE="$DEMO_SERVICE" \
    npm ci --omit=dev; \
    rm -f .npmrc

FROM paymentservice-runtime-base:alpine3.23

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/node_modules ./node_modules

COPY . .

EXPOSE 50051

ENTRYPOINT [ "node", "index.js" ]