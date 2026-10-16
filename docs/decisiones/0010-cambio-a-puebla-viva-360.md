# ADR-0010 · Cambio de producto: de Radar de Atención a Puebla Viva 360

**Estado:** aceptada · 2026-10-16

## Contexto

El equipo refinó la propuesta después de la mentoría. El documento maestro [`docs/producto/contexto-maestro.txt`](../producto/contexto-maestro.txt) (v3.1) define un producto nuevo: **Puebla Viva 360**, una plataforma de experiencias turísticas inclusivas para el visitante (B2C) y un observatorio institucional para la Secretaría de Desarrollo Turístico (B2B).

El Radar medía atención digital y la comparaba con la ocupación. Puebla Viva 360 conserva la idea de decidir con datos y agrega lo que el Radar no tenía: una experiencia útil para el visitante, accesibilidad como criterio de primera clase y un circuito cerrado (la misma señal de accesibilidad personaliza la ruta y revela una brecha territorial).

## Decisión

1. Se construye Puebla Viva 360 en este mismo repositorio.
2. Se reutiliza lo que ya funciona:
   - catálogo de los 12 Pueblos Mágicos con claves INEGI y coordenadas (spec 001);
   - serie hotelera mensual 2017–2026 leída del PDF del Observatorio (spec 002), que alimenta el módulo Oferta–demanda;
   - el registro de fuentes con SHA-256 y el paquete `pipelines/`.
3. El stack cambia a lo que fija la sección 12 del documento maestro:
   - backend en Python 3.12 con uv, FastAPI, SQLAlchemy 2, GeoAlchemy2 y Alembic;
   - PostgreSQL 16 + PostGIS 3 en Docker, con esquemas `core`, `private`, `analytics` y `audit`;
   - frontend en Vite + React + TypeScript (PWA), con MapLibre; el tablero institucional vive en `/admin` con su propio layout.
4. Lo específico del Radar (specs 003–009 y 011, arquitectura, visión y el sitio Astro de `web/`) se mueve a [`docs/archivo/radar/`](../archivo/radar/) o se elimina del árbol. Queda en el historial de git.
5. El trabajo se integra por pull request: una rama por spec o por tarea, revisión y merge a `main`.

## Consecuencias

- El MVP es más grande: hay que priorizar P0 estrictamente (sección 03 del documento maestro).
- La demo es local y reproducible con `docker compose`; el despliegue en AWS solo si P0 y P1 están estables.
- Las reglas del documento maestro se suman a la constitución: datos sintéticos siempre etiquetados, nada de rastreo oculto y agregados con umbral k.
