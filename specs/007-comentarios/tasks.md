# Tareas 007 · Clasificación de comentarios

- [x] T007-01 [P] `limpieza.py` con pruebas. Verificación: `uv run pytest tests/test_limpieza.py`.
- [x] T007-02 [P] `prompt_v1.md` con taxonomía, definiciones y ejemplos, más el JSON Schema de salida. Verificación: archivo revisado por el equipo.
- [x] T007-03 Muestra de validación de 120 comentarios etiquetada por dos personas. Depende de T004-04. Verificación: `validacion.csv` con dos columnas de etiqueta y consenso.
- [x] T007-04 `clasificar.py` reanudable con caché. Verificación: corrida sobre la muestra.
- [x] T007-05 `validar.py` y `validacion_clasificador.json` con κ y matriz de confusión. Verificación: κ del clasificador ≥ 0.6 (o se aplica la pregunta abierta de la spec). Parcial: κ 0.31 con una persona y 64 comentarios; no cumple el umbral. Actualización 2026-10-17: v2 con `imagen_destino`, κ 0.72 contra el consenso final (preliminar; ver T007-08).
- [x] T007-06 Clasificación completa y `opinion_agregada.csv` con supresión n < 5. Verificación: prueba de que no hay celdas con n < 5 ni columnas de texto.
- [x] T007-07 Registrar los resultados de validación en `docs/ia-responsable.md` §3. Verificación: cifras anotadas.
- [ ] T007-08 Validar la v2 con una muestra nueva de 60 comentarios no vistos, etiquetada por dos personas (sin etiqueta de IA). Depende de T007-05. Verificación: κ del clasificador ≥ 0.6 contra el consenso humano.
- [ ] T007-09 (P2) Mostrar la opinión agregada en fichas y en la vista Redes cuando T007-08 se cumpla. Verificación: contratos `ficha` y `redes` con `opinion` no nulo.
