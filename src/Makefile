.PHONY: build-services
build-services:
	docker buildx bake -f docker-compose.yml \
		--set "*.platform=linux/amd64"

.PHONY: push-services
push-services:
	docker buildx bake -f docker-compose.yml \
		--push \
		--set "*.platform=linux/amd64"

#		--set "*.platform=linux/amd64,linux/arm64"

