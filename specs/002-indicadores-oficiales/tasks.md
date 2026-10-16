# Tareas 002 · Indicadores oficiales

- [x] T002-01 Registrar la fuente con su SHA-256 en `data/fuentes/fuentes.csv`. Verificación: `uv run radar fuentes`.
- [x] T002-02 Lector del PDF con corrección de nombres y procedencia. Verificación: `uv run pytest tests/test_indicadores.py`.
- [x] T002-03 Comprobación de acumulados con distinción entre errores y huecos de la fuente. Verificación: `uv run radar indicadores` termina con «Acumulados del PDF: correcto» y lista un hueco.
- [x] T002-04 Recorte de meses no publicados. Verificación: el último periodo es 2026-06.
- [x] T002-05 Tablas mensual y anual, y factor de afluencia en `data/curado/`. Verificación: archivos presentes y versionados.
- [ ] T002-06 Prueba que fije los resultados clave: participación de 2025 (capital 59.9 %, Pueblos Mágicos 28.8 %) y factor 2.222 en Cuetzalan. Verificación: `uv run pytest`.
- [ ] T002-07 [P] (P1) Opción `--fuente` y reporte de diferencias contra la tabla versionada. Verificación: correr dos veces con la misma fuente produce un reporte vacío.
- [x] T002-08 [P] Pregunta a la Secretaría sobre la metodología de afluencia y excursionistas, en `docs/entregables/mentoria.md` § Preguntas. Verificación: pregunta escrita.
