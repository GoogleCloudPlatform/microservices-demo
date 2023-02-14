- [Introduction](#introduction)
  - [Use Cases](#use-cases)
  - [Implementation](#implementation)
- [Usage](#usage)
  - [1. Install pre-requisite tools](#1-install-pre-requisite-tools)
  - [2. Clone sample services](#2-clone-sample-services)
  - [3. Build and Push Images (Optional)](#3-build-and-push-images-optional)
    - [Build images from source](#build-images-from-source)
    - [Push services to container registry](#push-services-to-container-registry)
  - [4. Deploy](#4-deploy)
  - [5. Interacting with the microservices](#5-interacting-with-the-microservices)
    - [Add to cart using gRPC API](#add-to-cart-using-grpc-api)
    - [Add to cart using REST API](#add-to-cart-using-rest-api)
    - [Add to cart using Thrift API](#add-to-cart-using-thrift-api)
    - [Verify contents of cart](#verify-contents-of-cart)
  - [Contributing Code](#contributing-code)


# Introduction

This is a demo project based on [GCP **Online Boutique**](https://github.com/GoogleCloudPlatform/microservices-demo) with added support for REST and Thrift APIs. It is designed to be used during cloud-native development for testing across different APIs–REST, gRPC, and Thrift. It is extensible in support of  future functionality (e.g. GraphQL).


## Use Cases

1. Use as a test project for developing cloud-native dev tools.
2. Learn how gRPC, Thrift and REST APIs can be used in a microservices application.

Implemented by the [Skyramp](www.skyramp.dev) team.

## Implementation
For each microservice in the repo, REST and Thrift implementations open up separate ports to listen to the corresponding traffic. Implementations are in the `rest.go` and `thrift.go` files in the top-level directory for each service. 

Default ports for REST and Thrift are hardcoded in the `main.go` file in each service directory. For example, the `carts` microservice has the following ports defined:

```
const (
	serverCrt         = "server.crt"
	serverKey         = "server.key"
	defaultThriftPort = "50000"
	defaultRestPort   = "60000"
)
```
# Usage

## 1. Install pre-requisite tools
- docker
- curl (required for REST)
- jq (optional)
- kubectl (optional)


## 2. Clone sample services
```
git clone https://github.com/letsramp/sample-microservices.git
cd sample-microservices/src
```

## 3. Build and Push Images (Optional)

Images for sample-microservices are already available in a publicly accessible registry. To use your own registry, follow these steps.

### Build images from source 
```
docker compose build
```

### Push services to container registry
Update the host path/s in the docker-compose.yaml file to point to your down docker registry. Push images by running: 

```
docker compose push
```

## 4. Deploy

Deploy Online Boutique by running the following command:

```
docker compose up
```
Now, familiarize yourself with the application by navigating to http://127.0.0.1:8080 on your browser.

<br/><br/>
<img width="1728" alt="Online Boutique" src="https://user-images.githubusercontent.com/1672645/217123094-00e455d5-316d-44f3-8e80-b56da07b668d.png">
<br/><br/>

> 📝 **NOTE:** You can look at the logs for `cart service` to see that we've opened up separate ports for gRPC(7070), REST(60000), and Thrift(50000) traffice to the service. 


<img width="1127" alt="Logs for Carts Service" src="https://user-images.githubusercontent.com/1672645/217123495-9a516fe5-3bf1-4e97-bd46-2270ae130df6.png">


## 5. Interacting with the microservices

To demonstrate the REST and Thrift implementations, we've created simple clients (`src/clients`) for the "add to cart" scenario for each of the APIs. The clients code is accessivle from the `clients` container in the cluster.

To connect to the `clients` container, run the following command in your terminal:

```
docker compose exec -it clients ash
```


Optionally,you can download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) to follow along.

If you are using Docker Desktop, click on the "clients_1" container and go to the CLI from there to run the commands below.

<img width="1122" alt="CLI for the clients container" src="https://user-images.githubusercontent.com/1672645/217331154-3be0e78b-3c22-43c3-bdb2-ac5b5365c50b.png">


### Add to cart using gRPC API

1. In the `clients` container, navigate to the grpc/golang folder and download the required `go` modules.
```
cd /grpc/golang
go mod download
```

2. In the `addCart.go` file, you will notice that we open a connection to port 7070 of `cart` microservice which listens to grpc traffic. 

```
conn, err := grpc.Dial("cartservice:7070", grpc.WithInsecure())
```

Run the code in the file to add an item to the cart.

```
go run ./cmd/cart
```
Expected result
```
Successfully added the item to the cart.
```

Having seen how to successfully add an item to the cart with a gRPC client calling the gRPC endpoint, we can see how to do the same through the REST and Thrift endpoints.

### Add to cart using REST API

Since cURL is already installed in the `clients` container, you can issue a request directly from the CLI as of the container to add an item to the cart.

```
curl -X 'POST' 'http://cartservice:60000/cart/user_id/abcde' \
  -H 'accept: application/json' \
  -H 'content-type: application/json' \
  -d '{
  "product_id": "L9ECAV7KIM",
  "quantity": 1
}'
```

Again, notice that the request is being sent to port `60000` of `cart` microservice which listens to REST traffic.

Result

```
{"success":"200 OK"}
```

### Add to cart using Thrift API

1. In the `clients` container, navigate to the thrift/golang folder and download the required `go` modules for the Thrift client.

Setup
```
cd /thrift/golang
go mod download
```

2. In the `addCart.go` file, you will notice that we open a connection to port 50000 of `cart` microservice which listens to Thrift traffic. 

```
clientAddr := "cartservice:50000"
```

Now, run the code in the file to add an item to the cart.

```
go run ./cmd/cart
```

Result:

```
"Successfully added the item to the cart."
```


### Verify contents of cart

You can now fetch the contents of the cart using REST API to see that a total of 3 items were added (one using each supported API).

```
curl -X 'GET' \
  'http://cartservice:60000/cart/abcde' \
   -H 'accept: application/json'
```

Result:

```
{"user_id":"abcde","items":[{"product_id":"OLJCESPC7Z","quantity":3}]}
```


## Contributing Code

PRs are welcome!  

This project follows the [CNCF Code of Conduct](https://github.com/cncf/foundation/blob/main/code-of-conduct.md) .

<br>

