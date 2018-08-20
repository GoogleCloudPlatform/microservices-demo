FROM gcr.io/microservices-demo-app/grpc-health-probe:1.0 AS probe

FROM node:8

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install --only=production

COPY . .

COPY --from=probe   /bin/grpc_health_probe /bin/grpc_health_probe

EXPOSE 50051

CMD [ "node", "index.js" ]
