# Tareas 007 · Clasificación de comentarios

- [ ] T007-01 [P] `limpieza.py` con pruebas. Verificación: `uv run pytest tests/test_limpieza.py`.
- [ ] T007-02 [P] `prompt_v1.md` con taxonomía, definiciones y ejemplos, más el JSON Schema de salida. Verificación: archivo revisado por el equipo.
- [ ] T007-03 Muestra de validación de 120 comentarios etiquetada por dos personas. Depende de T004-04. Verificación: `validacion.csv` con dos columnas de etiqueta y consenso.
- [ ] T007-04 `clasificar.py` reanudable con caché. Verificación: corrida sobre la muestra.
- [ ] T007-05 `validar.py` y `validacion_clasificador.json` con κ y matriz de confusión. Verificación: κ del clasificador ≥ 0.6 (o se aplica la pregunta abierta de la spec).
- [ ] T007-06 Clasificación completa y `opinion_agregada.csv` con supresión n < 5. Verificación: prueba de que no hay celdas con n < 5 ni columnas de texto.
- [ ] T007-07 Registrar los resultados de validación en `docs/ia-responsable.md` §3. Verificación: cifras anotadas.
