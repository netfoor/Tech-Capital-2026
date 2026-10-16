# Spec 014 · API y modelo de datos

| | |
|---|---|
| Contexto | Núcleo del backend: catálogo, datos personales, agregados y auditoría |
| Prioridad | P0 |
| Estado | Hecha: modelo, migraciones, semilla y endpoints P0; motor del recomendador provisional hasta la spec 015 |
| Depende de | Fundación (ADR-0010) |
| Habilita | 015 (recomendador), 016 (PWA), 017 (recorridos), 018 (barreras), 019 (tablero) |

## Bases que atiende

- §2 y §3 de la convocatoria: prototipo que mejora la experiencia antes, durante y después de la visita (exploración, guardados, itinerario, reseña y reporte de barrera).
- §5: datos documentados con procedencia (`DataSource`, `DataLineage`), respeto a la privacidad (esquema `private`, consentimientos, exportación y borrado).
- §8: prototipo funcional y demostrable con datos semilla.
- Turismo accesible e incluyente: atributos de accesibilidad con origen, fecha, confianza y estado; restricciones duras en el itinerario.

## Objetivo

Dar a la PWA, al recomendador y al tablero un modelo de datos único (§13.2) y los endpoints P0 (§13.3) con un contrato estable, documentado en [`docs/api/contrato-p0.md`](../../docs/api/contrato-p0.md). La exploración y los itinerarios funcionan sin cuenta; guardar, reseñar y reportar requieren una cuenta con JWT.

## Historias de usuario

**H1 (P0).** Como visitante sin cuenta, quiero buscar lugares del corredor con filtros de costo y accesibilidad.
- Dado el catálogo cargado, cuando pido `GET /pois?sin_escalones=true&solo_verificados=true`, entonces solo veo lugares con acceso sin escalones verificado, y cada atributo sin dato aparece como `sin_verificar`.

**H2 (P0).** Como visitante, quiero ver la ficha de un lugar con sus fuentes y las barreras reportadas.
- Dado un lugar, cuando pido `GET /pois/{poi_id}`, entonces veo descripción, dirección, horario, fuentes con URL y barreras en moderación o aceptadas, sin ningún dato de quien las reportó.

**H3 (P0).** Como visitante, quiero un itinerario con mis restricciones.
- Dado `POST /itineraries/recommend` con `sin_escalones=true`, entonces ninguna parada incumple la restricción y los lugares descartados aparecen en `no_incluidos` con su motivo.

**H4 (P0).** Como visitante con cuenta, quiero guardar lugares en listas y armar un plan de varios días.
- Dado que guardé lugares, cuando pido `POST /itineraries/from-saved`, entonces recibo un plan por día y la lista de lo que no cabe con su motivo.

**H5 (P0).** Como visitante, quiero reportar una barrera; como analista, quiero moderarla.
- Dado un reporte aceptado en `POST /moderation/{id}/decision`, entonces el atributo cambia a `reportado` con el valor del reporte, queda una `AccessibilityEvidence` y un `AuditEvent`, y la siguiente recomendación ya lo considera (§06.8).

**H6 (P0).** Como persona usuaria, quiero ver qué datos tengo y borrarlos.
- Dado `GET /me/export`, entonces recibo todos mis datos; dado `DELETE /me`, entonces no queda ninguna fila mía en `private`.

## Requisitos funcionales

- **FR-014-01** Modelos SQLAlchemy 2 + GeoAlchemy2 de las entidades P0 de §13.2 en su esquema (`core`, `private`, `analytics`, `audit`), con migración de Alembic.
- **FR-014-02** Invariantes de §13.2 como restricciones de base: toda visita guarda fuente de evidencia, precisión, confianza y si fue confirmada; todo atributo de accesibilidad guarda origen, fecha, alcance y estado; toda métrica guarda versión de fórmula y fecha de cálculo; toda tabla con datos posiblemente sintéticos tiene `is_synthetic`.
- **FR-014-03** Carga semilla idempotente (`uv run python -m app.services.semilla`) desde el contrato de datos de la spec 012 (`data/curado/poi.csv`, `poi_accesibilidad.csv`, `corredores.csv`), `data/referencia/destinos.csv`, `data/fuentes/fuentes.csv` y `data/curado/indicadores_oficiales_mensual.csv`.
- **FR-014-04** Endpoints P0 de `docs/api/contrato-p0.md`: POI, destinos, itinerarios, guardados, listas, reseñas, barreras, moderación, consentimientos, exportación y borrado, registro e inicio de sesión.
- **FR-014-05** JWT (HS256, secreto `JWT_SECRETO`) y contraseñas con argon2. Roles: `visitante`, `viewer`, `analista`, `admin`. El registro siempre crea `visitante`.
- **FR-014-06** Routers vacíos registrados para `/sessions`, `/visits`, `/checkins` (spec 017) y `/b2b` (spec 019).
- **FR-014-07** Tipos del recomendador en `app/recommender/tipos.py` y un motor provisional voraz por cercanía que respeta las restricciones duras; la spec 015 lo reemplaza sin cambiar la interfaz.

## Requisitos no funcionales

- Las respuestas públicas (`/pois*`, `/destinos`, `/itineraries/*`) no consultan el esquema `private` ni contienen datos personales (constitución IX y XI). Hay una prueba que lo comprueba.
- Los registros de la API no contienen coordenadas (§14).
- Pruebas con base PostGIS real (`pueblaviva_test`), sin servicios externos.
- `alembic downgrade base && alembic upgrade head` funciona en limpio.

## Fuera de alcance

- Sesiones, muestras y visitas (spec 017); tablero y agregados con k (spec 019); importación por enlace y enlaces compartidos (spec 022, P1).
- `Post`, `ShareLink` e `ImportAttempt` de §13.2: son P1 y llegan con su spec.
- El motor real del recomendador (spec 015).

## Preguntas abiertas

- 2026-10-16. El contrato de datos de la spec 012 no fija el formato de `valor`. Se asume `si` | `no` | `limitado` para atributos binarios y un número en texto para `pendiente_pct` y `numero_escalones`. El filtro `sin_escalones` solo acepta `si`.
- 2026-10-16. `fuentes` en `poi.csv` se interpreta como identificadores de `fuentes.csv` separados por `|` o `;`. Una fuente no registrada se crea con su identificador como nombre y sin URL.
- 2026-10-16. Un atributo de accesibilidad sin `fecha` en el CSV se rechaza en la semilla (invariante de §13.2) y se reporta; no se inventa una fecha.
- 2026-10-16. `barreras_reportadas` sale de `audit.moderation_case` (sin persona), no de `private.community_report`. Los casos rechazados no se muestran.
- 2026-10-16. `POST /itineraries/from-saved` devuelve también `itinerario_id` (campo adicional, no rompe el contrato).
- 2026-10-16. `foto` en `POST /reports/barrier` es una imagen en base64 (JPEG, PNG o WebP, ≤ 5 MB) que se vuelve a codificar sin metadatos (sin EXIF) y se guarda en `data/privado/media/`.
