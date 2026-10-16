# ADR-0007 · Python con uv y CSV versionados

**Estado:** aceptada · 2026-10-15

## Contexto

Hacen falta pipelines reproducibles, legibles en una revisión de código y fáciles de instalar en cualquier equipo.

## Decisión

- Python ≥ 3.11 gestionado con uv (`pipelines/pyproject.toml` y `uv.lock`).
- Las tablas curadas se guardan como CSV en UTF-8 dentro de git: el diff muestra qué cambió.
- Las respuestas crudas se guardan como JSONL.
- Si una tabla supera los 20 MB, se cambia a Parquet y se registra el cambio aquí.

## Consecuencias

- Hay una sola herramienta para instalar, ejecutar y probar.
- Los CSV se pueden revisar a ojo y la reproducibilidad se comprueba comparando la SHA-256.
