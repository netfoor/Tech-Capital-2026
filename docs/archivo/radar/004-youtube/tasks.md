# Tareas 004 · YouTube

- [ ] T004-01 `data/referencia/consultas_video.csv` con las consultas genéricas y una específica por destino. Verificación: 4 genéricas (es) y 13 específicas.
- [ ] T004-02 Cliente mínimo con estimación de cuota y guardado de lo crudo. Depende de T001-05 (`detectar`). Verificación: una consulta real guardada en `data/crudo/youtube/`.
- [ ] T004-03 Agregados `presencia_youtube.csv` y `videos_por_destino.csv`, con pruebas sobre la muestra guardada. Verificación: `uv run pytest tests/test_youtube.py`.
- [ ] T004-04 Descarga de comentarios a `data/privado/comentarios/youtube.jsonl` sin datos del autor. Verificación: la prueba de campos prohibidos pasa y hay ≥ 300 comentarios en total.
- [ ] T004-05 Comando `radar senales youtube` y corrida completa. Verificación: tablas en `data/curado/` con `fecha_consulta`.
- [ ] T004-06 [P] (P1) Consultas genéricas en inglés. Verificación: filas con `idioma=en`.
