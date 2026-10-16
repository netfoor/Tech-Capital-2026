# Spec 004 · YouTube

| | |
|---|---|
| Contexto | Atención digital |
| Prioridad | P1 |
| Estado | Pendiente (llave verificada el 2026-10-15) |
| Depende de | 001 (términos y `detectar`) |
| Habilita | 007 (comentarios) y 008 (componente de video) |

## Bases que atiende

DAT-01, DAT-03 y DAT-05 (API oficial dentro de sus términos), RUB-02 y CAT-DAT (diversidad de fuentes).

## Objetivo

Medir la presencia de cada destino en YouTube de dos formas:
1. qué tanto aparece en las búsquedas genéricas sobre Puebla;
2. cuánta audiencia tienen los videos que aparecen al buscar el destino.

Además, obtener comentarios para la spec 007.

## Historias de usuario

**H1 (P1).** Como analista, quiero saber qué destinos aparecen cuando alguien busca «qué visitar en Puebla» en YouTube.
- Dadas las consultas genéricas del protocolo, cuando corre `radar senales youtube`, entonces se calcula para cada destino la proporción de los primeros 25 resultados que lo mencionan en título o descripción.

**H2 (P1).** Como analista, quiero la audiencia de los videos de cada destino.
- Dada la consulta específica de un destino, cuando se obtienen los 10 primeros videos y sus estadísticas, entonces se publican la mediana y el total de vistas, los comentarios y la antigüedad mediana.

**H3 (P1).** Como responsable de la spec 007, quiero los comentarios más relevantes de los videos principales de cada destino, sin datos de quién los escribió.
- Dados los 3 primeros videos de cada destino, cuando se descargan hasta 100 comentarios por video, entonces se guardan en `data/privado/comentarios/youtube.jsonl` sin nombre de autor ni identificador de canal.

## Requisitos funcionales

- **FR-004-01** Consultas en `data/referencia/consultas_video.csv` (`consulta_id, tipo, texto, idioma, region`):
  - genéricas en español: «qué visitar en Puebla», «pueblos mágicos de Puebla», «fin de semana en Puebla», «sierra norte de Puebla»;
  - genéricas en inglés (P1): «things to do in Puebla Mexico», «Puebla Mexico travel»;
  - una específica por destino: «<destino> Puebla qué hacer».
- **FR-004-02** `search.list` (`type=video`, `regionCode=MX`, `relevanceLanguage` según el idioma, `maxResults` de 25 o 10), `videos.list` (estadísticas) y `commentThreads.list` (`order=relevance`, `textFormat=plainText`).
- **FR-004-03** Detección del destino en título y descripción con `catalogo.detectar`.
- **FR-004-04** Tabla `videos_por_destino.csv` (agregada) y `presencia_youtube.csv` (`destino_id, consulta_id, n_resultados, k_menciones, proporcion`).
- **FR-004-05** Datos crudos en `data/crudo/youtube/` (no versionado); comentarios en `data/privado/` (no versionado).
- **FR-004-06** Control de cuota: estimar unidades antes de correr y abortar si la corrida supera 8,000 unidades.

## Requisitos no funcionales

- Respeta los términos de la API de YouTube: no se publican datos crudos ni comentarios; las métricas agregadas llevan su fecha de consulta y se refrescan si tienen más de 30 días el día de la demostración.

## Fuera de alcance

- Transcripciones de video.
- Análisis de miniaturas.

## Preguntas abiertas

- ¿Se incluye `regionCode=US` en el piloto? Depende de los mercados que priorice la Secretaría para el Tianguis.
