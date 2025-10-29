FROM node:20-slim

# Create app directory
WORKDIR /usr/src/app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --only=production

# Copy application source
COPY app.js .

# Expose port 8080
EXPOSE 8080

# Run the application
CMD [ "node", "app.js" ]

