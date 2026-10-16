# Tareas 019 · Tablero institucional

Formato: `[ ]` pendiente, `[~]` en curso, `[x]` hecha. `[P]` = paralelizable con otras tareas de esta spec.

## Indicadores

- [x] T019-01 Spec, plan y tareas. Verificación: revisión del PR.
- [x] T019-02 `backend/metrics/definitions.yaml` y carga a `core.metric_definition` y `core.data_lineage`. Verificación: `tests/test_metricas.py::test_definiciones`.
- [x] T019-03 Servicio de métricas: Oferta–demanda (ocupación, cuartos libres, estadía, crecimiento, HHI, candidatos). Verificación: `tests/test_metricas.py` contra el fixture calculado a mano.
- [x] T019-04 [P] Inclusión: cobertura de información, barreras, tiempo de moderación y prioridades. Verificación: `tests/test_tablero.py`.
- [x] T019-05 [P] Panorama y Experiencia con supresión k, intervalos y separación sintético/real. Verificación: `tests/test_tablero.py`.

## API

- [x] T019-06 Router `/b2b`, `GET /metrics/{id}/lineage`, CSV con metadatos y autorización. Verificación: `tests/test_tablero.py`.
- [x] T019-07 Semilla de demostración con analista y datos sintéticos. Verificación: `uv run python -m app.services.demo_tablero` dos veces sin duplicar.

## Tablero

- [x] T019-08 Tablero en `/admin`: sesión, cuatro módulos, fichas, tablas alternativas, banda sintética, vista ejecutiva y técnica. Verificación: `npm test`, `npm run build`.
- [x] T019-09 Cola de moderación en el tablero. Verificación: `npm test`.
