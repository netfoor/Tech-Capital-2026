# Comandos del proyecto. `make ayuda` muestra la lista.
SHELL := /bin/bash
.DEFAULT_GOAL := ayuda

PERFIL ?= Fortino-IAM-Admin
UV := cd pipelines && uv run
TF := cd infra && terraform
PATRON_LLAVES := AIza[0-9A-Za-z_-]{35}|(^|[^A-Za-z0-9])sk-(proj-)?[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----

.PHONY: ayuda instalar datos exportar verificar secretos dev web web-config infra-plan infra-aplicar desplegar

ayuda: ## Muestra esta lista
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-14s %s\n", $$1, $$2}'

instalar: ## Instala las dependencias de pipelines y del sitio
	cd pipelines && uv sync
	cd web && npm ci

datos: ## Regenera data/curado/ con las etapas que no usan red
	$(UV) radar fuentes
	$(UV) radar catalogo
	$(UV) radar exportar --validar
	$(UV) radar indicadores
	$(UV) radar radar calcular

exportar: ## Genera web/public/datos/ y su manifiesto (spec 009)
	$(UV) radar exportar

verificar: secretos ## Llaves, pruebas, estilo, huellas de fuentes y catálogo
	$(UV) pytest -q
	$(UV) ruff check .
	$(UV) ruff format --check .
	$(UV) radar fuentes
	$(UV) radar catalogo
	$(UV) radar exportar --validar

secretos: ## Busca patrones de llaves en los archivos del repositorio
	@if git grep --untracked -nIE '$(PATRON_LLAVES)' -- . ':(exclude)Makefile'; then \
	  echo "Hay una posible llave en un archivo del repositorio. Debe ir en .env."; exit 1; \
	else echo "Sin llaves en los archivos del repositorio."; fi

dev: ## Sirve el sitio en local con recarga
	cd web && npm run dev

web: ## Compila el sitio en web/dist/
	cd web && npm run build

web-config: ## Escribe web/.env con el dominio y el cliente de Cognito (salidas de Terraform)
	cd infra && printf 'PUBLIC_COGNITO_DOMINIO=%s\nPUBLIC_COGNITO_CLIENTE_ID=%s\n' "$$(terraform output -raw cognito_dominio)" "$$(terraform output -raw cognito_cliente_id)" > ../web/.env
	@echo "web/.env listo. Compila con: make web"

infra-plan: ## Muestra el plan de Terraform
	$(TF) init -input=false && terraform plan -var="perfil_aws=$(PERFIL)"

infra-aplicar: ## Aplica la infraestructura después de revisar el plan
	$(TF) init -input=false && terraform apply -var="perfil_aws=$(PERFIL)"

desplegar: ## Sube web/dist/ a S3 e invalida la caché de CloudFront
	PERFIL=$(PERFIL) ./infra/desplegar.sh
