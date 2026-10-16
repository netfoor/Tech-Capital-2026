# Arquitectura

```
Fuentes públicas ─► pipelines/ (Python) ─► data/curado/ (CSV versionados) ─► semilla ─► Postgres + PostGIS
                                                                                          ▲
                PWA y tablero (React) ──► /api ──► FastAPI ──► recomendador ─────────────┘
```

- **Datos:** `pipelines/` descarga (con red) e integra (sin red). La integración es determinista: dos corridas dan archivos idénticos.
- **Base:** cuatro esquemas: `core` (catálogo), `private` (datos personales), `analytics` (agregados) y `audit` (moderación y eventos). Migraciones con Alembic.
- **API:** FastAPI con el contrato documentado en [`docs/api/contrato-p0.md`](../api/contrato-p0.md); JWT con los roles visitante, viewer, analista y admin.
- **Recomendador:** paquete puro en `backend/app/recommender/`, sin base de datos; su ficha está en [`docs/ia/model_card_recomendador.md`](../ia/model_card_recomendador.md).
- **Despliegue:** Vercel (dos servicios) y Neon ([ADR-0011](../decisiones/0011-despliegue-en-vercel-con-neon.md), [`docs/despliegue.md`](../despliegue.md)).

Las decisiones están en [`docs/decisiones/`](../decisiones/). La metodología es desarrollo guiado por especificaciones: cada funcionalidad tiene su carpeta en `specs/`, y una constitución fija las reglas que ninguna tarea rompe.
