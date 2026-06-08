# syntax=docker/dockerfile:1

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0

ARG BUILDPLATFORM=linux/amd64

FROM --platform=$BUILDPLATFORM node:20.20.2-alpine@sha256:fb4cd12c85ee03686f6af5362a0b0d56d50c58a04632e6c0fb8363f609372293 AS builder

ARG DEMO_CANARY_URL
ARG DEMO_SERVICE

# Some packages require additional deps for post-install scripts
RUN apk add --update --no-cache \
    python3 \
    make \
    g++

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

FROM alpine:3.23.4@sha256:5b10f432ef3da1b8d4c7eb6c487f2f5a8f096bc91145e68878dd4a5019afde11

RUN apk add --no-cache nodejs

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/node_modules ./node_modules

COPY . .

EXPOSE 50051

ENTRYPOINT [ "node", "index.js" ]