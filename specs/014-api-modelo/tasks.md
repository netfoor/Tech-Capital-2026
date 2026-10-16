# Tareas 014 · API y modelo de datos

Formato: `[ ]` pendiente, `[~]` en curso, `[x]` hecha. `[P]` = paralelizable con otras tareas de esta spec.

## Modelo

- [x] T014-01 Spec, plan, tareas, `docs/dominio/modelo-de-datos.md` y `docs/api/contrato-p0.md`. Verificación: revisión del PR.
- [x] T014-02 Modelos de `core`, `private`, `analytics` y `audit` con invariantes de §13.2 y migración `0002`. Verificación: `uv run alembic downgrade base && uv run alembic upgrade head`.
- [x] T014-03 Semilla idempotente desde `data/` y fixture sintético en `tests/datos/`. Verificación: `uv run pytest tests/test_semilla.py`.

## API

- [ ] T014-04 [P] Autenticación: registro, inicio de sesión, JWT y roles. Verificación: `tests/test_auth.py`.
- [ ] T014-05 [P] `GET /pois`, `GET /pois/{poi_id}` y `GET /destinos`. Verificación: `tests/test_pois.py`.
- [ ] T014-06 Tipos del recomendador, motor provisional, `POST /itineraries/recommend` y `POST /itineraries/from-saved`. Verificación: `tests/test_itinerarios.py`.
- [ ] T014-07 [P] Guardados y listas. Verificación: `tests/test_guardados.py`, con autorización horizontal.
- [ ] T014-08 Reseñas, reporte de barrera y moderación que actualiza la ficha. Verificación: `tests/test_barreras.py`, con autorización vertical y el circuito de §06.8.
- [ ] T014-09 Consentimientos, `GET /me/export` y `DELETE /me`. Verificación: `tests/test_privacidad.py`.
- [ ] T014-10 Routers vacíos de 017 y 019, registros sin coordenadas y prueba de que `/pois*` no expone `private`. Verificación: `tests/test_privacidad.py`.
