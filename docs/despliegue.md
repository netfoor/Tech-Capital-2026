# Despliegue

La app pública vive en **https://puebla-viva-360.vercel.app** ([ADR-0011](decisiones/0011-despliegue-en-vercel-con-neon.md)).

| Pieza | Dónde | Notas |
|---|---|---|
| PWA del visitante y tablero (`frontend/`) | Vercel, proyecto `puebla-viva-360`, equipo **GoSoft Projects** | Servicio `frontend` de `vercel.json`, sirve `/` |
| API FastAPI (`backend/`) | El mismo proyecto de Vercel, como función de Python | Servicio `backend`, sirve `/api/*`; la regla del servicio quita el prefijo `/api` |
| Base Postgres 16 + PostGIS | Neon, base `puebla-viva-360-db` (plan gratuito, región iad1) | Conectada desde la integración de Vercel; inyecta `DATABASE_URL` y `DATABASE_URL_UNPOOLED` |
| Presentación | `frontend/public/pitch/` | Se publica en `/pitch/` |

## Variables de entorno en Vercel

| Variable | Valor | Para qué |
|---|---|---|
| `DATABASE_URL` | La pone Neon | Conexión con pooler; `app/config.py` la convierte a `postgresql+psycopg://` |
| `JWT_SECRETO` | Cadena aleatoria | Firma de sesiones; sin ella los tokens no sobreviven entre instancias |
| `DB_SIN_POOL` | `true` | Las funciones no guardan conexiones |
| `DIRECTORIO_MEDIA` | `/tmp/media` | Fotos de reportes. Se pierden al reciclar la instancia: para un piloto, usar almacenamiento de objetos |

## Publicar un cambio

Requisitos: acceso al equipo **GoSoft Projects** en Vercel y `npx vercel login`.

```bash
git checkout main && git pull
make verificar                 # pruebas, estilo y compilación
npx vercel link --project puebla-viva-360 --scope gosoft-projects   # solo la primera vez
make desplegar                 # vercel deploy --prod
```

Para una vista previa sin tocar producción: `npx vercel deploy` (sin `--prod`).

## Cambiar el modelo o los datos de la base

Las migraciones y la semilla se corren desde una computadora del equipo contra la URL directa de Neon:

```bash
npx vercel env pull .env.vercel --environment=production   # no se versiona
export DATABASE_URL="$(grep '^DATABASE_URL_UNPOOLED=' .env.vercel | cut -d= -f2- | tr -d '"')"
cd backend
uv run alembic upgrade head                 # migraciones
uv run python -m app.services.semilla       # catálogo, serie oficial y fichas (idempotente)
uv run python -m app.services.demo_tablero  # cuenta de demostración y datos sintéticos etiquetados
```

`demo_tablero` lee `DEMO_ANALISTA_CORREO` y `DEMO_ANALISTA_CONTRASENA` de `.env`. La cuenta del tablero (`/admin`) se crea con esos valores; pídelos al equipo, no se versionan.

Borra `.env.vercel` al terminar.

## Probar que quedó bien

```bash
curl https://puebla-viva-360.vercel.app/api/health    # {"estado":"ok","base_de_datos":"disponible"}
curl "https://puebla-viva-360.vercel.app/api/pois?limit=3"
```

Si el navegador muestra una versión vieja, es la caché de la PWA: recarga forzada o abre en una ventana privada.
