# Tareas 006 · Auditoría de asistentes

## Preparación

- [x] T006-01 `data/referencia/prompts.csv` con los 22 prompts del plan y la columna `revisado` (es y en revisados; fr, ko y zh pendientes en T006-02). Verificación: 22 filas; es 9, en 4, fr 3, ko 3 y zh 3.
- [ ] T006-02 [P] Revisión de los prompts en fr, ko y zh por alguien que hable el idioma o con traducción de ida y vuelta. Verificación: `revisado=true` en las 9 filas.
- [ ] T006-03 [P] `data/referencia/dominios.csv` con al menos 40 dominios clasificados (gobierno, medio, blog, agencia de viajes, red social, enciclopedia). Verificación: archivo presente.
- [ ] T006-04 `radar/asistentes/proveedores.py` con las dos clases y pruebas simuladas (el extra `asistentes` ya está en `pyproject.toml`). Verificación: `uv run pytest tests/test_proveedores.py`.

## Corrida

- [ ] T006-05 `radar asistentes plan` y `radar asistentes correr`: reanudable, con tope, semilla y JSONL. Verificación: corrida de humo con 2 prompts × 2 proveedores × 1 repetición y su JSONL.
- [ ] T006-06 Corrida en es y en (13 prompts × 2 × 10 = 260). Depende de T006-05. Verificación: 260 líneas válidas en lo crudo.
- [ ] T006-07 Corrida en fr, ko y zh (9 prompts × 2 × 10 = 180). Depende de T006-02 y T006-05. Verificación: 180 líneas.

## Procesamiento

- [ ] T006-08 `radar/asistentes/menciones.py` (términos y extractor) con pruebas por idioma. Depende de T001-05. Verificación: `uv run pytest tests/test_menciones.py`.
- [ ] T006-09 `radar/asistentes/citas.py` y su resumen de dominios. Verificación: `asistentes_citas.csv` con `tipo_dominio` en ≥ 90 % de las filas.
- [ ] T006-10 `radar asistentes procesar`: las cinco tablas curadas con Wilson, incluida `asistentes_ejemplos.csv`. Verificación: `asistentes_visibilidad.csv` tiene los 12 Pueblos Mágicos en el segmento total y hay un ejemplo por idioma.
- [ ] T006-11 Validación manual de 60 respuestas estratificadas por idioma; precisión y exhaustividad anotadas en `docs/ia-responsable.md`. Verificación: métricas registradas; si están bajo la meta, se corrige y se vuelve a procesar.
- [ ] T006-12 Costo real de la corrida a partir de los tokens. Verificación: cifra en `09-resultados.md`.

## P1 y P2

- [ ] T006-13 [P] (P1) Brazo real a partir de T005-09 y comparación con el controlado en español. Verificación: segmento `brazo=real` en la tabla de visibilidad.
- [ ] T006-14 [P] (P1) Brazo sin búsqueda en Gemini (el mismo corpus sin herramienta). Verificación: segmento `con_busqueda=false`.
- [ ] T006-15 [P] (P2) Omisiones y errores por destino (H4). Verificación: tabla `asistentes_afirmaciones.csv` para al menos 3 destinos.
