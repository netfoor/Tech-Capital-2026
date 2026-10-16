# Spec 012 · Ingesta y catálogo del corredor

| | |
|---|---|
| Contexto | Catálogo territorial: puntos de interés (POI) y su accesibilidad |
| Prioridad | P0 |
| Estado | Hecha: catálogo, accesibilidad declarada, inventario de fuentes y reporte de calidad |
| Depende de | 001 |
| Habilita | 013 (análisis del problema), 014 (API y modelo), 015 (recomendador), 016 (PWA), 018 (barreras) |

## Bases que atiende

- §5 de la convocatoria: proponer, obtener, documentar y justificar los datos; explicar su preparación y procesamiento; respetar licencias, términos y privacidad.
- §9.4 (inventario y documentación de fuentes), §9.5 (justificación de datos) y §9.6 (obtención, limpieza, integración y transformación).
- Contexto maestro: §02.3 B y D, §06.2, §08 y §13.2 (`Corridor`, `PointOfInterest`, `POIAccessibilityAttribute`, `DataSource`).

## Objetivo

Un catálogo único y reproducible de lugares del corredor piloto «Centro Histórico de Puebla → San Pedro/San Andrés Cholula» y de los centros de los 12 Pueblos Mágicos, integrado desde fuentes abiertas (OpenStreetMap, Sistema de Información Cultural y DENUE), con los atributos de accesibilidad que esas fuentes declaran y con su procedencia. La ausencia de un dato de accesibilidad queda como «sin verificar», nunca como «accesible» (constitución, XIII).

## Historias de usuario

**H1 (P0).** Como recomendador (spec 015), quiero una tabla de POI con categoría, ubicación, horario, costo y destino para armar itinerarios.
- Dado `data/curado/poi.csv`, cuando se carga, entonces cada fila tiene `poi_id` único, coordenadas dentro de Puebla, `categoria` del vocabulario cerrado y `destino_id` del catálogo.

**H2 (P0).** Como visitante con una necesidad de movilidad, quiero saber qué se sabe y qué no se sabe de la accesibilidad de cada lugar.
- Dado un POI con `wheelchair=yes` en OSM, cuando se integra, entonces aparece `acceso_sin_escalones=si` con `estado=sin_verificar`, `origen=osm` y `confianza=0.6`.
- Dado un POI sin etiqueta, cuando se integra, entonces no tiene fila de ese atributo.

**H3 (P0).** Como analista (spec 013), quiero la cobertura de información de accesibilidad y la oferta por municipio para medir la brecha.
- Dado `reports/calidad_datos.md`, cuando se regenera, entonces muestra conteos, nulos, duplicados, matches y el % de POI con algún atributo de accesibilidad.

**H4 (P0).** Como jurado, quiero ver de dónde sale cada dato, con licencia, fecha y limitaciones.
- Dado `data/catalog/data_catalog.csv`, cuando se revisa, entonces hay una fila por fuente con las columnas de §08.4 y una ficha en `docs/source_cards.md`.

## Requisitos funcionales

- **FR-012-01** `radar corredor descargar` (con red): consulta Overpass por zona respetando sus límites (una consulta a la vez, pausa y reintentos con espera creciente), descarga las tablas del SIC y la descarga masiva del DENUE de la entidad 21. Guarda lo crudo en `data/crudo/corredor/AAAA-MM-DD/` con un manifiesto (URL, fecha y SHA-256) y escribe extractos pequeños en `data/fuentes/corredor/`, registrados en `data/fuentes/fuentes.csv`.
- **FR-012-02** `radar corredor integrar` (sin red): lee los extractos versionados, normaliza, valida coordenadas dentro del estado, asigna municipio por punto en polígono, integra OSM–SIC–DENUE por nombre difuso y distancia menor de 75 m, deduplica y escribe `poi.csv`, `poi_accesibilidad.csv`, `corredores.csv` y `oferta_denue_municipio.csv` en `data/curado/`.
- **FR-012-03** Contrato de salida fijo (nombres y orden de columnas) de `poi.csv`, `poi_accesibilidad.csv` y `corredores.csv`, descrito en `plan.md`.
- **FR-012-04** Mapeo OSM → accesibilidad de §06.2 sin inferencias: solo se crean filas a partir de etiquetas presentes.
- **FR-012-05** `radar corredor reporte` (sin red): escribe `reports/calidad_datos.md` y la tabla de cifras de `docs/corredor_piloto.md`.
- **FR-012-06** `data/catalog/data_catalog.csv` con las columnas de §08.4 y `docs/source_cards.md`.
- **FR-012-07** `docs/corredor_piloto.md` justifica el corredor con datos y `docs/entregables/06_pipeline_datos.md` describe el pipeline.

## Requisitos no funcionales

- Determinista: mismo insumo, mismos archivos (orden estable de filas y columnas, `float_format="%.4f"`).
- Las pruebas no usan red; usan respuestas guardadas en `pipelines/tests/datos/`.
- Atribución «© OpenStreetMap contributors» (ODbL 1.0) y crédito del SIC en las fichas y en la documentación.
- Nada sintético en esta spec: `is_synthetic=false` en todas las filas.

## Fuera de alcance

- Red peatonal, pendiente desde un modelo de elevación y ruteo (013 o 015).
- Carga a PostGIS (014): esta spec entrega CSV.
- Censo por AGEB (P1).

## Preguntas abiertas

- 2026-10-16. No hay `INEGI_DENUE_TOKEN`. Se usa la descarga masiva por entidad (sin token) y se filtra a SCIAN 7211, 7225, 7121 y 5615. Si INEGI la bloquea, se documenta y se sigue con OSM y SIC.
- 2026-10-16. DENUE trae miles de restaurantes en el corredor. Para no inundar el catálogo, los establecimientos de DENUE solo de alimentos (7225) y agencias (5615) se usan para enlazar con OSM y para conteos por municipio; entran como POI propio solo los de alojamiento (7211) y museos o sitios históricos (7121). Opción conservadora; se revisa con el recomendador.
- 2026-10-16. `costo_rango` solo sale de la etiqueta `fee` de OSM (`fee=no` → `gratis`); todo lo demás queda `desconocido`. No se infiere el costo por categoría.
- 2026-10-16. Las bancas de OSM se cuentan en el reporte, pero no entran como POI. Usarlas para el atributo `asientos` cercano es una inferencia que corresponde a 015.
- 2026-10-16. Los límites municipales están simplificados al 4 %; un punto a pocos metros de un límite puede quedar en el municipio vecino.
- 2026-10-16. `lat` y `lon` se escriben con 6 decimales (≈ 0.1 m) y no con `%.4f` (≈ 11 m), que no alcanza para enlazar a 75 m ni para detectar paradas. Sigue siendo determinista.
- 2026-10-16. El SIC sugiere un formato de crédito, pero no encontramos una licencia formal publicada en su portal: queda «NO VERIFICADO» en el catálogo de fuentes.
- 2026-10-16. Para no versionar datos de contacto, los extractos quitan teléfono, correo y redes (SIC), teléfono, correo, sitio web y razón social (DENUE), y usuario y conjunto de cambios (OSM). El original completo queda en `data/crudo/` con su SHA-256 en el manifiesto.
- 2026-10-16. El DENUE completo de Puebla filtrado a las cuatro ramas pesa ≈ 11 MB; se versionan un extracto estatal compacto (para conteos) y uno detallado solo de las zonas (para POI).
- 2026-10-16. Overpass estuvo saturado durante la descarga; se usó también el servidor público de mail.ru (mismo software y datos de OSM). La URL usada queda en el manifiesto.
