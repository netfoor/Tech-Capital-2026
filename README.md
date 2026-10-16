# Puebla Viva 360

Plataforma de experiencias turísticas inclusivas e inteligencia territorial para Puebla. Tiene dos productos que comparten catálogo y métricas, pero no datos personales:

1. **Para el visitante (PWA):** descubrir, guardar, planear, vivir y recordar recorridos, con la accesibilidad como criterio de primera clase.
2. **Para la Secretaría de Desarrollo Turístico (tablero):** señales agregadas y trazables para decidir dónde mejorar accesos, señalización y servicios, y qué destinos alternativos promover.

> Una Puebla que se descubre entre todos y se comprende con datos: experiencias inclusivas para las personas, inteligencia accionable para sus destinos.

Proyecto del equipo DreamHack para el Hackathon «Puebla Turística 360°: datos que transforman experiencias», de Tech Capital 2026.

## El problema

La visita turística en Puebla se concentra en pocos polos, como la capital y Cholula, mientras otros destinos con oferta cultural y natural reciben poca demanda. El visitante no encuentra información confiable y unificada sobre costo, horarios y, sobre todo, accesibilidad física. Quien tiene una necesidad de movilidad, viaja con personas mayores o con poco presupuesto planea a ciegas o se queda en lo más conocido. La Secretaría tiene indicadores hoteleros agregados, pero no señales finas sobre permanencia, satisfacción y barreras por destino.

El análisis con datos está en `reports/` (spec 013) y la evidencia pública en [`docs/producto/evidencia.md`](docs/producto/evidencia.md).

## El circuito cerrado

La misma señal de accesibilidad sirve para personalizar la ruta del visitante y para revelar una brecha territorial a la Secretaría. Cuando la brecha se corrige, las siguientes recomendaciones mejoran.

```
ruta con restricciones → visita → reporte de barrera → moderación → la ficha cambia
        ↑                                                              ↓
 la siguiente recomendación la considera  ←  el tablero muestra la brecha
```

## Puesta en marcha

Requisitos: [uv](https://docs.astral.sh/uv/), Node.js ≥ 22.12 y Docker.

```bash
cp .env.example .env     # llaves opcionales; .env nunca se versiona
make instalar            # dependencias de backend, pipelines y frontend
make db                  # PostGIS en Docker y migraciones
make dev                 # API en :8000 y PWA en :5173
make verificar           # pruebas, estilo y compilación
```

`make ayuda` muestra todos los comandos.

## Estructura

```
├── backend/          API FastAPI: catálogo, recomendador, recorridos, reseñas y tablero
├── frontend/         PWA del visitante (/) y tablero de la Secretaría (/admin)
├── pipelines/        Ingesta y limpieza de fuentes públicas (Python con uv)
├── data/             Fuentes originales, referencia y tablas curadas
├── analysis/         Análisis del problema y evaluación del recomendador
├── metrics/          Definición de cada indicador
├── reports/          Resultados y calidad de datos
├── docs/             Producto, dominio, decisiones, IA, privacidad y entregables
├── specs/            Constitución y una carpeta por funcionalidad
└── infra/            Terraform (AWS), para cuando el MVP esté estable
```

## Cómo se trabaja

- [`specs/constitucion.md`](specs/constitucion.md): principios que ninguna tarea rompe.
- [`docs/producto/contexto-maestro.txt`](docs/producto/contexto-maestro.txt): definición completa del producto.
- [`docs/plan-de-ejecucion.md`](docs/plan-de-ejecucion.md): specs, carriles y ruta crítica.
- [`docs/requirements.md`](docs/requirements.md) y [`docs/ENTREGABLES.md`](docs/ENTREGABLES.md): requisitos y entregables de la convocatoria.
- [`STATUS.md`](STATUS.md): qué está hecho, en curso y bloqueado.
- [`AGENTS.md`](AGENTS.md): reglas para tomar una tarea.

## Propiedad intelectual

De acuerdo con la sección 14 de la convocatoria, la propiedad intelectual permanece con sus autores. Los organizadores reciben una autorización de uso no exclusiva, gratuita y no comercial, solo para difusión. La licencia del código está pendiente de decisión del equipo; mientras tanto, todos los derechos quedan reservados.
