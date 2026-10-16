# Modelo de datos

Entidades de §13.2 del contexto maestro, el esquema de PostgreSQL donde vive cada una y sus invariantes. Las entidades conservan su nombre en inglés; las columnas van en español. El código está en `backend/app/models/` y la migración en `backend/alembic/versions/`.

## Esquemas

| Esquema | Qué guarda | Quién lo lee |
|---|---|---|
| `core` | Catálogo territorial y procedencia | Todas las respuestas públicas |
| `private` | Datos personales, guardados, reseñas, reportes, itinerarios y trayectorias | Solo la persona dueña y la moderación; nunca una respuesta pública |
| `analytics` | Agregados protegidos con `n` y supresión | Tablero (spec 019) y MCP (spec 021) |
| `audit` | Bitácora de acciones y casos de moderación | Analistas y administración |

`core` nunca apunta a `private`. `private` sí apunta a `core` (un guardado apunta a su POI).

## core

| Entidad (tabla) | Llave | Columnas principales |
|---|---|---|
| Destination (`destination`) | `destino_id` | `nombre`, `tipo`, `pueblo_magico`, `municipios_cvegeo`, `cabecera_cvegeo`, `zona`, `centro_ot`, `altitud_m`, `geom` (Point 4326), `is_synthetic` |
| Corridor (`corridor`) | `corredor_id` | `nombre`, `descripcion`, `lat_min`, `lon_min`, `lat_max`, `lon_max`, `geom` (Polygon 4326), `is_synthetic` |
| PointOfInterest (`point_of_interest`) | `poi_id` | `nombre`, `categoria`, `subcategoria`, `destino_id`, `corredor_id`, `municipio_cvegeo`, `geom` (Point 4326), `direccion`, `horario_osm`, `costo_rango`, `descripcion`, `fuentes` (lista de `fuente_id`), `osm_id`, `denue_id`, `sic_id`, `match_score`, `is_synthetic` |
| POIAccessibilityAttribute (`poi_accessibility_attribute`) | `id`; único (`poi_id`, `atributo`) | `atributo`, `valor`, `origen`, `fecha`, `alcance`, `confianza`, `estado`, `evidencia`, `actualizado_en`, `is_synthetic` |
| AccessibilityEvidence (`accessibility_evidence`) | `id` | `attribute_id`, `poi_id`, `atributo`, `valor`, `origen`, `fecha`, `confianza`, `descripcion`, `referencia` (p. ej. `moderation_case:7`), `is_synthetic` |
| OpeningHours (`opening_hours`) | `id` | `poi_id`, `dia_semana` (0 = lunes), `abre`, `cierra`, `texto_osm`, `origen`, `fecha`, `is_synthetic` |
| Provider (`provider`) | `id` | `nombre`, `tipo`, `poi_id`, `denue_id`, `is_synthetic` |
| DataSource (`data_source`) | `fuente_id` | `nombre`, `institucion`, `tipo`, `url`, `licencia`, `fecha_consulta`, `sha256` |
| DataLineage (`data_lineage`) | `id` | `entidad`, `entidad_id`, `fuente_id`, `campo`, `metodo`, `fecha` |
| MetricDefinition (`metric_definition`) | `metric_id` | `nombre`, `descripcion`, `formula`, `version_formula`, `unidad`, `denominador`, `procedencia`, `fuente_id`, `k_minimo` |

Valores controlados:

- `atributo` ∈ `acceso_sin_escalones`, `rampa`, `banio_accesible`, `elevador`, `superficie`, `asientos`, `estacionamiento_reservado`, `pendiente_pct`, `numero_escalones`.
- `estado` ∈ `verificado`, `sin_verificar`, `reportado`, `en_moderacion`.
- `costo_rango` ∈ `gratis`, `bajo`, `medio`, `alto` o nulo.
- `confianza` y `match_score` entre 0 y 1.

## private

| Entidad (tabla) | Columnas principales |
|---|---|
| User (`user_account`) | `id` (UUID), `correo` (único, en minúsculas), `hash_contrasena` (argon2), `rol` ∈ `visitante`, `viewer`, `analista`, `admin`, `nombre_visible`, `creado_en`, `is_synthetic` |
| ConsentGrant (`consent_grant`) | `user_id`, `finalidad` ∈ `ubicacion_sesion`, `resenas`, `fotos`, `analitica_agregada`, `version`, `otorgado`, `fecha`, `revocado_en` |
| PrivacyPreference (`privacy_preference`) | `user_id` (único), `perfil_publico`, `precision_publicacion` ∈ `lugar`, `zona`, `retencion_dias` |
| UserAccessibilityPreference (`user_accessibility_preference`) | `user_id` (único), `sin_escalones`, `banio_accesible`, `descansos_cada_min`, `pendiente_max_pct` |
| TripSession (`trip_session`) | `user_id`, `consent_id`, `version_consentimiento`, `estado` ∈ `activa`, `pausada`, `detenida`, `inicio`, `fin`, `is_synthetic` |
| LocationSample (`location_sample`) | `session_id`, `ts`, `geom` (Point 4326), `precision_m`, `version_consentimiento`, `is_synthetic` |
| VisitCandidate (`visit_candidate`) | `session_id`, `poi_id`, `inicio`, `fin`, `duracion_min`, `estado` ∈ `visita_probable`, `paso_cercano`, `desconocido`, `fuente_evidencia`, `precision_m`, `confianza`, `confirmada`, `is_synthetic` |
| ConfirmedVisit (`confirmed_visit`) | `user_id`, `poi_id`, `candidate_id`, `fecha`, `fuente_evidencia` ∈ `gps_confirmado`, `check_in`, `manual`, `precision_m`, `confianza`, `confirmada`, `is_synthetic` |
| CheckIn (`check_in`) | `user_id`, `poi_id`, `fecha`, `nota`, `is_synthetic` |
| Review (`review`) | `user_id`, `poi_id`, `texto`, `publica` (falso por omisión), `creado_en`, `is_synthetic` |
| ReviewDimension (`review_dimension`) | `review_id`, `dimension` ∈ `accesibilidad`, `limpieza`, `servicio`, `precio_percibido`, `senalizacion`, `comodidad`, `inclusion`, `global`, `puntaje` 1–5 |
| CommunityReport (`community_report`) | `user_id`, `poi_id`, `tipo` ∈ `escalones`, `rampa_bloqueada`, `sin_banio_accesible`, `superficie`, `senalizacion`, `otro`, `descripcion`, `media_asset_id`, `estado` ∈ `en_moderacion`, `aceptado`, `rechazado`, `creado_en`, `is_synthetic` |
| MediaAsset (`media_asset`) | `user_id`, `ruta`, `tipo_mime`, `bytes`, `texto_alternativo`, `sin_exif` (siempre verdadero), `creado_en`, `is_synthetic` |
| SavedPlace (`saved_place`) | `user_id`, `poi_id` o `nombre_propio`, `nota`, `url_origen`, `plataforma_origen`, `creado_en`, `is_synthetic` |
| PlaceList (`place_list`) | `user_id`, `nombre`, `etiquetas`, `creado_en` |
| PlaceListItem (`place_list_item`) | `list_id`, `saved_place_id`, `orden`; único (`list_id`, `saved_place_id`) |
| Itinerary (`itinerary`) | `user_id` (opcional), `modo` ∈ `recomendado`, `desde_guardados`, `solicitud` (JSON sin punto de partida), `explicacion`, `motor`, `creado_en`, `is_synthetic` |
| ItineraryDay (`itinerary_day`) | `itinerary_id`, `dia` |
| ItineraryStop (`itinerary_stop`) | `day_id`, `orden`, `poi_id`, `llegada_min`, `estancia_min`, `traslado_min`, `motivo`, `advertencias` |
| Recommendation (`recommendation`) | `itinerary_id`, `poi_id`, `incluido`, `alternativo`, `motivo` |
| RecommendationFeedback (`recommendation_feedback`) | `recommendation_id`, `user_id`, `util`, `comentario`, `creado_en` |

Todas las tablas de `private` que dependen de una persona usan `ON DELETE CASCADE` desde `user_account`: `DELETE /me` borra todo.

## analytics

| Entidad (tabla) | Columnas principales |
|---|---|
| AggregateMetric (`aggregate_metric`) | `metric_id`, `destino_id`, `corredor_id`, `centro_ot`, `nivel`, `periodo`, `valor`, `n`, `suprimido`, `procedencia` ∈ `medido`, `derivado`, `version_formula`, `calculado_en`, `fuente_id`, `is_synthetic`; único (`metric_id`, `centro_ot`, `nivel`, `periodo`) |

## audit

| Entidad (tabla) | Columnas principales |
|---|---|
| AuditEvent (`audit_event`) | `ts`, `actor_id` (UUID seudónimo, sin llave foránea), `accion`, `entidad`, `entidad_id`, `detalle` (JSON sin coordenadas) |
| ModerationCase (`moderation_case`) | `community_report_id` (`ON DELETE SET NULL`), `poi_id`, `tipo`, `atributo`, `estado` ∈ `abierto`, `aceptado`, `rechazado`, `decision`, `nota`, `decidido_por`, `decidido_en`, `creado_en`, `is_synthetic` |

## Invariantes (§13.2)

| Invariante | Cómo se cumple |
|---|---|
| Toda visita guarda fuente de evidencia, precisión, confianza y si fue confirmada | `visit_candidate` y `confirmed_visit`: `fuente_evidencia`, `confianza` y `confirmada` `NOT NULL`; `precision_m` `NOT NULL` en el candidato y obligatoria en la visita salvo `fuente_evidencia` ∈ `check_in`, `manual` (restricción `CHECK`); `confianza` entre 0 y 1 |
| Todo atributo de accesibilidad guarda fuente, fecha, alcance y estado | `origen`, `fecha`, `alcance` y `estado` `NOT NULL`; `CHECK` sobre `atributo`, `estado` y `confianza` |
| Toda métrica guarda versión de fórmula y fecha de cálculo | `aggregate_metric.version_formula` y `calculado_en` `NOT NULL`; `metric_definition.version_formula` `NOT NULL` |
| Perfiles públicos sin referencias a `LocationSample` | Ninguna tabla fuera de `private` apunta a `location_sample`; las respuestas públicas no consultan `private` (prueba en `tests/test_privacidad.py`) |
| Toda fila sintética con `is_synthetic = true` | Columna `is_synthetic` `NOT NULL` en toda tabla que puede recibir datos sintéticos |
| Una restricción indispensable nunca se viola | El recomendador descarta un lugar si el dato de la restricción falta o no la cumple |

## Contrato de datos de la spec 012

La semilla (`uv run python -m app.services.semilla`) lee estos archivos. Si falta una columna, falla con un mensaje claro.

| Archivo | Columnas |
|---|---|
| `data/curado/poi.csv` | `poi_id, nombre, categoria, subcategoria, destino_id, corredor_id, municipio_cvegeo, lat, lon, direccion, horario_osm, costo_rango, descripcion, fuentes, osm_id, denue_id, sic_id, match_score, is_synthetic` |
| `data/curado/poi_accesibilidad.csv` | `poi_id, atributo, valor, origen, fecha, confianza, estado, evidencia` |
| `data/curado/corredores.csv` | `corredor_id, nombre, descripcion, lat_min, lon_min, lat_max, lon_max` |
| `data/referencia/destinos.csv` | Catálogo de destinos (spec 001) |
| `data/fuentes/fuentes.csv` | Registro de fuentes → `DataSource` |
| `data/curado/indicadores_oficiales_mensual.csv` | Serie hotelera (spec 002) → `MetricDefinition` y `AggregateMetric` |

- `fuentes` en `poi.csv`: identificadores de `fuentes.csv` separados por `|` o `;`.
- La semilla es idempotente y no sobrescribe atributos con `origen = comunidad` (vienen de moderación).
