# Wishlist Service

Keeps one or more wish lists per shopper. Added on top of the upstream
Online Boutique demo.

Like every other backend in the demo it speaks **gRPC**, owns its own datastore
(`redis-wishlist`), holds no state in the process, and is deployed as an
independent Deployment + Service. The contract lives in
[`protos/wishlist.proto`](../../protos/wishlist.proto).

## Storage layout

Per user (the anonymous session id from the shop cookie):

| Key | Type | Contents |
| --- | --- | --- |
| `wl:<user>:index` | HASH | field = list id, value = `{"name":...,"created_at":...}` |
| `wl:<user>:<list id>` | ZSET | member = product id, score = time added |

The sorted set gives de-duplication and newest-first ordering for free. Both
keys get a TTL (`WISHLIST_TTL_SECONDS`, 48h by default) so abandoned sessions
and load generator traffic cannot grow the dataset without bound.

## Configuration

| Variable | Required | Default | Meaning |
| --- | --- | --- | --- |
| `REDIS_ADDR` | yes | – | host:port of the Redis instance |
| `PORT` | no | `8080` | gRPC listen port |
| `WISHLIST_TTL_SECONDS` | no | `172800` | expiry refreshed on every write |

Limits: 20 lists per user, 100 items per list.

## API

`hipstershop.WishlistService`:

| RPC | Request | Returns |
| --- | --- | --- |
| `CreateWishlist` | `user_id`, `name` | the new `Wishlist` |
| `ListWishlists` | `user_id` | every `Wishlist` with its `item_count` |
| `GetWishlist` | `user_id`, `id` | one `Wishlist` including `items` |
| `RenameWishlist` | `user_id`, `id`, `name` | the renamed `Wishlist` |
| `DeleteWishlist` | `user_id`, `id` | `WishlistEmpty` |
| `AddWishlistItem` | `user_id`, `id`, `product_id` | `WishlistEmpty` |
| `RemoveWishlistItem` | `user_id`, `id`, `product_id` | `WishlistEmpty` |
| `GetWishlistSummary` | `user_id` | `list_count`, `item_count` |

Status codes: `INVALID_ARGUMENT` for bad input, `NOT_FOUND` for an unknown
list, `RESOURCE_EXHAUSTED` when a limit is reached, `UNAVAILABLE` when Redis is
down.

A `Wishlist` carries product ids only. Names, pictures and prices are resolved
by the frontend against the product catalog on every render, so a wish list can
never show a stale price.

### Health checking

The standard `grpc.health.v1.Health` service is registered, with two levels:

| Request | Meaning | Used by |
| --- | --- | --- |
| empty `service` | the process is alive | liveness probe |
| `service: hipstershop.WishlistService` | Redis answers too | readiness probe |

That split is why a Redis outage takes the pod out of the load balancer instead
of restarting it in a loop.

## Generating the gRPC code

The generated stubs are checked in, as they are for every other service. After
changing `protos/wishlist.proto`, regenerate them from the repository root:

```sh
./gen-wishlist-protos.sh
```

That runs `protoc` and the Go plugins inside a container, so nothing needs to be
installed locally. It writes `src/wishlistservice/genproto/` and
`src/frontend/genproto/`, and runs `go mod tidy` for this service.

If you do have the toolchain installed, `./genproto.sh` in this directory is the
same command the other services use.

## Local run

```sh
docker run --rm -d -p 6379:6379 --name wl-redis redis:alpine
REDIS_ADDR=localhost:6379 go run .
```

Server reflection is enabled, so `grpcurl` needs no `.proto` file:

```sh
grpcurl -plaintext localhost:8080 list
grpcurl -plaintext -d '{"user_id":"demo","name":"Christmas"}' \
  localhost:8080 hipstershop.WishlistService/CreateWishlist
grpcurl -plaintext -d '{"user_id":"demo"}' \
  localhost:8080 hipstershop.WishlistService/ListWishlists
grpcurl -plaintext -d '{"service":"hipstershop.WishlistService"}' \
  localhost:8080 grpc.health.v1.Health/Check
```

## Notes

There is no login in Online Boutique: the frontend generates an anonymous
session id and stores it in a cookie, and that id is the `user_id` here. Wish
lists therefore live per browser, and disappear when the cookie does.
