# Contexto del proyecto

Léelo completo antes de tocar el repositorio. Sirve para personas y para asistentes de programación: si trabajas con uno, pásale este archivo y [`AGENTS.md`](AGENTS.md).

## Qué es

**Puebla Viva 360**: proyecto del equipo DreamHack para el Hackathon «Puebla Turística 360°: datos que transforman experiencias» (Tech Capital 2026, SECIHTI Puebla y Secretaría de Desarrollo Turístico; evento del 15 al 17 de octubre de 2026).

Dos productos que comparten catálogo y métricas, pero no datos personales:

1. **PWA del visitante** (`/`): descubrir lugares con su accesibilidad, guardarlos, planear rutas que respetan restricciones (sin escalones, baño accesible, descansos, presupuesto), reportar barreras y calificar.
2. **Tablero de la Secretaría** (`/admin`): Oferta–demanda con la serie oficial real, Inclusión (cobertura de información de accesibilidad), Panorama y Experiencia (sintéticos etiquetados por ahora) y cola de moderación.

**Circuito cerrado:** un reporte de barrera se modera, cambia la ficha del lugar, aparece en el tablero y la siguiente recomendación ya lo considera.

En producción: **https://puebla-viva-360.vercel.app** · presentación en `/pitch/`.

## Historia (para no confundirse)

- Hasta el 15 de octubre el proyecto era el **Radar de Atención Turística**: medía atención digital (Trends, YouTube, asistentes de IA) contra la ocupación. Está en [`docs/archivo/radar/`](docs/archivo/radar/).
- El 16 de octubre el equipo cambió a Puebla Viva 360 ([ADR-0010](docs/decisiones/0010-cambio-a-puebla-viva-360.md)). La definición completa del producto está en [`docs/producto/contexto-maestro.txt`](docs/producto/contexto-maestro.txt); las secciones se citan como §NN.
- `pipelines/` conserva módulos del Radar (`senales`, `asistentes`, `radar`) que la app no usa; ver la sección «Pendientes y decisiones».

## Arquitectura

```
Fuentes públicas ──► pipelines/ (Python, uv) ──► data/curado/*.csv ──► semilla ──► PostGIS (Neon)
  INEGI DENUE y MG        integrar, limpiar,         versionados,          backend/app/services/semilla.py
  SIC Cultura             enlazar por nombre         reproducibles
  OpenStreetMap           y distancia
  Observatorio (PDF)
                                                                      ▲
PWA y tablero (frontend/, Vite + React) ──► /api ──► FastAPI (backend/) ┘
                     Vercel: dos servicios en vercel.json
```

| Carpeta | Qué hay |
|---|---|
| `backend/` | FastAPI, SQLAlchemy 2, GeoAlchemy2, Alembic. `app/api` (rutas), `app/services` (lógica, semilla), `app/recommender` (motor de rutas), `app/models` (esquemas `core`, `private`, `analytics`, `audit`), `metrics/definitions.yaml` (fichas de 28 indicadores) |
| `frontend/` | PWA y tablero. `src/` es la app del visitante; `src/admin/` el tablero; `public/pitch/` la presentación |
| `pipelines/` | Ingesta y limpieza. Paquete `radar` (el nombre es herencia). Comandos: `uv run radar --help` |
| `analysis/` | `01_problema.py` (concentración, desajuste y brecha de accesibilidad) y `02_eval_recomendador.py` (motor contra líneas base) |
| `reports/` | Salidas del análisis y reporte de calidad de datos. Las genera el código |
| `data/` | `fuentes/` (originales con SHA-256), `referencia/`, `curado/` (lo escribe el código), `catalog/data_catalog.csv` |
| `docs/` | Producto, decisiones (ADR), API, dominio, IA, pitch, entregables y despliegue |
| `specs/` | Constitución y una carpeta por funcionalidad con `spec.md`, `plan.md` y `tasks.md` |

## Cifras que sostienen el pitch

Todas las genera el código; si cambian los datos, cambian aquí ([`reports/01_problema.md`](reports/01_problema.md), [`reports/eval_recomendador.md`](reports/eval_recomendador.md)).

- La capital y Cholula recibieron el 54.2 % de las llegadas a hotel del estado en 2025.
- 10 de 11 Pueblos Mágicos tienen oferta cultural y ocupación por debajo del promedio estatal.
- Solo el 2.2 % de 1,991 lugares tiene algún dato de accesibilidad; en 10 de 11 Pueblos Mágicos, ninguno.
- El recomendador tuvo 0 violaciones de restricciones indispensables en 40 perfiles; recomendar lo más popular, 219; lo más cercano, 237.

## Reglas que no se rompen

Detalle en [`specs/constitucion.md`](specs/constitucion.md):

- Ninguna cifra se escribe a mano en la interfaz ni en los entregables.
- Lo sintético siempre lleva la etiqueta «DATOS SINTÉTICOS DE DEMOSTRACIÓN».
- La falta de un dato de accesibilidad es «sin verificar», nunca «accesible».
- No hay rastreo oculto. El tablero solo ve agregados con umbral k.
- Todo cambio entra por pull request. Los commits van en español, sin líneas de coautoría.

## Cómo trabajar

```bash
make instalar && make demo && make dev     # local: PostGIS en Docker (puerto 5433), API :8000, PWA :5173
make verificar                             # antes de cada PR
```

- Despliegue y base de producción: [`docs/despliegue.md`](docs/despliegue.md).
- Estado y pendientes al día: [`STATUS.md`](STATUS.md).
- Preparar la presentación: [`docs/pitch/`](docs/pitch/).

En Windows: `make` no viene instalado (usa Git Bash y los comandos del Makefile), y la consola puede necesitar `PYTHONIOENCODING=utf-8`.

## Pendientes y decisiones

- **Spec 017, recorridos y visitas con GPS:** en desarrollo, sin mergear. La demo lo presenta como siguiente paso.
- **Specs 020 a 022** (accesibilidad manual, MCP, importar enlaces): no empezadas.
- **Datos de accesibilidad:** falta la auditoría presencial del equipo (8 a 15 lugares del corredor).
- **Módulos del Radar en `pipelines/`:** el equipo decide si se reutilizan (por ejemplo, la auditoría de asistentes como módulo del tablero) o se retiran.
- **CI de GitHub:** el flujo existe (`.github/workflows/ci.yml`), pero en `netfoor/Tech-Capital-2026` no corre; el dueño debe habilitar Actions. Mientras tanto, `make verificar` en local.
