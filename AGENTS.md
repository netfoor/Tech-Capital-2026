# Reglas de ejecución

Este documento es para cualquier persona o agente que tome una tarea de este repositorio. Si algo de aquí choca con [`specs/constitucion.md`](specs/constitucion.md), manda la constitución.

## 1. Antes de la primera tarea

Lee en este orden:

1. [`README.md`](README.md) y [`STATUS.md`](STATUS.md)
2. [`specs/constitucion.md`](specs/constitucion.md)
3. [`docs/producto/contexto-maestro.txt`](docs/producto/contexto-maestro.txt): el producto completo; las secciones se citan como §NN
4. [`docs/plan-de-ejecucion.md`](docs/plan-de-ejecucion.md): specs, carriles y ruta crítica
5. La carpeta de la spec en la que vas a trabajar: `spec.md`, `plan.md` y `tasks.md`

Según la tarea, consulta también:

| Si la tarea toca… | Lee |
|---|---|
| Un requisito de la convocatoria | [`docs/requirements.md`](docs/requirements.md) |
| Un entregable | [`docs/ENTREGABLES.md`](docs/ENTREGABLES.md) |
| Datos personales o ubicación | §07 y §14 del contexto maestro |
| Accesibilidad | §06 del contexto maestro |
| Un componente con IA | §10 del contexto maestro y `docs/ia/` |
| Una decisión ya tomada | [`docs/decisiones/`](docs/decisiones/) |

## 2. Elegir una tarea

- Las tareas están en `specs/NNN-*/tasks.md`. Estados: `[ ]` libre, `[~]` tomada, `[x]` hecha.
- P0 va antes que P1, y P1 antes que P2 (constitución, VIII).
- Si la spec no existe todavía, la primera commit de tu rama la crea con `spec.md`, `plan.md` y `tasks.md`, a partir del contexto maestro.

## 3. Hacer la tarea

1. Crea una rama desde `main` actualizado: `feat/NNN-nombre-corto`.
2. Implementa lo que pide la spec, nada más. Lo que veas que falta se anota en la spec.
3. Si la spec es ambigua, elige la opción más conservadora que respete la constitución y anótala con fecha en «Preguntas abiertas». Si cambia una decisión de arquitectura, agrega un ADR en `docs/decisiones/`.
4. La tarea está hecha cuando pasa su verificación y `make verificar`. Se marca `[x]` y se actualiza `STATUS.md`.
5. Abre un pull request hacia `main` con: qué cambia, cómo se verificó y qué queda pendiente. Si cambia el modelo de datos o un endpoint, la descripción lo dice con `contrato:`.

## 4. Comandos

| Qué | Comando |
|---|---|
| Lista de comandos | `make ayuda` |
| Instalar dependencias | `make instalar` |
| Base de datos y migraciones | `make db` |
| API y PWA en local | `make dev` |
| Regenerar datos curados | `make datos` |
| Verificación completa | `make verificar` |
| Demo con datos semilla | `make demo` |

## 5. Código

**Backend (`backend/`)**: Python 3.12 con uv, FastAPI, Pydantic v2, SQLAlchemy 2, GeoAlchemy2 y Alembic.
- Módulos en `app/{api,models,schemas,services,pipeline,recommender,privacy}`.
- Esquemas de base: `core` (catálogo), `private` (datos personales y trayectorias), `analytics` (agregados protegidos) y `audit`.
- Cada cambio de modelo lleva su migración de Alembic.
- Cada endpoint tiene prueba. Las pruebas no llaman a servicios externos.

**Datos (`pipelines/`)**: Python con uv. Las rutas se arman con `radar.config.ruta()`. Resultados deterministas: semilla fija, orden estable y `float_format="%.4f"` en CSV. Cada fuente se registra en `data/catalog/data_catalog.csv`.

**Frontend (`frontend/`)**: Vite, React y TypeScript. La lista es la vista accesible principal y el mapa es su equivalente. Objetivo WCAG 2.2 AA. Atribución «© OpenStreetMap contributors» visible en cada mapa.

**Nombres**: módulos, funciones y columnas del dominio en español. Las entidades de §13.2 conservan su nombre en inglés en el código y en la API, porque así las fija el contexto maestro.

## 6. Datos

| Carpeta | ¿Se versiona? | Quién la escribe |
|---|---|---|
| `data/fuentes/` | Sí | Personas: archivo original y su fila con URL, fecha y SHA-256. Un original nunca se edita |
| `data/referencia/` | Sí | Personas, con revisión |
| `data/curado/` | Sí | Solo el código |
| `data/synthetic/` | Sí | Solo el código. Cada fila lleva `is_synthetic=true` |
| `data/crudo/` y `data/privado/` | No | Etapas con red y datos personales |

- Todo dato sintético se muestra en la interfaz con la etiqueta «DATOS SINTÉTICOS DE DEMOSTRACIÓN».
- Las llaves solo van en `.env`. `make verificar` busca patrones de llaves.

## 7. Commits y pull requests

- Mensaje breve en español: `tipo: qué cambió (NNN)`. Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore` y `build`.
- Commits pequeños. Nada se sube directo a `main`: todo entra por pull request.
- El mensaje no lleva líneas de coautoría ni firmas generadas por herramientas.

## 8. Lo que no se hace

- Rastreo oculto, ubicación pública en vivo o un tablero con personas identificables.
- Scraping de Instagram, TikTok u otras plataformas en contra de sus términos.
- Inventar datos, cifras, resultados de IA, entrevistas o acuerdos. Lo no verificado se marca «NO VERIFICADO».
- Escribir cifras a mano en la interfaz o en los entregables.
- Subir llaves, `data/crudo/` o `data/privado/`.
- Mencionar en la interfaz o en los entregables las herramientas con que se construyó el proyecto (constitución, X).

## 9. Al cerrar una sesión de trabajo

- Cada tarea tomada queda en `[x]`, o vuelve a `[ ]` con una nota en su spec sobre lo que falta.
- `STATUS.md` al día y el pull request abierto.
