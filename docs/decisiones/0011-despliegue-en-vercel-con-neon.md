# ADR-0011 · Despliegue en Vercel con Neon

**Estado:** aceptada · 2026-10-17

## Contexto

La demo necesita una URL pública estable con la PWA, la API y la base PostGIS. El perfil de AWS del proyecto no estaba disponible en la computadora que preparó el despliegue y el tiempo no alcanzaba para aplicar Terraform.

## Decisión

- Un proyecto de Vercel (`puebla-viva-360`, equipo GoSoft Projects) con dos servicios en `vercel.json`: `frontend` (Vite, en `/`) y `backend` (FastAPI, en `/api`; la regla del servicio quita el prefijo).
- Base Postgres 16 con PostGIS en Neon (plan gratuito, región iad1), conectada al proyecto desde la integración de Vercel. Vercel inyecta `DATABASE_URL`; `app/config.py` la convierte al driver psycopg.
- Las funciones no guardan conexiones (`DB_SIN_POOL=true`); el pooler de Neon las reparte.
- Las fotos de reportes van a `/tmp/media` (`DIRECTORIO_MEDIA`): se pierden al reciclar la instancia. Para un piloto van a almacenamiento de objetos.
- Las migraciones y la semilla se corren desde una computadora del equipo contra la URL directa de Neon (`DATABASE_URL_UNPOOLED`).

## Consecuencias

- `https://puebla-viva-360.vercel.app` sirve todo con HTTPS y sin servidores que administrar.
- Terraform en AWS (`infra/`) queda como ruta para un piloto institucional.
