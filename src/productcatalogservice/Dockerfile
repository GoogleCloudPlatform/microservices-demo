FROM golang:1.20.6-alpine@sha256:6f592e0689192b7e477313264bb190024d654ef0a08fb1732af4f4b498a2e8ad AS builder
RUN apk add --no-cache ca-certificates git
RUN apk add build-base
ARG SEALIGHTS_TOKEN=eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL1BST0QtQ1VTVE9NRVJTMi5hdXRoLnNlYWxpZ2h0cy5pby8iLCJqd3RpZCI6IlBST0QtQ1VTVE9NRVJTMixuZWVkVG9SZW1vdmUsQVBJR1ctZDk5MWY3YWMtMDc2MC00OTQ4LWIzNzctZmUzZjEwYjU5NGNiLDE2OTEwMDIzMDkzMTgiLCJzdWJqZWN0Ijoic2VhbGlnaHRzX21vbml0b3JAYWdlbnQiLCJhdWRpZW5jZSI6WyJhZ2VudHMiXSwieC1zbC1yb2xlIjoiYWdlbnQiLCJ4LXNsLXNlcnZlciI6Imh0dHBzOi8vdHV0b3JpYWwuc2VhbGlnaHRzLmNvL2FwaSIsInNsX2ltcGVyX3N1YmplY3QiOiIiLCJpYXQiOjE2OTEwMDIzMDl9.PPpTPq4cHdX3J6e9TPkaLzJ-9l3ZvPHVjxch4Wfs1alBY7PlZSggi6nEaDcyzEp13FIi9_LT_qecJs7wzkmT4bNYxLqTSc773Btifo3_R22VdcDOq-RtXlU3CsR9fNXg1jHbwhkeQEsefT2Xly0vtxT0bqXjipLlCT6DwldR-9yagZA5x98JNGRCY3Ch9a6jrxRu9AQXMkLAE-2Cxti9IoTCSQPa3Yi_UajPLmHwF0tCcGxAmm03UdcReIF_KjnHdD7uOwvkIx4frzi7a1_AAInnDxMZzMYxRtCEb_MFRIZKQIz43n53aPR6lTZMce4dA00AxKtU-6oHKmteC0KLQYHLs1YhzzoOwmM42EcL2BeSKhIHc4iGsyuSsmroeIU_Mbj1EgkKa1nsnUCdozc2ev4ytRALvQEY9OZcwWKAEndqScZZw8VKPAwKEgvabY9apc2u9BLpqBlh8En3HW5FMwGhVzoYnRYtHnKnaT_ndddQ9RiDPrMeNFnleqjZoOmPIw8QJc_02boytk5eCW1EMSBimV-Eh-EIsMojgpEaF2hCwjSDzvFAYS0ClbM6iUvowyfFp59WkLohBWsgAfHceG4IzEPt1NpDC1czCTJVZMyuCg8VjsSisr0nU7mKvCjyYs9R0Y5AGaGfHK9nbS-WUuWgSvIzGpqzbdkS03mpxl8
ARG BRANCH_NAME=master
ARG BUILD_NAME=productcatalogservice1.5
ARG SERVICE_NAME=productcatalogservice
ENV OS_ARCH linux-amd64

WORKDIR /src

# restore dependencies
COPY go.mod go.sum ./
RUN go mod download
COPY . .

RUN wget -U "slgoagent" -q -O slgoagent.tar.gz \
   https://agents.sealights.co/slgoagent/latest/slgoagent-${OS_ARCH}.tar.gz \
    && tar -xvf slgoagent.tar.gz \
    && rm slgoagent.tar.gz
RUN wget -U "slcli" -q -O slcli.tar.gz \
    https://agents.sealights.co/slcli/latest/slcli-${OS_ARCH}.tar.gz \
    && tar -xvf slcli.tar.gz \
    && rm slcli.tar.gz
RUN echo ${SEALIGHTS_TOKEN} >> ./token.txt
RUN ./slcli config init --lang go --token ./token.txt
RUN ./slcli config create-bsid --app ${SERVICE_NAME} --branch ${BRANCH_NAME} --build ${BUILD_NAME}
RUN ./slcli scan --bsid buildSessionId.txt --path-to-scanner ./slgoagent --workspacepath ./ --scm none



# Skaffold passes in debug-oriented compiler flags
ARG SKAFFOLD_GO_GCFLAGS
RUN go build -gcflags="${SKAFFOLD_GO_GCFLAGS}" -o /productcatalogservice .

FROM alpine:3.18.2@sha256:82d1e9d7ed48a7523bdebc18cf6290bdb97b82302a8a9c27d4fe885949ea94d1
RUN apk add --no-cache ca-certificates

WORKDIR /src
COPY --from=builder /productcatalogservice ./server
COPY products.json .

# Definition of this variable is used by 'skaffold debug' to identify a golang binary.
# Default behavior - a failure prints a stack trace for the current goroutine.
# See https://golang.org/pkg/runtime/
ENV GOTRACEBACK=single

EXPOSE 3550
CMD export SEALIGHTS_TOKEN="${SL_TOKEN}" && export SEALIGHTS_LAB_ID="${SL_LAB_ID}" && /src/server
