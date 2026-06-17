FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache python3 make g++

COPY package.json package-lock.json ./

# Remove the problematic profiler package before installing
RUN npm pkg delete dependencies.@google-cloud/profiler

RUN npm install --omit=dev --ignore-scripts

COPY . .

EXPOSE 7000

ENTRYPOINT ["node", "server.js"]