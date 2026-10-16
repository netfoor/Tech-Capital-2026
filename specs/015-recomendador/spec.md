# Spec 015 · Recomendador inclusivo

| | |
|---|---|
| Contexto | Inteligencia (recomendación de itinerarios) |
| Prioridad | P0 |
| Estado | MVP implementado y evaluado offline con datos sintéticos; falta repetir la evaluación con el catálogo real de la spec 012 |
| Depende de | 012 (catálogo `poi.csv` y `poi_accesibilidad.csv`), 014 (endpoint que lo consume) |
| Habilita | 016 (planificación en la PWA), escena de valor §06.8 |

## Bases que atiende

- §5: uso de datos abiertos e IA **justificada**: el recomendador combina catálogo multi-fuente con atributos de accesibilidad verificables y se compara contra líneas base.
- §11 (rúbrica): solidez técnica, impacto en inclusión y distribución territorial; la evaluación reporta las cifras con `n`.
- §12 (premio «Mejor uso de IA»): la IA resuelve un problema de optimización con restricciones que una lista ordenada no resuelve, es explicable y se mide.
- §16: declarar qué componente usa IA, su función y sus límites (`docs/ia/model_card_recomendador.md`).
- Contexto maestro: §04.4 (L3 multi-día), §06 (inclusión), §10.1 (caso 1), §15 (reglas de inclusión en datos y evaluación) y §18 (IA: baselines, métricas, ejemplos de fallo).

## Objetivo

Que una persona con tiempo, intereses, presupuesto y necesidades de acceso obtenga un itinerario a pie que **nunca** viole una restricción indispensable, que diga por qué recomienda cada parada, qué no sabe y qué alternativas hay, y que reparta visitas hacia destinos menos saturados sin sacrificar pertinencia.

## Historias de usuario

**H1 (P0).** Como visitante que no puede subir escalones, quiero una ruta de 4 horas solo con lugares cuyo acceso sin escalones esté verificado, para no llegar a una barrera.
- Dado `sin_escalones=true`, cuando pido una ruta, entonces cada parada tiene `acceso_sin_escalones=si` verificado o sin verificar con confianza ≥ 0.6; los lugares sin dato aparecen solo en `alternativos`, marcados «sin verificar», y los que tienen `valor=no` o un reporte de barrera no aparecen.

**H2 (P0).** Como visitante que necesita descansar, quiero descansos cada N minutos y baños accesibles a lo largo de la ruta.
- Dado `descansos_cada_min=30`, entonces ningún tramo continuo de caminata o visita pasa de 30 min sin un descanso.
- Dado `banio_accesible=true`, entonces ningún tramo pasa de 90 min (configurable) sin acceso a un baño accesible confiable.

**H3 (P0).** Como visitante, quiero saber por qué me recomiendan cada lugar y qué datos faltan.
- Cada parada tiene un motivo «Te lo recomendamos porque…»; la respuesta lista los datos desconocidos (horarios sin verificar, costos sin dato, pendiente del trayecto no medida).

**H4 (P0).** Como visitante con lugares guardados, quiero repartirlos en N días agrupados por cercanía y horario.
- Dado un conjunto de guardados y N días, entonces ningún lugar se repite, cada día cabe en sus horas y los que no caben o no cumplen restricciones salen en `no_incluidos` con su motivo.

**H5 (P0).** Como jurado, quiero ver que el recomendador es mejor que una regla simple.
- La evaluación offline compara contra popularidad y cercanía pura con las mismas métricas y el mismo `n`.

## Requisitos funcionales

- **FR-015-01** Paquete puro `backend/app/recommender/` sin base de datos ni FastAPI, con `recomendar(SolicitudRuta, list[POICandidato]) -> RespuestaRuta` y `planear_multidia(SolicitudMultidia, list[POICandidato]) -> RespuestaMultidia`. Los tipos viven en `tipos.py` y son el contrato con la spec 014.
- **FR-015-02** Etapa 1, elegibilidad dura: horario (parser conservador de `opening_hours`), presupuesto, duración y restricciones indispensables (`sin_escalones`, `pendiente_max_pct`, `banio_accesible`, `descansos_cada_min`). Una restricción indispensable nunca se viola.
- **FR-015-03** Etapa 2, ranking multiobjetivo con pesos configurables: pertinencia por intereses (TF-IDF determinista), cercanía, diversidad territorial, calidad de información y esfuerzo.
- **FR-015-04** Etapa 3, secuenciación tipo orienteering con ventanas de tiempo: inserción voraz más 2-opt, tiempos peatonales por haversine × 1.3 a 4.5 km/h, estancias por categoría, descansos y baños accesibles insertados.
- **FR-015-05** Etapa 4, explicación por parada, datos desconocidos y alternativas.
- **FR-015-06** Multi-día: agrupamiento espacial con capacidad (k-means con asignación por arrepentimiento) y secuenciación por día; métricas de distancia contra orden ingenuo, cruces entre días y no asignados con motivo.
- **FR-015-07** Baselines de popularidad y de cercanía pura con la misma secuenciación y sin restricciones inteligentes.
- **FR-015-08** Evaluación offline reproducible `analysis/02_eval_recomendador.py` con 40 perfiles sintéticos rotulados, que escribe `reports/eval_recomendador.md` y `reports/eval_recomendador.csv`.
- **FR-015-09** Model card `docs/ia/model_card_recomendador.md`.

## Requisitos no funcionales

- Determinista: misma entrada, misma salida (semilla fija y desempates por `poi_id`).
- Sin servicios externos ni dependencias pesadas.
- Latencia p95 menor a 1 s por solicitud con un catálogo de hasta 100 POI.

## Fuera de alcance

- Ruteo sobre la red peatonal de OSM (OSMnx); queda como mejora.
- Transporte público o en auto.
- Pendiente de los tramos entre paradas (requiere el modelo de elevación de la spec 012).
- Aprendizaje a partir de retroalimentación de usuarios (no hay datos todavía).

## Preguntas abiertas

- 2026-10-16. `poi.csv` (spec 012) no trae `popularidad` ni `es_destino_alternativo`. Opción conservadora: el cargador los lee si existen como columnas opcionales; si no, marca como polo saturado a `puebla` y `cholula` (boletín estatal citado en §02) con popularidad 0.8, y al resto como destino alternativo con 0.3. La spec 014 debería calcularlos desde datos.
- 2026-10-16. Nombres de atributos de accesibilidad: se usan `acceso_sin_escalones`, `banio_accesible`, `pendiente_pct` y `asientos_descanso`, con alias de OSM (`wheelchair`, `toilets:wheelchair`, `incline`). Confirmar con la spec 012.
- 2026-10-16. Costo desconocido: entra en la ruta con la advertencia «costo sin verificar» y se lista en datos desconocidos. El presupuesto no es una restricción de accesibilidad; si el equipo decide tratarlo como indispensable, el lugar pasaría a `alternativos`.
- 2026-10-16. Sin `dia_semana`, la ventana de horario es la intersección de los días en que abre (conservador) y la advertencia dice qué días cierra.
- 2026-10-16. `wheelchair=limited` no cuenta como «sin escalones»: queda fuera con motivo «acceso limitado».
- 2026-10-16. La zona para medir diversidad es una celda de 500 m; el contrato de `poi.csv` no trae barrio ni colonia.
- 2026-10-16. Compatibilidad con la spec 014 (PR de la API): `tipos.py` es un superconjunto de sus tipos provisionales. Se conservan `recomendar()` y `recomendar_multidia(solicitud, pois, alternativas)` (más el alias directo `planear_multidia`), `AtributoAcceso`, `NoIncluido` (tupla con nombres `poi_id`, `motivo`), `DiaPlan` y el campo `motor`. Los descansos no son paradas propias (el endpoint exige que cada parada sea un POI del catálogo): se suman al traslado de la parada siguiente y se anuncian en sus advertencias; la línea de tiempo completa queda en `metricas`.
- 2026-10-16. En los datos de la spec 014, `estado=reportado` también aparece como «declarado por el prestador». El motor lo trata siempre como barrera (opción conservadora). Conviene separar «declarado» de «barrera reportada» en el modelo de datos.
- 2026-10-16. El motor es solo a pie: desde Cholula, Atlixco no cabe en una ruta de un día; el provisional de 014 suponía vehículo para más de 2 km. Transporte queda fuera de alcance.
