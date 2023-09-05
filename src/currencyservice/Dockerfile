FROM node:20.5.0-alpine@sha256:11087abe911baf2fd7e34192f4598bf7e438239e9914f5b7ecda5fb5a7b1a2dd as base

FROM base as builder

# Some packages (e.g. @google-cloud/profiler) require additional
# deps for post-install scripts
RUN apk add --update --no-cache \
    python3 \
    make \
    g++

WORKDIR /usr/src/app

#COPY package*.json ./
COPY . .
RUN npm install --only=production
#debug
ENV NODE_DEBUG=sl

RUN npm i slnodejs

#run comfig
RUN  ./node_modules/.bin/slnodejs config --tokenfile sltoken.txt --appname "currencyservice" --branch "main" --build "0.4"
#sl-scan
RUN ./node_modules/.bin/slnodejs scan --tokenfile sltoken.txt --buildsessionidfile buildSessionId --workspacepath "." --scm none --es6Modules 

FROM base

WORKDIR /usr/src/app
COPY --from=builder /usr/src/app/buildSessionId .

COPY --from=builder /usr/src/app/node_modules ./node_modules

COPY . .

EXPOSE 7000
CMD  ./node_modules/.bin/slnodejs run --token "${SL_TOKEN}" --buildsessionidfile buildSessionId --labid "${SL_LAB_ID}" --workspacepath . server.js
