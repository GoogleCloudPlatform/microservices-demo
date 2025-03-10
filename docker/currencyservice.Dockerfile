#Base image

FROM node:20.17.0-alpine@sha256:2d07db07a2df6830718ae2a47db6fedce6745f5bcd174c398f2acdda90a11c03 AS builder

# set the working directory in the container
WORKDIR /app

ENV NODE_ENV=production

# copy the package.json 
COPY src/currencyservice/package*.json ./

# we need to install python3, g++ and make to build the dependencies
RUN apk add --update --no-cache \
    python3 \
    make \
    g++

RUN npm install --only=production

FROM alpine:3.20.3@sha256:beefdbd8a1da6d2915566fde36db9db0b524eb737fc57cd1367effd16dc0d06d

WORKDIR /app

RUN apk add --no-cache nodejs

COPY --from=builder /app/node_modules ./node_modules

COPY src/currencyservice/ .

EXPOSE 7000

ENTRYPOINT [ "node", "server.js" ]


