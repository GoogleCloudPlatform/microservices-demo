FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache python3 make g++

COPY package.json package-lock.json ./

RUN npm pkg delete dependencies.@google-cloud/profiler

RUN npm install --omit=dev --ignore-scripts

COPY . .

EXPOSE 50051

ENTRYPOINT ["node", "server.js"]