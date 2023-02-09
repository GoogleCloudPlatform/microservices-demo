FROM alpine:3.15

RUN apk update && apk --no-cache add dnsmasq

EXPOSE 53 53/udp

CMD ["/usr/sbin/dnsmasq", "--no-daemon"]
