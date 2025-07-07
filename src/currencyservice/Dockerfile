# Use a stable Node.js image
FROM node:18-alpine AS build

# Install python3, make, g++ for node-gyp native module builds
RUN apk add --no-cache python3 make g++

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json and install dependencies
# This leverages Docker's build cache: dependencies are only re-downloaded if package.json changes
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application source code
COPY . .

# Expose the port the service listens on (default for currencyservice is 7000)
EXPOSE 7000

# Define the command to run the service
ENTRYPOINT ["node", "server.js"]
