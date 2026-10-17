# Tareas 006 · Auditoría de asistentes

## Preparación

- [x] T006-01 `data/referencia/prompts.csv` con los 22 prompts del plan y la columna `revisado` (es y en revisados; fr, ko y zh pendientes en T006-02). Verificación: 22 filas; es 9, en 4, fr 3, ko 3 y zh 3.
- [x] T006-02 [P] Revisión de los prompts en fr, ko y zh por alguien que hable el idioma o con traducción de ida y vuelta. Verificación: `revisado=true` en las 9 filas.
- [x] T006-03 [P] `data/referencia/dominios.csv` con al menos 40 dominios clasificados (gobierno, medio, blog, agencia de viajes, red social, enciclopedia). Verificación: archivo presente.
- [x] T006-04 `radar/asistentes/proveedores.py` con las dos clases y pruebas simuladas (el extra `asistentes` ya está en `pyproject.toml`). Verificación: `uv run pytest tests/test_proveedores.py`.

## Corrida

- [x] T006-05 `radar asistentes plan` y `radar asistentes correr`: reanudable, con tope, semilla y JSONL. Verificación: corrida de humo con 2 prompts × 2 proveedores × 1 repetición y su JSONL.
- [x] T006-06 Corrida en es y en (13 prompts × 2 × 10 = 260). Depende de T006-05. Verificación: 260 líneas válidas en lo crudo.
- [x] T006-07 Corrida en fr, ko y zh (9 prompts × 2 × 10 = 180). Depende de T006-02 y T006-05. Verificación: 180 líneas.

> 2026-10-16 · T006-07 completa: OpenAI hizo sus 60 corridas pendientes en fr, ko y zh (440 líneas en total). Tokens de OpenAI: 1 492 061 de entrada y 227 178 de salida en este lote.

## Procesamiento

- [x] T006-08 `radar/asistentes/menciones.py` (términos y extractor) con pruebas por idioma. Depende de T001-05. Verificación: `uv run pytest tests/test_menciones.py`.
- [x] T006-09 `radar/asistentes/citas.py` y su resumen de dominios. Verificación: `asistentes_citas.csv` con `tipo_dominio` en ≥ 90 % de las filas.
- [x] T006-10 `radar asistentes procesar`: las cinco tablas curadas con Wilson, incluida `asistentes_ejemplos.csv`. Verificación: `asistentes_visibilidad.csv` tiene los 12 Pueblos Mágicos en el segmento total y hay un ejemplo por idioma.
- [x] T006-11 Validación manual de 60 respuestas estratificadas por idioma; precisión y exhaustividad anotadas en `docs/ia-responsable.md`. Verificación: métricas registradas; si están bajo la meta, se corrige y se vuelve a procesar.
- [~] T006-12 Costo real de la corrida a partir de los tokens. Verificación: cifra en `09-resultados.md`.

## P1 y P2

- [ ] T006-13 [P] (P1) Brazo real a partir de T005-09 y comparación con el controlado en español. Verificación: segmento `brazo=real` en la tabla de visibilidad.
- [ ] T006-14 [P] (P1) Brazo sin búsqueda en Gemini (el mismo corpus sin herramienta). Verificación: segmento `con_busqueda=false`.
- [ ] T006-15 [P] (P2) Omisiones y errores por destino (H4). Verificación: tabla `asistentes_afirmaciones.csv` para al menos 3 destinos.

> 2026-10-16 · T006-02: los nueve prompts fr, ko y zh se revisaron con traducción de ida y vuelta al español (sentido y registro equivalentes al original). Una persona que hable el idioma debería confirmarlos antes de la corrida; si cambia alguno, se actualiza `prompts.csv` y se anota la versión.

> 2026-10-16 · Estado de las corridas: 380 de 440. Se completaron es y en (260 líneas, T006-06). En fr, ko y zh hay 120 de 180: Gemini terminó sus 90 y OpenAI hizo 30 de 90 porque se acabó su saldo (`credit_balance_exhausted`). Al recargar: `uv run radar asistentes correr --proveedor openai --idioma fr --idioma ko --idioma zh` retoma solo lo pendiente, y luego `uv run radar asistentes extraer` y `uv run radar asistentes procesar`. Las cifras del sitio y de los documentos salen de las tablas, así que se actualizan al reprocesar.
> 2026-10-16 · Hallazgo: con `google_search` habilitado, Gemini buscó en solo 0.9 % de las corridas; su visibilidad refleja sobre todo el conocimiento del modelo. OpenAI buscó en 94 %. Por eso el sitio debe mostrar los proveedores por separado y la tasa de búsqueda.
> 2026-10-16 · Menciones de la capital: «Puebla» sola es ambigua. Se agregaron expresiones que nombran la ciudad en es, en y fr (`destinos.csv` y `terminos_idiomas.csv`) y, para ko y zh, un extractor con Gemini cuyo resultado queda en caché. La validación manual (T006-11) mide la precisión.
- [ ] T006-16 Distinguir la Ciudad de Puebla como punto de salida o referencia de distancia de la Ciudad de Puebla como destino recomendado. Depende de T006-11. Verificación: las 29 filas de la muestra con este caso quedan bien clasificadas.
- [ ] T006-17 Excluir «Reserva Tehuacán-Cuicatlán» de la detección de Tehuacán. Verificación: las 6 filas de la muestra dejan de contar Tehuacán.
- [ ] T006-18 (P2) Marcar si la mención es recomendación, referencia de ruta o mención negativa (saturado, «a evitar»). Verificación: precisión ≥ 0.9 en la muestra de T006-11.
