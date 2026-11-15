# Online Boutique (app source only)

Online Boutique is a cloud-native e-commerce demo: a web store where users browse products, add them to a cart and check out. It is made of polyglot microservices that talk to each other over gRPC (protos in `protos/`), fronted by an HTTP web server.

This repository contains **only the application source**. All DevOps (containers, CI/CD, infrastructure, deployment, observability) is being built from scratch in phases.

## Services

| Service | Language | Port (default) |
|---|---|---|
| frontend | Go | 8080 |
| cartservice | C# | 7070 |
| productcatalogservice | Go | 3550 |
| currencyservice | Node.js | 7000 |
| paymentservice | Node.js | 50051 |
| shippingservice | Go | 50051 |
| emailservice | Python | 8080 |
| checkoutservice | Go | 5050 |
| recommendationservice | Python | 8080 |
| adservice | Java | 9555 |
| shoppingassistantservice | Python | 8080 |
| loadgenerator | Python (Locust) | 8089 (Locust web UI) |

Most services read `PORT` from the environment; the ports above are the upstream defaults/conventions and must be set explicitly where the code has no default (e.g. paymentservice, currencyservice).

## License and attribution

Derived from [GoogleCloudPlatform/microservices-demo](https://github.com/GoogleCloudPlatform/microservices-demo), Copyright Google LLC, licensed under the Apache License 2.0. See [LICENSE](LICENSE).
