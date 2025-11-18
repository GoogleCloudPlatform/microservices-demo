
# Docker build args
variable "IMAGE_REPO" {default = "ghcr.io/riptideslabs/microservices-demo"}
variable "IMAGE_TAG" {default = "test"}

function "get_tag" {
    params = [tags, name]
      result = [for t in tags : replace(t, "${name}", name)]
}

# docker-bake.hcl
group "default" {
    targets = [
        "emailservice",
        "productcatalogservice",
        "recommendationservice",
        "shoppingassistantservice",
        "shippingservice",
        "checkoutservice",
        "paymentservice",
        "currencyservice",
        "cartservice",
        "frontend",
        "adservice",
        "loadgenerator"
    ]
}

target "_common" {
  output = [
    "type=image",
  ]
  platforms = [
    "linux/arm64",
    "linux/amd64",
  ]
}

target "docker-metadata-action" {
  tags = [
    "${IMAGE_REPO}/${name}:${IMAGE_TAG}",
    # "${IMAGE_REPO}/${name}:latest"
  ]
}

target "emailservice" {
    context = "src/emailservice"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.emailservice.name}")
}

target "productcatalogservice" {
    context = "src/productcatalogservice"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.productcatalogservice.name}")
}

target "recommendationservice" {
    context = "src/recommendationservice"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.recommendationservice.name}")
}

target "shoppingassistantservice" {
    context = "src/shoppingassistantservice"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.shoppingassistantservice.name}")
}

target "shippingservice" {
    context = "src/shippingservice"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.shippingservice.name}")
}

target "checkoutservice" {
    context = "src/checkoutservice"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.checkoutservice.name}")
}

target "paymentservice" {
    context = "src/paymentservice"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.paymentservice.name}")
}

target "currencyservice" {
    context = "src/currencyservice"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.currencyservice.name}")
}

target "cartservice" {
    context = "src/cartservice/src"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.cartservice.name}")
}

target "frontend" {
    context = "src/frontend"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.frontend.name}")
}

target "adservice" {
    context = "src/adservice"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.adservice.name}")
}

target "loadgenerator" {
    context = "src/loadgenerator"
    dockerfile = "./Dockerfile"
    inherits = [
        "_common",
        "docker-metadata-action",
    ]
    tags = get_tag(target.docker-metadata-action.tags, "${target.loadgenerator.name}")
}
