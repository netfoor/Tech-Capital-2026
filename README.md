# Puebla Viva 360

Experiencias turísticas inclusivas para las personas; inteligencia accionable para los destinos de Puebla.

**Pruébalo:** https://puebla-viva-360.vercel.app · Tablero de la Secretaría en `/admin` · Presentación en `/pitch/`

Proyecto del equipo DreamHack para el Hackathon «Puebla Turística 360°: datos que transforman experiencias», de Tech Capital 2026.

## El problema

- En 2025, la capital y Cholula recibieron el **54.2 %** de las llegadas a hotel del estado, y 10 de 11 Pueblos Mágicos tuvieron ocupación por debajo del promedio estatal.
- Solo el **2.2 %** de 1,991 lugares turísticos tiene algún dato de accesibilidad. Quien viaja con una necesidad de movilidad planea a ciegas.

Cifras generadas por [`analysis/01_problema.py`](analysis/01_problema.py) → [`reports/01_problema.md`](reports/01_problema.md).

## La solución

| Para | Qué hace |
|---|---|
| **Visitante** (PWA) | Descubre lugares con su accesibilidad («sin verificar» cuando no hay dato), guarda, planea rutas que respetan sus restricciones y explican por qué, y reporta barreras |
| **Secretaría** (tablero) | Concentración de la demanda y destinos alternativos con datos oficiales, cobertura de información de accesibilidad, experiencia del visitante agregada y moderación de reportes |

Un reporte moderado cambia la ficha, aparece en el tablero y la siguiente ruta ya lo considera. El recomendador tuvo **0** violaciones de accesibilidad frente a **219** de recomendar lo más popular ([`reports/eval_recomendador.md`](reports/eval_recomendador.md)).

## Puesta en marcha

Requisitos: [uv](https://docs.astral.sh/uv/), Node.js ≥ 22.12 y Docker.

```bash
cp .env.example .env
make instalar     # dependencias de backend, pipelines y frontend
make demo         # PostGIS en Docker, migraciones, datos reales y cuenta de demostración
make dev          # API en :8000 y PWA en :5173
make verificar    # pruebas, estilo y compilación
```

`make ayuda` lista todos los comandos. Para publicar, ver [`docs/despliegue.md`](docs/despliegue.md).

## Estructura

```
├── backend/      API FastAPI: catálogo, recomendador, cuentas, reportes, moderación y tablero
├── frontend/     PWA del visitante (/), tablero (/admin) y presentación (public/pitch/)
├── pipelines/    Ingesta y limpieza de fuentes públicas
├── analysis/     Análisis del problema y evaluación del recomendador
├── reports/      Resultados y calidad de datos (los escribe el código)
├── data/         Fuentes originales con SHA-256, referencia, tablas curadas y catálogo de fuentes
├── docs/         Producto, decisiones, API, IA, pitch, entregables y despliegue
└── specs/        Constitución y una carpeta por funcionalidad
```

## Documentación

| Para… | Lee |
|---|---|
| Entender todo el proyecto (personas o asistentes) | [`CONTEXTO.md`](CONTEXTO.md) |
| Tomar una tarea | [`AGENTS.md`](AGENTS.md) y [`specs/constitucion.md`](specs/constitucion.md) |
| Ver qué está hecho y qué falta | [`STATUS.md`](STATUS.md) |
| Presentar | [`docs/pitch/`](docs/pitch/) |
| Revisar los entregables de la convocatoria | [`docs/ENTREGABLES.md`](docs/ENTREGABLES.md) |
| Desplegar | [`docs/despliegue.md`](docs/despliegue.md) |

## Propiedad intelectual

De acuerdo con la sección 14 de la convocatoria, la propiedad intelectual permanece con sus autores. Los organizadores reciben una autorización de uso no exclusiva, gratuita y no comercial, solo para difusión. La licencia del código está pendiente de decisión del equipo; mientras tanto, todos los derechos quedan reservados.
