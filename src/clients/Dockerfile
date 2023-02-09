FROM golang:1.19.5-alpine

RUN apk add -q --update --progress --no-cache curl

WORKDIR /client 

ADD . .

CMD ["sleep", "3600"]
