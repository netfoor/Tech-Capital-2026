# Tareas 015 · Recomendador inclusivo

Formato: `[ ]` pendiente, `[~]` en curso, `[x]` hecha. `[P]` = paralelizable con otras tareas de esta spec.

## Motor

- [ ] T015-01 Tipos del contrato (`tipos.py`) y configuración documentada (`config.py`). Verificación: la spec 014 los importa sin cambios.
- [ ] T015-02 [P] Parser conservador de horarios. Verificación: `uv run pytest tests/test_recomendador_horarios.py`.
- [ ] T015-03 Etapas 1 a 4 y `recomendar()`. Verificación: `uv run pytest tests/test_recomendador_motor.py`.
- [ ] T015-04 Verificador independiente y prueba de propiedad «una restricción indispensable nunca se viola». Verificación: `uv run pytest tests/test_recomendador_propiedades.py` con 0 violaciones.
- [ ] T015-05 Multi-día con agrupamiento con capacidad. Verificación: `uv run pytest tests/test_recomendador_multidia.py`.

## Evaluación

- [ ] T015-06 [P] Baselines de popularidad y cercanía. Verificación: `uv run pytest tests/test_recomendador_baselines.py`.
- [ ] T015-07 Catálogo sintético rotulado y cargador del contrato de la spec 012. Verificación: `backend/tests/datos/poi_sintetico.csv` con `is_synthetic=true` en cada fila.
- [ ] T015-08 Evaluación offline con 40 perfiles. Verificación: `uv run python ../analysis/02_eval_recomendador.py` escribe `reports/eval_recomendador.md` y `.csv`.
- [ ] T015-09 Model card. Verificación: `docs/ia/model_card_recomendador.md` con las cifras del reporte y su `n`.
