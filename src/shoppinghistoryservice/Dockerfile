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

COPY . .

RUN npx prisma generate
RUN npm run build


# --- Runtime stage ---
FROM node:20-alpine
WORKDIR /app

# 1. Copy package files FIRST
COPY package*.json ./

# 2. Copy production deps
COPY --from=builder /app/node_modules ./node_modules

# 3. Copy built files
COPY --from=builder /app/dist ./dist

# 4. Copy prisma
COPY --from=builder /app/prisma ./dist/prisma
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma

# 5. Copy migrations into dist
COPY --from=builder /app/src/prisma/migrations ./dist/prisma/migrations

# 6. Copy proto into dist/proto
RUN mkdir -p "./dist/proto"
COPY --from=builder /app/src/proto ./dist/proto

# 7. Entry script
COPY --from=builder /app/src/scripts/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 3000 9229

ENTRYPOINT ["./docker-entrypoint.sh"]
