# Tareas 017 · Recorridos y visitas

Formato: `[ ]` pendiente, `[~]` en curso, `[x]` hecha. `[P]` = paralelizable con otras tareas de esta spec.

## Modelo y contrato

- [~] T017-01 Spec, plan, tareas, sección de recorridos en `docs/api/contrato-p0.md` y columnas nuevas en `docs/dominio/modelo-de-datos.md`. Verificación: revisión del PR.
- [ ] T017-02 Migración `0003` con las columnas nuevas y el estado `visita_confirmada`. Verificación: `uv run alembic downgrade 0002 && uv run alembic upgrade head`.

## Pipeline

- [ ] T017-03 [P] Pipeline puro en `app/pipeline/visitas.py` y horario. Verificación: `tests/test_pipeline_visitas.py`.
- [ ] T017-04 [P] Generador determinista de trazas sintéticas y `data/synthetic/`. Verificación: dos corridas producen el mismo SHA-256; todas las filas con `is_synthetic=true`.
- [ ] T017-05 Evaluación (`reports/eval_visitas.md`) y `docs/calibracion_gps.md`. Verificación: `uv run python -m app.pipeline.evaluar` reproduce el reporte.

## API

- [ ] T017-06 Sesiones: iniciar, muestras, pausar, reanudar, detener, candidatos y demo sintética. Verificación: `tests/test_recorridos.py`.
- [ ] T017-07 Confirmar, corregir o rechazar; check-ins y diario. Verificación: `tests/test_recorridos.py`, con autorización horizontal.

## Privacidad

- [ ] T017-08 Retención con purga de muestras crudas y comando; ninguna respuesta con coordenadas; registros sin coordenadas; `DELETE /me` borra recorridos. Verificación: `tests/test_recorridos.py`.
