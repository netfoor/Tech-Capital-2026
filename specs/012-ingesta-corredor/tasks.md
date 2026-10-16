# Tareas 012 · Ingesta y catálogo del corredor

Formato: `[ ]` pendiente, `[~]` en curso, `[x]` hecha. `[P]` = paralelizable con otras tareas de esta spec.

## Fuentes y descarga

- [x] T012-01 Zonas: corredor `puebla-cholula` y círculos de los 12 Pueblos Mágicos; `docs/corredor_piloto.md`. Verificación: `corredores.csv` con una fila y documento con cifras generadas.
- [x] T012-02 `radar corredor descargar`: Overpass con límites, SIC y DENUE masivo; crudo con manifiesto y extractos registrados. Verificación: manifiesto con SHA-256 y `uv run radar fuentes` correcto.

## Integración

- [x] T012-03 Mapeo OSM → categoría y accesibilidad (§06.2). Verificación: `uv run pytest tests/test_corredor_osm.py`.
- [x] T012-04 `radar corredor integrar`: normalización, validación, municipio, enlace difuso < 75 m, deduplicación y salidas con el contrato. Verificación: `uv run pytest tests/test_corredor_integrar.py`.
- [x] T012-05 Oferta DENUE por municipio y SCIAN para 013. Verificación: `oferta_denue_municipio.csv` presente.

## Documentación y calidad

- [x] T012-06 [P] `data/catalog/data_catalog.csv` (§08.4) y `docs/source_cards.md`. Verificación: una fila y una ficha por fuente.
- [x] T012-07 `radar corredor reporte`: `reports/calidad_datos.md` (conteos, nulos, duplicados, matches, cobertura). Verificación: el reporte se regenera igual dos veces.
- [x] T012-08 [P] Borrador de `docs/entregables/06_pipeline_datos.md`. Verificación: describe obtención, limpieza, integración y transformación.
- [x] T012-09 Comandos en `radar/cli.py`, `pipelines/README.md` y receta `datos` del Makefile. Verificación: `uv run radar corredor --help`.
