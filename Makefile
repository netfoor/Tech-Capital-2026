# Comandos del proyecto. `make ayuda` muestra la lista.
SHELL := /bin/bash
.DEFAULT_GOAL := ayuda

PIPE := cd pipelines && uv run
BACK := cd backend && uv run
FRONT := cd frontend && npm run
VERCEL := npx -y vercel@50.4.0
PATRON_LLAVES := AIza[0-9A-Za-z_-]{35}|(^|[^A-Za-z0-9])sk-(proj-)?[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----

.PHONY: ayuda instalar db migrar semilla demo dev api pwa datos analisis verificar secretos desplegar

ayuda: ## Muestra esta lista
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-12s %s\n", $$1, $$2}'

instalar: ## Instala las dependencias de backend, pipelines y frontend
	cd backend && uv sync
	cd pipelines && uv sync --all-extras
	cd frontend && npm ci

db: ## Levanta PostGIS en Docker y aplica las migraciones
	docker compose up -d db
	@until docker compose exec -T db pg_isready -U pueblaviva >/dev/null 2>&1; do sleep 1; done
	$(MAKE) migrar

migrar: ## Aplica las migraciones de Alembic
	$(BACK) alembic upgrade head

semilla: ## Carga el catálogo, la serie oficial y las fichas de indicadores en la base
	$(BACK) python -m app.services.semilla

demo: db semilla ## Base lista para la demo: datos reales más visitantes sintéticos etiquetados
	$(BACK) python -m app.services.demo_tablero

dev: ## API en :8000 y PWA en :5173
	$(MAKE) -j2 api pwa

api: ## Solo la API, con recarga
	$(BACK) uvicorn app.main:app --reload --port 8000

pwa: ## Solo la PWA, con recarga
	$(FRONT) dev

datos: ## Regenera data/curado/ y el reporte de calidad sin usar la red
	$(PIPE) radar fuentes
	$(PIPE) radar catalogo
	$(PIPE) radar indicadores
	$(PIPE) radar corredor integrar
	$(PIPE) radar corredor reporte

analisis: ## Análisis del problema y evaluación del recomendador (escribe reports/)
	uv run --project pipelines --extra analisis python analysis/01_problema.py
	cd backend && uv run python ../analysis/02_eval_recomendador.py

verificar: secretos ## Llaves, pruebas, estilo y compilación de todo el proyecto
	$(BACK) pytest -q
	$(BACK) ruff check .
	$(BACK) ruff format --check .
	$(PIPE) pytest -q
	$(PIPE) ruff check . ../analysis
	$(PIPE) ruff format --check . ../analysis
	$(PIPE) radar fuentes
	$(PIPE) radar catalogo
	$(FRONT) lint
	$(FRONT) test
	$(FRONT) build

secretos: ## Busca patrones de llaves en los archivos del repositorio
	@if git grep --untracked -nIE '$(PATRON_LLAVES)' -- . ':(exclude)Makefile'; then \
	  echo "Hay una posible llave en un archivo del repositorio. Debe ir en .env."; exit 1; \
	else echo "Sin llaves en los archivos del repositorio."; fi

desplegar: ## Publica en Vercel (producción) después de make verificar
	$(VERCEL) deploy --prod
