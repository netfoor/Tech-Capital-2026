# Obtención, limpieza, integración y transformación de los datos

> Borrador (spec 012). Entregable 9.6 de la convocatoria. Las cifras están en [`reports/calidad_datos.md`](../../reports/calidad_datos.md), que se genera desde los datos; este documento describe el proceso.

## Resumen

Un solo catálogo de lugares (POI) del corredor Puebla–Cholula y de los centros de los 12 Pueblos Mágicos, armado con tres fuentes abiertas que se complementan: OpenStreetMap (lugares y accesibilidad declarada), el Sistema de Información Cultural (recintos culturales oficiales) y el DENUE de INEGI (oferta formal de alojamiento, alimentos y museos). Todo se regenera con dos comandos y cada fila dice de qué fuente viene.

```
descarga (con red)          extractos versionados          integración (sin red)          salidas
Overpass ─┐                 data/fuentes/corredor/osm/      normalizar → validar →          data/curado/poi.csv
SIC ──────┼─► data/crudo/ ─► data/fuentes/corredor/sic/  ─► ubicar → enlazar →        ─►   data/curado/poi_accesibilidad.csv
DENUE ────┘   (fecha+SHA)   data/fuentes/corredor/denue/    deduplicar → escribir           data/curado/corredores.csv
                            (manifiesto con SHA-256)                                         data/curado/oferta_denue_municipio.csv
                                                                                             reports/calidad_datos.md
```

## 1. Obtención

| Fuente | Cómo | Respeto a términos |
|---|---|---|
| OpenStreetMap | Overpass API: una consulta por zona (corredor y cada Pueblo Mágico), etiquetas turísticas y de accesibilidad | Uso justo: una consulta a la vez, pausa entre zonas, espera creciente ante saturación, agente identificado; atribución ODbL |
| SIC | Directorios abiertos en CSV del portal de datos del SIC | Descarga pública; crédito sugerido por el SIC |
| DENUE | Descarga masiva por entidad (Puebla, sin token) | Términos de Libre Uso del INEGI; no se elude ningún control |

- Comando: `uv run radar corredor descargar` (en `pipelines/`).
- Lo crudo se guarda en `data/crudo/corredor/AAAA-MM-DD/` (no se versiona) con la consulta exacta.
- De cada fuente se escribe un extracto pequeño en `data/fuentes/corredor/<fuente>/` y un `manifiesto.csv` con URL, fecha de consulta, SHA-256 del extracto y SHA-256 del original. El manifiesto se registra en `data/fuentes/fuentes.csv`, y `uv run radar fuentes` comprueba su huella.

## 2. Limpieza

- **Privacidad desde el extracto:** OSM sin usuario ni conjunto de cambios; SIC sin teléfono, correo ni redes; DENUE sin teléfono, correo, sitio web ni razón social.
- **Codificación:** todo a UTF-8 (el DENUE viene en Latin-1).
- **Nombres:** se quitan etiquetas HTML del SIC; los nombres del DENUE pasan de mayúsculas a tipo título. Para comparar se usa una forma normalizada (sin acentos, minúsculas, sin puntuación y sin palabras genéricas como «museo», «templo» o «hotel»).
- **Coordenadas:** se descartan las ausentes y las que caen fuera del contorno estatal de INEGI.
- **Categorías:** cada etiqueta de OSM, tabla del SIC o código SCIAN se traduce a un vocabulario cerrado de 14 categorías. Lo que no encaja (por ejemplo, tableros informativos) o no tiene nombre (salvo sanitarios) no entra. Las bancas se cuentan pero no son POI.

## 3. Integración

1. **Ubicación:** municipio por punto en polígono (Marco Geoestadístico) y destino del catálogo (`destinos.csv`). En el corredor solo entran los municipios de Puebla, San Andrés y San Pedro Cholula.
2. **Enlace entre fuentes:** un registro del SIC o del DENUE se enlaza con un POI si está a menos de 75 m, la categoría es compatible y la similitud de nombre (`rapidfuzz`) es de al menos 0.80. Se asigna primero el par con mejor puntaje; cada POI recibe a lo más un registro de cada fuente. El puntaje queda en `match_score`.
3. **Registros sin par:** los recintos del SIC y los hoteles y museos del DENUE sin par en OSM entran como POI propio. Los establecimientos de alimentos y las agencias del DENUE solo se enlazan y se cuentan.
4. **Duplicados:** dentro de OSM se funden los elementos con el mismo nombre y categoría a menos de 30 m (por ejemplo, el nodo y el contorno de un mismo templo); las etiquetas se combinan.

## 4. Transformación

- **Accesibilidad:** cada etiqueta de OSM presente se convierte en una fila de `poi_accesibilidad.csv` con origen, fecha de la edición, confianza (0.6), estado `sin_verificar` y la etiqueta original como evidencia. Sin etiqueta no hay fila: la falta de dato se muestra como «sin verificar», nunca como «accesible» (constitución, XIII).
- **Costo:** solo desde `fee` de OSM (`fee=no` → gratis); lo demás queda «desconocido». No se infiere por categoría.
- **Oferta por municipio:** conteo de establecimientos del DENUE por municipio y rama SCIAN (`oferta_denue_municipio.csv`), insumo del análisis de concentración de la oferta (spec 013).
- **Determinismo:** orden estable por `poi_id`, coordenadas con 6 decimales y `float_format="%.4f"` en lo demás; dos corridas con los mismos extractos producen los mismos archivos (prueba automática).

## 5. Calidad

`uv run radar corredor reporte` escribe `reports/calidad_datos.md`: conteos por fuente, POI por categoría y zona, nulos por columna, duplicados, enlaces y cobertura de información de accesibilidad por zona. También actualiza las cifras de [`docs/corredor_piloto.md`](../corredor_piloto.md).

## 6. Cómo reproducirlo

```bash
cd pipelines
uv run radar corredor descargar   # con red; opcional, los extractos ya están versionados
uv run radar corredor integrar    # sin red
uv run radar corredor reporte     # sin red
uv run pytest -q                  # pruebas con respuestas guardadas, sin red
```

## Pendiente

- Auditoría presencial del equipo en 8 a 15 POI del corredor (fuente «verificado por equipo»).
- Pendiente del entorno con un modelo de elevación y red peatonal (specs 013 y 015).
- Carga a PostGIS (spec 014) y tabla de linaje `data_lineage`.
