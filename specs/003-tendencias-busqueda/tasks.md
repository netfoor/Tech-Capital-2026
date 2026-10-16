# Tareas 003 · Tendencias de búsqueda

- [x] T003-01 Extra `senales` (`pytrends` y `httpx`) en `pyproject.toml`; `uv sync --extra senales` resuelve con urllib3 2. Los reintentos se programan en `trends.py` (FR-003-05) y no con el parámetro `retries` de `TrendReq`, que usa `method_whitelist` y falla con urllib3 2. Verificación: `uv run python -c "import pytrends"`.
- [x] T003-02 `radar/senales/trends.py`: armado de lotes con ancla y reescalado por lote (FR-003-01 a 03), con pruebas sintéticas. Verificación: `uv run pytest tests/test_trends.py`.
- [x] T003-03 Consulta con pausas, reintentos y guardado de lo crudo (FR-003-04 y 05). Verificación: un lote real guardado en `data/crudo/trends/`.
- [x] T003-04 Comando `radar senales trends` y tabla `interes_busqueda_mensual.csv` para los 12 Pueblos Mágicos en MX. Se ejecuta desde una red residencial. Verificación: 12 destinos × periodos desde 2017-01; ningún destino con todos los meses en 0.
- [x] T003-05 [P] Reproducir el pico de noviembre de Chignahuapan frente a la afluencia oficial y guardar la gráfica en `docs/entregables/figuras/`. Verificación: figura y una nota en `09-resultados.md`.
- [ ] T003-06 [P] (P1) Repetición de un lote otro día y reporte de variabilidad. Verificación: correlación reportada en el plan.
- [~] T003-07 [P] (P1) Serie en región US. Verificación: filas con `geo=US`.

> 2026-10-16 · T003-03 y T003-04 se corrieron desde la computadora del equipo: 12 destinos, 2017-01 a 2026-09, 1 404 filas. El crudo (`data/crudo/trends/`) se conserva fuera de git.
