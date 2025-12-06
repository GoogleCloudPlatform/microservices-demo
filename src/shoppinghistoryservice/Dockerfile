# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# --- Build stage ---
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

# Copy the source code
COPY . .

# Generate Prisma client BEFORE building TS
RUN npx prisma generate

# Build TS -> JS
RUN npm run build

# --- Runtime stage ---
FROM node:20-alpine

WORKDIR /app

# Copy only prod dependencies
COPY --from=builder /app/node_modules ./node_modules

# Copy compiled JS
COPY --from=builder /app/dist ./dist


# Copy prisma schema + runtime engines
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=builder /app/src/prisma/migrations ./dist/prisma/migrations

# Copy package files
COPY package*.json ./

EXPOSE $PORT

CMD ["node", "--inspect=0.0.0.0:9229", "dist/index.js"]
