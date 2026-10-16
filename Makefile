# Comandos del proyecto. `make ayuda` muestra la lista.
SHELL := /bin/bash
.DEFAULT_GOAL := ayuda

PERFIL ?= Fortino-IAM-Admin
PIPE := cd pipelines && uv run
BACK := cd backend && uv run
FRONT := cd frontend && npm run
TF := cd infra && terraform
PATRON_LLAVES := AIza[0-9A-Za-z_-]{35}|(^|[^A-Za-z0-9])sk-(proj-)?[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----

.PHONY: ayuda instalar db migrar dev api pwa datos verificar secretos demo infra-plan infra-aplicar

ayuda: ## Muestra esta lista
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-14s %s\n", $$1, $$2}'

instalar: ## Instala las dependencias de backend, pipelines y frontend
	cd backend && uv sync
	cd pipelines && uv sync
	cd frontend && npm ci

db: ## Levanta PostGIS en Docker y aplica las migraciones
	docker compose up -d db
	@until docker compose exec -T db pg_isready -U pueblaviva >/dev/null 2>&1; do sleep 1; done
	$(MAKE) migrar

migrar: ## Aplica las migraciones de Alembic
	$(BACK) alembic upgrade head

dev: ## API en :8000 y PWA en :5173
	$(MAKE) -j2 api pwa

api: ## Solo la API, con recarga
	$(BACK) uvicorn app.main:app --reload --port 8000

pwa: ## Solo la PWA, con recarga
	$(FRONT) dev

datos: ## Regenera data/curado/ con las etapas que no usan red
	$(PIPE) radar fuentes
	$(PIPE) radar catalogo
	$(PIPE) radar indicadores

verificar: secretos ## Llaves, pruebas, estilo y compilación
	$(BACK) pytest -q
	$(BACK) ruff check .
	$(BACK) ruff format --check .
	$(PIPE) pytest -q
	$(PIPE) ruff check .
	$(PIPE) ruff format --check .
	$(PIPE) radar fuentes
	$(PIPE) radar catalogo
	$(FRONT) lint
	$(FRONT) test
	$(FRONT) build

secretos: ## Busca patrones de llaves en los archivos del repositorio
	@if git grep --untracked -nIE '$(PATRON_LLAVES)' -- . ':(exclude)Makefile'; then \
	  echo "Hay una posible llave en un archivo del repositorio. Debe ir en .env."; exit 1; \
	else echo "Sin llaves en los archivos del repositorio."; fi

demo: db ## Base con datos semilla y la app lista para la demo
	@echo "Los datos semilla se cargan cuando exista la spec 012. Luego: make dev"

infra-plan: ## Muestra el plan de Terraform
	$(TF) init -input=false && terraform plan -var="perfil_aws=$(PERFIL)"

infra-aplicar: ## Aplica la infraestructura después de revisar el plan
	$(TF) init -input=false && terraform apply -var="perfil_aws=$(PERFIL)"
