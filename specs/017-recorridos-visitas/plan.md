# Plan 017 · Recorridos y visitas

## Enfoque

El pipeline es una función pura (`procesar(muestras, pois, parametros)`) sin base de datos ni red, para probarlo con trazas en memoria y evaluarlo fuera de la API. La API solo valida, guarda muestras, consulta los POI cercanos de `core` y persiste el resultado: candidatos en `private.visit_candidate` y un resumen sin coordenadas en `private.trip_session.resumen`.

## Archivos

| Archivo | Contenido |
|---|---|
| `app/pipeline/visitas.py` | Tipos (`Muestra`, `POICercano`, `Parametros`, `Candidato`, `Resumen`) y etapas del pipeline |
| `app/pipeline/horario.py` | Intérprete del subconjunto de `opening_hours` del catálogo |
| `app/pipeline/trazas_sinteticas.py` | Generador determinista de trazas y su verdad; comando |
| `app/pipeline/evaluar.py` | Métricas sobre las trazas; escribe `reports/eval_visitas.md` |
| `app/services/recorridos.py` | Consentimiento vigente, POI cercanos, procesar y persistir una sesión, carga de traza de demo |
| `app/api/sesiones.py` | `/sessions*` |
| `app/api/visitas.py` | `/visits/confirm`, `/checkins` y `/me/diario` |
| `app/schemas/recorridos.py` | Esquemas de Pydantic |
| `app/privacy/retencion.py` | Purga de muestras crudas; comando |
| `alembic/versions/0003_recorridos.py` | Columnas nuevas y estado `visita_confirmada` |
| `data/synthetic/` | `trazas_visitas.csv` y `trazas_visitas_verdad.csv` |
| `docs/calibracion_gps.md` | Parámetros, su justificación y lo que falta calibrar |

## Cambios al modelo (migración `0003`)

- `visit_candidate`: estado admite `visita_confirmada`; columnas `duracion_observada_min`, `distancia_m`, `n_muestras`, `alternativas` (JSON: `poi_id` y probabilidad, sin coordenadas), `decision` ∈ `confirmada`, `corregida`, `rechazada` y `decidido_en`.
- `trip_session`: `resumen` (JSON sin coordenadas) y `procesada_en`.
- `confirmed_visit`: `duracion_min`.

## Pipeline

1. **Validación**: coordenadas en rango, no (0, 0), precisión ≤ `precision_max_m`, fecha no futura.
2. **Duplicados**: misma marca de tiempo (se queda la de mejor precisión) o misma posición en menos de 1 s.
3. **Saltos imposibles**: se descarta la muestra cuya velocidad desde la última aceptada supera `velocidad_max_mps` después de restar el ruido combinado `√(p₁² + p₂²)`.
4. **Paradas**: agrupamiento secuencial por radio (`radio_parada_m`) alrededor del centroide ponderado por 1/p²; una parada dura al menos `duracion_minima_min` (de la primera a la última muestra).
5. **Duración observada y huecos**: la suma de intervalos ≤ `hueco_max_min`; los mayores son huecos y bajan la confianza.
6. **Asociación**: para cada POI a ≤ `radio_asociacion_m`, verosimilitud gaussiana `exp(−d²/2σ²)` con `σ² = precisión_centroide² + extensión_poi²`, por un factor de horario (abierto 1, desconocido 0.8, cerrado 0.3); se normaliza con una hipótesis «ningún lugar del catálogo» de peso fijo.
7. **Estado y confianza**: `confianza = probabilidad × (0.7 + 0.3 × cobertura)`. `visita_probable` si la confianza ≥ `umbral_probable`; si no, `desconocido` sin `poi_id` y con alternativas. Los tramos en movimiento que pasan a ≤ `radio_paso_m` de un lugar de interés son `paso_cercano`.
8. **Resumen**: muestras recibidas, válidas y descartadas por motivo; tiempo observado; distancia estimada (con cada parada colapsada a su centroide para no sumar el ruido); huecos.

## Pruebas

- `tests/test_pipeline_visitas.py`: cada etapa con casos mínimos, horario, determinismo del generador y una traza sintética completa.
- `tests/test_recorridos.py`: consentimiento (403), pausa (409), lote máximo (422), flujo completo con la traza de demo, confirmar/corregir/rechazar, check-in, diario, autorización horizontal, ninguna respuesta con coordenadas, registros sin coordenadas, `DELETE /me` y purga por retención.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| POI muy densos en el centro de Puebla (comercios a pocos metros) | Se reporta la tasa de indeterminadas en lugar de forzar una asignación; la persona corrige |
| El ruido sintético es independiente entre muestras y el real está correlacionado | La precisión del centroide tiene un piso de 10 m; se declara en la evaluación y en la calibración |
| Otra spec (019) agrega migraciones en paralelo | Esta es `0003` sobre `0002`; no se tocan `app/api/b2b*` ni `analytics` |
