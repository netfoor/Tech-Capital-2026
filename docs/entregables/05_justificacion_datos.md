# Justificación de la selección de datos

| Necesidad | Fuente | Por qué esta |
|---|---|---|
| ¿Dónde se concentra la demanda? | Observatorio Turístico (DataTur), serie mensual 2017–2026 | Es la serie oficial de la Secretaría; distingue lo **medido** (llegadas, ocupación) de lo **derivado** (afluencia, derrama) |
| ¿Qué lugares hay y dónde? | OpenStreetMap, SIC (Secretaría de Cultura) y DENUE (INEGI) | Tienen cobertura nacional, licencias abiertas y campos complementarios: OSM aporta accesibilidad y horarios; el SIC, recintos culturales oficiales; el DENUE, establecimientos con su actividad económica |
| ¿Qué se sabe de su accesibilidad? | Etiquetas `wheelchair` y `toilets:wheelchair` de OSM | Es la única fuente abierta con ese dato; su escasez es el hallazgo central |
| Unidades territoriales | Marco Geoestadístico (INEGI) | Claves oficiales para unir todas las fuentes |

La calidad de cada fuente (nulos, duplicados, enlaces entre fuentes y cobertura) está en [`reports/calidad_datos.md`](../../reports/calidad_datos.md). El inventario completo, con licencia, fecha y sesgos, está en [`data/catalog/data_catalog.csv`](../../data/catalog/data_catalog.csv) y [`docs/source_cards.md`](../source_cards.md).

**Lo que se descartó y por qué:** el Censo por AGEB y el modelo de elevación quedaron pendientes por tiempo. No se hizo scraping de redes sociales porque sería contrario a sus términos.
