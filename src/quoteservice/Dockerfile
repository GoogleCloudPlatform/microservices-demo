FROM node:8-alpine as base
FROM base as builder

WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install --only=production

FROM base

WORKDIR /usr/src/app
COPY --from=builder /usr/src/app/node_modules ./node_modules
COPY . .

EXPOSE 3000
ENTRYPOINT [ "node", "index.js" ]
