# 6. Procesos de obtención, limpieza, integración, transformación y análisis

Cada etapa lee solo lo que publicaron las anteriores en `data/curado/` y escribe tablas con columnas definidas en [`../dominio/modelo-de-datos.md`](../dominio/modelo-de-datos.md). Los planes detallados están en cada `specs/NNN-*/plan.md`.

| Etapa | Obtención | Limpieza e integración | Transformación y análisis | Salida | Spec |
|---|---|---|---|---|---|
| Catálogo | Semilla de destinos, claves INEGI y términos en cinco idiomas | Verificación de claves contra el Marco Geoestadístico; el estado es el único contorno oficial | Asignación de municipios a destinos | `data/referencia/destinos.csv`, geometrías | [001](../../specs/001-catalogo-destinos/) |
| Indicadores oficiales | PDF mensuales del Observatorio, guardados con huella | Extracción de tablas, unificación de nombres de centros, validación de sumas contra el agregado estatal | Estadía, derrama por visitante, cuartos libres por día y factor de afluencia por centro | `indicadores_oficiales_mensual.csv` y anual | [002](../../specs/002-indicadores-oficiales/) |
| Búsqueda | Consultas a Google Trends en tandas A, B y C con un destino ancla | Reescala entre tandas con el factor del ancla (segundo ancla para volumen bajo) | Interés ajustado mensual por destino | `interes_busqueda_mensual.csv` | [003](../../specs/003-tendencias-busqueda/) |
| Asistentes | Corridas repetidas de un corpus de prompts en OpenAI y Gemini, con semilla fija | Respuesta cruda guardada con huella; detección de menciones con límites de palabra y términos verificados; extractor para coreano y chino | Visibilidad con intervalo de Wilson; dominios citados y su tipo | `asistentes_*.csv` | [006](../../specs/006-auditoria-asistentes/) |
| Radar | Tablas curadas anteriores | Periodo de referencia común; valores faltantes como nulos | Percentiles, índices, brecha, cuadrante, sensibilidad | `radar_destinos.csv`, `radar_referencia.csv` | [008](../../specs/008-radar/) |
| Publicación | `data/curado/` y referencia | Validación de cada JSON contra su esquema; todo o nada | Manifiesto con SHA-256 y descargas | `web/public/datos/`, `web/public/descargas/` | [009](../../specs/009-sitio/) |
| YouTube, comentarios y panel | Pendientes; mismo patrón con datos personales en `data/privado/` | Sin nombres ni texto de comentarios fuera de lo privado | Solo agregados con n mínimo | — | [004](../../specs/004-youtube/), [005](../../specs/005-panel-tiktok/), [007](../../specs/007-comentarios/) |

## Reglas de calidad comunes

- Resultados deterministas: semilla fija, orden estable y formato numérico fijo al escribir.
- Pruebas sin red: usan respuestas guardadas en `pipelines/tests/datos/`.
- Dato faltante = vacío con nota; nunca se imputa.
- `make verificar` corre pruebas, estilo, huellas de fuentes, catálogo y validación de contratos.
