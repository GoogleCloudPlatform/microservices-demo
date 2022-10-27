# Tor + Kubernetes
Plan is to:
1. Load test using src/loadgenerator/locustfile.py.
    - Figure out [locustio bug for spawning multiple users](https://github.com/locustio/locust/wiki/Installation#increasing-maximum-number-of-open-files-limit).
    - Response times (50-99 percentile, multiple users, request types/endpoints)

2. Install Tor in Online Boutique.
    - FFI bindings Golang/Rust.
    - gRPCs (encryption microservice in the gateway?).

## Setup
Configure an insecure registry in minikube following [this guide](https://gist.github.com/trisberg/37c97b6cc53def9a3e38be6143786589).

Then:

```bash
minikube start --cpus 4 --memory 4096 --insecure-registry 0.0.0.0:5000
```

## SOCKS hacking
### Ocean
- [ ] Find a [SOCKS implementation](https://pkg.go.dev/golang.org/x/net/internal/socks) in Golang (or write it ourselves)
- [ ] Confirm that we can ping ~arti~ through this implementation in the same way as `httping -x 127.0.0.1:9150 -g http://www.google.com -5`.

### Together
- [ ] Connect to ~arti~ from customized emissary installed on local k8s cluster.
- [ ] Send all packets to that ~arti~ connection, rather than via the device interface.
- [ ] Profile? Ask Theo.

