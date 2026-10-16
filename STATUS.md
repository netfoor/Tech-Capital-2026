# Estado del proyecto

Última actualización: 2026-10-16. Se actualiza en cada pull request.

Los cuatro estados se separan siempre: **producto objetivo**, **MVP implementado**, **demo sintética** y **resultado medido** (contexto maestro, §00.3).

## Hecho

- Fundación: ADR-0010, plan de ejecución, matriz de requisitos y mapa de entregables.
- Backend FastAPI con `/health`, Alembic y PostGIS con esquemas `core`, `private`, `analytics` y `audit`.
- Frontend Vite + React + TypeScript con rutas `/` (visitante) y `/admin` (Secretaría).
- CI con pruebas, estilo y compilación.
- Reutilizado del Radar: catálogo de 12 Pueblos Mágicos y serie hotelera 2017–2026.

## En curso

- Ninguna spec tomada todavía.

## Bloqueado

- Token de la API DENUE de INEGI: hace falta registrarlo con un correo del equipo. Alternativa sin token: descarga masiva por entidad.

## Decisiones

- ADR-0010: cambio de producto y de stack; mismo repositorio; integración por PR.
- Puerto local de PostGIS: 5433 (configurable con `DB_PUERTO`), para no chocar con otras bases.

## Próximos pasos

1. Specs 012 (ingesta) y 014 (API y modelo) en paralelo.
2. Después 015 (recomendador), 016 (PWA) y 018 (barreras).

## Para decidir con el equipo

- 2026-10-16: llegaron a `main` 14 commits del Radar (specs 001, 003, 005, 006 y 008: Trends, auditoría de asistentes e índices). Se integraron sin perder nada: el código sigue en `pipelines/` con sus pruebas y las tareas quedaron en `docs/archivo/radar/`. Propuesta: reutilizar la auditoría de asistentes como módulo P1 del tablero («qué recomiendan los asistentes sobre cada destino»).
