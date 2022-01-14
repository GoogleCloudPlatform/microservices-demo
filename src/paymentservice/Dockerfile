FROM node:16-alpine as base

FROM base as builder

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install --only=production

FROM base

RUN rm -r /usr/local/lib/node_modules

RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/node_modules ./node_modules

COPY . .

EXPOSE 50051

ENTRYPOINT [ "node", "-r", "./tracing.js", "index.js" ]
