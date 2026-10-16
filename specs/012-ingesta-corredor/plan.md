# Plan 012 · Ingesta y catálogo del corredor

## Enfoque

Dos etapas separadas. `descargar` es la única que usa red: guarda lo crudo con fecha y huella, y deja extractos pequeños y versionados en `data/fuentes/corredor/`. `integrar` y `reporte` no usan red y regeneran `data/curado/` desde esos extractos, así cualquier clon reproduce el catálogo con `make datos`.

## Zonas de consulta

| Zona | Forma | Qué se pide |
|---|---|---|
| `puebla-cholula` (corredor) | Rectángulo que cubre el Centro Histórico de Puebla, San Andrés y San Pedro Cholula | Turismo, patrimonio, templos, parques y miradores en todo el rectángulo; alimentos, baños, bancas y artesanías solo a 1.2 km de los tres centros |
| Cada Pueblo Mágico | Círculo de 1.5 km alrededor de la cabecera (`destinos.csv`) | Todo lo anterior |

Etiquetas: `tourism=*`, `historic=*`, `amenity=place_of_worship|restaurant|cafe|toilets|bench|marketplace|arts_centre|theatre`, `leisure=park|garden`, `shop=craft|gift|art`, `craft=*` (solo con nombre). Salida `out center meta` para tener la fecha de edición.

## Archivos

| Archivo | Contenido |
|---|---|
| `pipelines/src/radar/geo.py` | Distancia haversine, punto en polígono y carga de los límites de INEGI |
| `pipelines/src/radar/corredor/zonas.py` | Corredor y zonas de Pueblos Mágicos |
| `pipelines/src/radar/corredor/osm.py` | Consulta Overpass, lectura y mapeo a categoría y accesibilidad |
| `pipelines/src/radar/corredor/sic.py` | Lectura de las tablas del SIC |
| `pipelines/src/radar/corredor/denue.py` | Lectura y filtro de la descarga masiva del DENUE |
| `pipelines/src/radar/corredor/descargar.py` | Etapa con red: crudo, manifiesto y extractos |
| `pipelines/src/radar/corredor/integrar.py` | Etapa sin red: integración, deduplicación y escritura |
| `pipelines/src/radar/corredor/calidad.py` | Reporte de calidad y cifras del corredor |
| `data/fuentes/corredor/` | Extractos versionados (respuestas de Overpass y filas de Puebla del SIC y del DENUE) |
| `data/curado/{poi,poi_accesibilidad,corredores,oferta_denue_municipio}.csv` | Salidas |
| `data/catalog/data_catalog.csv` y `docs/source_cards.md` | Inventario de fuentes (§08.4) |
| `reports/calidad_datos.md` | Reporte automático |

## Contrato de salida

`poi.csv`: `poi_id, nombre, categoria, subcategoria, destino_id, corredor_id, municipio_cvegeo, lat, lon, direccion, horario_osm, costo_rango, descripcion, fuentes, osm_id, denue_id, sic_id, match_score, is_synthetic`

- `categoria` ∈ {museo, sitio_historico, templo, zona_arqueologica, mercado, artesanias, parque, mirador, restaurante, cafe, alojamiento, banio, centro_cultural, otro}.
- `costo_rango` ∈ {gratis, bajo, medio, alto, desconocido}. `fuentes` = ids de `data_catalog.csv` separados por `|`. `corredor_id` = `puebla-cholula` o vacío.
- `poi_id` estable: `osm-n123`, `osm-w123`, `osm-r123`, `sic-museo-123` o `denue-123`, según la fuente principal.
- `match_score` 0–1: el mejor puntaje de enlace con otra fuente; vacío si no hubo enlace.

`poi_accesibilidad.csv`: `poi_id, atributo, valor, origen, fecha, confianza, estado, evidencia`

- `atributo` ∈ {acceso_sin_escalones, rampa, banio_accesible, elevador, superficie, asientos, estacionamiento_reservado, pendiente_pct, numero_escalones}.
- `origen` ∈ {osm, sic, denue, equipo, comunidad, prestador}; `estado` ∈ {verificado, sin_verificar, reportado, en_moderacion}.

`corredores.csv`: `corredor_id, nombre, descripcion, lat_min, lon_min, lat_max, lon_max`.

`oferta_denue_municipio.csv` (para 013): `municipio_cvegeo, scian_prefijo, rama, establecimientos, fuente_id`.

## Mapeo de accesibilidad desde OSM

| Etiqueta | Atributo | Valor |
|---|---|---|
| `wheelchair=yes|designated` | `acceso_sin_escalones` (en baños: `banio_accesible`) | `si` |
| `wheelchair=limited` | ídem | `parcial` |
| `wheelchair=no` | ídem | `no` |
| `toilets:wheelchair=yes|no|limited` | `banio_accesible` | `si`, `no`, `parcial` |
| `ramp=*`, `ramp:wheelchair=*` | `rampa` | `si`, `no`, `parcial` |
| `step_count=N` | `numero_escalones` | N |
| `incline=N%` | `pendiente_pct` | N (solo si es número) |
| `surface=*` | `superficie` | valor de OSM |
| `elevator=yes|no` | `elevador` | `si`, `no` |
| `bench=yes|no` | `asientos` | `si`, `no` |
| `capacity:disabled=N`, `parking:disabled=yes` | `estacionamiento_reservado` | `si` si N > 0 |

Todas con `origen=osm`, `estado=sin_verificar`, `confianza=0.6`, `fecha` = última edición del elemento y `evidencia` = `osm:<tipo>/<id> <clave>=<valor>`. Sin etiqueta no hay fila.

## Integración

1. Normalizar nombres (`texto.normalizar`) y descartar prefijos genéricos al comparar («museo», «templo de», «parroquia de»… se conservan en el nombre visible).
2. Validar coordenadas: dentro del contorno estatal de INEGI. Las que no, se descartan y se cuentan.
3. Municipio por punto en polígono; `destino_id` por municipio (`destinos.csv`, Cholula agrupa 21140 y 21119).
4. Enlace: para cada registro del SIC y del DENUE se buscan elementos de OSM a menos de 75 m; puntaje = `rapidfuzz.fuzz.token_set_ratio / 100`; se acepta con ≥ 0.80 y se toma el mejor. Un elemento de OSM se enlaza a lo más con un registro de cada fuente.
5. Deduplicación: dentro de OSM, dos elementos con el mismo nombre normalizado y la misma categoría a menos de 30 m se funden (gana el de menor id de tipo nodo → vía → relación).
6. Orden de salida por `poi_id`; accesibilidad por `poi_id, atributo`.

## Pruebas

- `tests/test_corredor_osm.py`: mapeo de categoría y de accesibilidad (sin etiqueta no hay fila).
- `tests/test_corredor_integrar.py`: integración con respuestas guardadas en `tests/datos/corredor/`; enlace a < 75 m y rechazo a > 75 m; coordenadas fuera de Puebla; determinismo (dos corridas, misma SHA-256); contrato de columnas.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Overpass saturado | Varios servidores públicos, una consulta a la vez, espera creciente; se reanuda por zona |
| DENUE bloqueado o enorme | Descarga masiva por entidad (≈ 37 MB) y filtro local por SCIAN; si falla, se documenta |
| Cobertura de accesibilidad muy baja | Es el hallazgo (§02.3 D): se reporta como cobertura de información, no como accesibilidad |
| SIC con coordenadas imprecisas | Enlace solo a < 75 m; lo no enlazado entra como POI propio con su procedencia |
