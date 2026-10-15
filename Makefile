SERVICES := currencyservice paymentservice

.PHONY: secrets clean-secrets up down logs stop

secrets:
	@for svc in $(SERVICES); do \
		if [ -f src/$$svc/.env.enc.env ]; then \
			echo "Decrypting src/$$svc/.env"; \
			sops --decrypt src/$$svc/.env.enc.env > src/$$svc/.env; \
		fi \
	done

clean-secrets:
	@for svc in $(SERVICES); do \
		rm -f src/$$svc/.env; \
	done

up: secrets
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

stop: down clean-secrets