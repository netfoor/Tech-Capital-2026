# Plan 001 · Catálogo de destinos

## Enfoque

El catálogo es un CSV pequeño, revisable a ojo y versionado. Las claves y coordenadas vienen del servicio web de INEGI. Los nombres en otros idiomas se capturan con su origen y se marcan como verificados solo cuando una persona confirmó la escritura con una fuente (Wikipedia en ese idioma, un sitio oficial de turismo o una agencia de viajes del país).

## Archivos

| Archivo | Contenido |
|---|---|
| `data/referencia/destinos.csv` | Semilla con 18 destinos: los 12 Pueblos Mágicos, la capital y 5 ciudades con datos del observatorio |
| `data/referencia/geo/municipios-puebla.geojson` | 217 municipios, propiedades `cvegeo` y `nomgeo`, simplificado al 4 % con mapshaper (`-simplify 4% keep-shapes`) |
| `data/referencia/geo/estado-puebla.geojson` | Contorno estatal (disolución de los municipios) |
| `data/referencia/terminos_idiomas.csv` | `destino_id, idioma, termino, origen, verificado` |
| `data/referencia/trends_temas.csv` | (P1) temas de Trends por destino |
| `pipelines/src/radar/catalogo.py` | Carga, validación, índice por centro y `detectar()` |

## Cómo se obtuvieron los datos de la semilla

1. Claves municipales: `GET https://gaia.inegi.org.mx/wscatgeo/v2/mgem/21` (217 municipios).
2. Cabeceras (nombre, latitud, longitud y altitud): `GET https://gaia.inegi.org.mx/wscatgeo/v2/localidades/{cvegeo_mun}0001`.
3. Geometrías: `GET https://gaia.inegi.org.mx/wscatgeo/v2/geo/mgem/21` (Marco Geoestadístico de diciembre de 2025, 9.7 MB) y luego `npx mapshaper -filter-fields cvegeo,nomgeo -simplify 4% keep-shapes -o precision=0.0001`.
4. Lista de los 12 Pueblos Mágicos: el gobierno estatal confirma el número (12); los nombres se cotejaron con dos guías de viaje que coinciden. Antes de la entrega se confirma en el catálogo federal de Pueblos Mágicos.

## Detección de menciones (`detectar`)

- Alfabeto latino (es, en, fr): se normaliza el texto (`texto.normalizar`), se busca cada término normalizado con límites de palabra y se guarda la posición del primer carácter. Si un término está contenido en otro («Puebla» en «San Pedro Cholula, Puebla»), gana el más largo en esa posición.
- La palabra «Puebla» sola es ambigua (estado o capital). Solo cuenta como el destino `puebla` si va acompañada de «ciudad de», «capital», «centro histórico» o «Puebla city»; si no, se ignora.
- Alfabetos ko y zh: búsqueda de subcadenas exactas de los términos verificados. Lo que no se encuentre lo resuelve el extractor de la spec 006.

## Pruebas

- `tests/test_catalogo.py`: validación, 12 Pueblos Mágicos, Cholula con dos municipios y normalización.
- `tests/test_detectar.py`: casos positivos y negativos por idioma, la regla de «Puebla» sola, orden de aparición y el término más largo.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Transliteraciones incorrectas en ko o zh | Columna `verificado`; solo se usan las verificadas; respaldo con extractor y revisión manual (spec 006) |
| Ambigüedad de «Puebla» | Regla explícita y prueba dedicada |
