# Plan 014 · API y modelo de datos

## Enfoque

Monolito modular en `backend/` (§12). Los modelos viven en `app/models/` por esquema; los esquemas de Pydantic en `app/schemas/`; los routers en `app/api/`; la lógica que se reutiliza (consultas de POI, semilla, autenticación) en `app/services/`. La API usa los nombres de campo del contrato en snake_case y en español; las entidades conservan su nombre en inglés de §13.2.

## Archivos

| Archivo | Contenido |
|---|---|
| `app/models/core.py` | Destination, Corridor, PointOfInterest, POIAccessibilityAttribute, AccessibilityEvidence, OpeningHours, Provider, DataSource, DataLineage, MetricDefinition |
| `app/models/private.py` | User, ConsentGrant, PrivacyPreference, UserAccessibilityPreference, TripSession, LocationSample, VisitCandidate, ConfirmedVisit, CheckIn, Review, ReviewDimension, CommunityReport, MediaAsset, SavedPlace, PlaceList, PlaceListItem, Itinerary, ItineraryDay, ItineraryStop, Recommendation, RecommendationFeedback |
| `app/models/analytics.py` | AggregateMetric |
| `app/models/audit.py` | AuditEvent, ModerationCase |
| `alembic/versions/0002_modelo_p0.py` | Tablas, restricciones e índices espaciales; extensión `unaccent` |
| `app/services/semilla.py` | Carga idempotente desde `data/` |
| `app/services/catalogo.py` | Consulta y serialización de POI (solo esquema `core` y `audit`) |
| `app/services/seguridad.py` | Hash argon2, JWT y dependencias de rol |
| `app/recommender/tipos.py` | `SolicitudRuta`, `POICandidato`, `RespuestaRuta` y tipos multi-día |
| `app/recommender/__init__.py` | Motor provisional voraz por cercanía (lo reemplaza 015) |
| `app/privacy/registros.py` | Filtro de registros que oculta coordenadas |
| `docs/api/contrato-p0.md` | Contrato P0 para el frontend |
| `docs/dominio/modelo-de-datos.md` | Entidades, esquema e invariantes |

## Decisiones

- `poi_id`, `destino_id` y `corredor_id` son texto: vienen de la spec 012 y de `destinos.csv`. Las entidades propias usan enteros o UUID (`User`).
- Las claves foráneas de `private` hacia `core` son válidas; `core` nunca apunta a `private`. `audit.moderation_case` apunta a `private.community_report` con `ON DELETE SET NULL`, para que el caso sobreviva al borrado de la persona sin datos personales.
- `cobertura_accesibilidad`: `verificada` si `acceso_sin_escalones` y `banio_accesible` están verificados; `parcial` si al menos un atributo está verificado; `sin_verificar` en otro caso.
- `accesibilidad` en `POIResumen` trae siempre los 9 atributos; los que no tienen dato salen con `estado = sin_verificar` y `valor = null` (constitución XIII).
- La semilla no sobrescribe atributos con `origen = comunidad` (vienen de moderación).
- El JWT sin `JWT_SECRETO` usa un secreto aleatorio por proceso: los tokens no sobreviven a un reinicio, pero nunca hay un secreto en el código.
- El punto de partida del itinerario no se guarda (minimización, §14).

## Pruebas

- `tests/conftest.py`: crea `pueblaviva_test` en el mismo PostGIS, aplica migraciones una vez por sesión y trunca entre pruebas.
- Una prueba por endpoint, más autorización vertical (visitante no modera) y horizontal (un usuario no ve guardados ni listas de otro).
- Prueba de que `GET /pois*` no toca `private` (se capturan las sentencias SQL) ni devuelve datos personales.
- Prueba de que los registros no traen coordenadas.
- Semilla con el fixture sintético `tests/datos/`.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| La spec 012 cambia columnas | El contrato está fijado en esta spec y en `modelo-de-datos.md`; la semilla falla con un mensaje claro si falta una columna |
| Otras specs agregan migraciones en paralelo | Esta migración es `0002`; las siguientes encadenan desde ella |
