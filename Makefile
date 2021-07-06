PUBLISH_VERSION=$(shell echo ${NEW_VERSION} | sed 's/inner-999/1/g')

GIT_COMMIT=$(shell git rev-parse HEAD)
GIT_ORIGIN=$(shell git config --get remote.origin.url)

build:
	docker build --tag rookout/microservices-demo-adservice:latest --tag rookout/microservices-demo-adservice:${PUBLISH_VERSION} --file ./src/adservice/Dockerfile ./src/adservice --build-arg GIT_COMMIT=${GIT_COMMIT} --build-arg GIT_ORIGIN=${GIT_ORIGIN}
	docker build --tag rookout/microservices-demo-cartservice:latest --tag rookout/microservices-demo-cartservice:${PUBLISH_VERSION} --file ./src/cartservice/src/Dockerfile ./src/cartservice/src --build-arg GIT_COMMIT=${GIT_COMMIT} --build-arg GIT_ORIGIN=${GIT_ORIGIN}
	docker build --tag rookout/microservices-demo-checkoutservice:latest --tag rookout/microservices-demo-checkoutservice:${PUBLISH_VERSION} --file ./src/checkoutservice/Dockerfile ./src/checkoutservice --build-arg GIT_COMMIT=${GIT_COMMIT} --build-arg GIT_ORIGIN=${GIT_ORIGIN}
	docker build --tag rookout/microservices-demo-currencyservice:latest --tag rookout/microservices-demo-currencyservice:${PUBLISH_VERSION} --file ./src/currencyservice/Dockerfile ./src/currencyservice --build-arg GIT_COMMIT=${GIT_COMMIT} --build-arg GIT_ORIGIN=${GIT_ORIGIN}
	docker build --tag rookout/microservices-demo-emailservice:latest --tag rookout/microservices-demo-emailservice:${PUBLISH_VERSION} --file ./src/emailservice/Dockerfile ./src/emailservice --build-arg GIT_COMMIT=${GIT_COMMIT} --build-arg GIT_ORIGIN=${GIT_ORIGIN}
	docker build --tag rookout/microservices-demo-frontend:latest --tag rookout/microservices-demo-frontend:${PUBLISH_VERSION} --file ./src/frontend/Dockerfile ./src/frontend --build-arg GIT_COMMIT=${GIT_COMMIT} --build-arg GIT_ORIGIN=${GIT_ORIGIN}
	docker build --tag rookout/microservices-demo-paymentservice:latest --tag rookout/microservices-demo-paymentservice:${PUBLISH_VERSION} --file ./src/paymentservice/Dockerfile ./src/paymentservice --build-arg GIT_COMMIT=${GIT_COMMIT} --build-arg GIT_ORIGIN=${GIT_ORIGIN}
	docker build --tag rookout/microservices-demo-productcatalogservice:latest --tag rookout/microservices-demo-productcatalogservice:${PUBLISH_VERSION} --file ./src/productcatalogservice/Dockerfile ./src/productcatalogservice --build-arg GIT_COMMIT=${GIT_COMMIT} --build-arg GIT_ORIGIN=${GIT_ORIGIN}
	docker build --tag rookout/microservices-demo-recommendationservice:latest --tag rookout/microservices-demo-recommendationservice:${PUBLISH_VERSION} --file ./src/recommendationservice/Dockerfile ./src/recommendationservice --build-arg GIT_COMMIT=${GIT_COMMIT} --build-arg GIT_ORIGIN=${GIT_ORIGIN}
	docker build --tag rookout/microservices-demo-shippingservice:latest --tag rookout/microservices-demo-shippingservice:${PUBLISH_VERSION} --file ./src/shippingservice/Dockerfile ./src/shippingservice --build-arg GIT_COMMIT=${GIT_COMMIT} --build-arg GIT_ORIGIN=${GIT_ORIGIN}

upload-no-latest:
	docker push rookout/microservices-demo-adservice:${PUBLISH_VERSION}
	docker push rookout/microservices-demo-cartservice:${PUBLISH_VERSION}
	docker push rookout/microservices-demo-checkoutservice:${PUBLISH_VERSION}
	docker push rookout/microservices-demo-currencyservice:${PUBLISH_VERSION}
	docker push rookout/microservices-demo-emailservice:${PUBLISH_VERSION}
	docker push rookout/microservices-demo-frontend:${PUBLISH_VERSION}
	docker push rookout/microservices-demo-paymentservice:${PUBLISH_VERSION}
	docker push rookout/microservices-demo-productcatalogservice:${PUBLISH_VERSION}
	docker push rookout/microservices-demo-recommendationservice:${PUBLISH_VERSION}
	docker push rookout/microservices-demo-shippingservice:${PUBLISH_VERSION}

upload: upload-no-latest
	@if [ ${CIRCLE_BRANCH} = "master" ]; then \
		docker push rookout/microservices-demo-adservice:latest; \
		docker push rookout/microservices-demo-cartservice:latest; \
		docker push rookout/microservices-demo-checkoutservice:latest; \
		docker push rookout/microservices-demo-currencyservice:latest; \
		docker push rookout/microservices-demo-emailservice:latest; \
		docker push rookout/microservices-demo-frontend:latest; \
		docker push rookout/microservices-demo-paymentservice:latest; \
		docker push rookout/microservices-demo-productcatalogservice:latest; \
		docker push rookout/microservices-demo-recommendationservice:latest; \
		docker push rookout/microservices-demo-shippingservice:latest; \
	fi

build-and-upload: build upload