# Plan 004 · YouTube

## Dependencias

`uv sync --extra senales` (`httpx`). Llave `YOUTUBE_API_KEY` en `.env`. Se llama al API REST directamente; no hace falta el cliente de Google.

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `radar/senales/youtube.py` | Cliente mínimo (búsqueda, videos y comentarios), conteo de cuota, guardado de lo crudo y agregados |
| `data/referencia/consultas_video.csv` | Consultas del protocolo |

## Cuota estimada por corrida

| Llamada | Unidades | Veces | Total |
|---|---|---|---|
| `search.list` genéricas (es) | 100 | 4 | 400 |
| `search.list` específicas (13 destinos) | 100 | 13 | 1,300 |
| `videos.list` (hasta 50 ids por llamada) | 1 | ~6 | 6 |
| `commentThreads.list` (3 videos × 13 destinos) | 1 | 39 | 39 |
| **Total** | | | **~1,750** de 10,000 diarias |

## Algoritmo

1. Leer las consultas y estimar la cuota; abortar si supera 8,000 unidades.
2. Para cada consulta, `search.list` y guardar lo crudo (`yt-<consulta_id>-<AAAAMMDD>.json`).
3. Juntar los `videoId` y pedir `videos.list?part=statistics,snippet` en bloques de 50.
4. Detectar el destino en el título y la descripción de cada video.
5. Consultas genéricas: proporción de resultados que mencionan cada destino → `presencia_youtube.csv`.
6. Consultas específicas: de los 10 primeros, conservar solo los que mencionan el destino y calcular la mediana y el total de vistas, los comentarios y la antigüedad → `videos_por_destino.csv`.
7. Comentarios: para los 3 videos con más vistas de cada destino, `commentThreads.list?maxResults=100&order=relevance`. Se guardan solo el `video_id`, el `destino_id`, el texto, los me gusta y la fecha. **No se guardan autor ni canal.**

## Pruebas

- Detección y agregación con respuestas guardadas en `tests/datos/youtube_muestra.json`.
- Una prueba comprueba que el JSONL de comentarios no tenga los campos `author*` ni `channelId`.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Cuota agotada | Estimación previa y lo crudo guardado para no repetir llamadas |
| Videos que no son del destino (homónimos) | Solo cuentan los que mencionan el destino en título o descripción |
