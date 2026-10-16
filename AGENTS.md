# Reglas de ejecución

Este documento es para cualquier persona o agente que tome una tarea de este repositorio. Si algo de aquí choca con [`specs/constitucion.md`](specs/constitucion.md), manda la constitución.

## 1. Antes de la primera tarea

Lee en este orden:

1. [`README.md`](README.md)
2. [`specs/constitucion.md`](specs/constitucion.md)
3. [`docs/plan-de-ejecucion.md`](docs/plan-de-ejecucion.md): ruta crítica, carriles y reglas de coordinación
4. [`docs/dominio/lenguaje-ubicuo.md`](docs/dominio/lenguaje-ubicuo.md) y [`docs/dominio/mapa-de-contextos.md`](docs/dominio/mapa-de-contextos.md)
5. La carpeta de la spec en la que vas a trabajar: `spec.md`, `plan.md` y `tasks.md`

Según la tarea, consulta también:

| Si la tarea toca… | Lee |
|---|---|
| Columnas de una tabla | [`docs/dominio/modelo-de-datos.md`](docs/dominio/modelo-de-datos.md) |
| Los JSON del sitio | [`contracts/`](contracts/) |
| Cualquier cosa visual | [`docs/diseno.md`](docs/diseno.md) |
| Un componente con IA | [`docs/ia-responsable.md`](docs/ia-responsable.md) |
| Un requisito de la convocatoria | [`docs/bases/trazabilidad.md`](docs/bases/trazabilidad.md) |
| Una decisión ya tomada | [`docs/decisiones/`](docs/decisiones/) |

## 2. Elegir una tarea

- Las tareas están en `specs/NNN-*/tasks.md`. Estados: `[ ]` libre, `[~]` tomada, `[x]` hecha.
- Toma la primera tarea `[ ]` de la ruta crítica cuyas dependencias estén en `[x]`. P0 va antes que P1, y P1 antes que P2 (constitución, VIII).
- `[P]` significa que la tarea se puede hacer en paralelo con otras de la misma spec.
- **Para tomarla:** cambia `[ ]` por `[~]`, haz commit (`chore: toma T006-05`) y push de inmediato. Si al hacer pull ya estaba tomada, elige otra.

## 3. Hacer la tarea

1. Implementa lo que pide la tarea y su spec, nada más. Lo que veas que falta se anota en la spec; no se hace en la misma tarea.
2. Si la spec es ambigua o ya no corresponde a la realidad (una API cambió, un dato no existe):
   - elige la opción más conservadora que respete la constitución;
   - anótala con fecha en «Preguntas abiertas» de la spec;
   - si cambia una decisión de arquitectura, agrega un ADR en `docs/decisiones/` con el siguiente número y el mismo formato.
3. Si cambian las columnas de una tabla o un contrato, el orden es: primero `docs/dominio/modelo-de-datos.md` o `contracts/`, después el código. El cuerpo del commit dice `contrato:` y qué cambió.
4. La tarea está hecha cuando pasa su «Verificación» y `make verificar`. Entonces se marca `[x]`, se actualiza el «Estado» de la spec si cambió y se hace commit con el identificador de la tarea.

## 4. Comandos

| Qué | Comando |
|---|---|
| Lista de comandos | `make ayuda` |
| Instalar dependencias | `make instalar` |
| Regenerar `data/curado/` (etapas sin red) | `make datos` |
| Verificación completa | `make verificar` |
| Paquete de datos del sitio | `make exportar` |
| Sitio en local | `make dev` |
| Compilar el sitio | `make web` |
| Revisar y aplicar la infraestructura | `make infra-plan` y `make infra-aplicar` |
| Desplegar | `make desplegar` |

Python vive en `pipelines/` y se corre con uv: `uv run radar --help`, `uv run pytest`, `uv run ruff check .` y `uv run ruff format --check .`. Los extras se instalan con `uv sync --extra senales` o `uv sync --extra asistentes`.

Las etapas con red o con costo (Trends, YouTube y asistentes) no forman parte de `make datos`. Se corren a propósito con su comando, respetan sus topes y guardan lo crudo con fecha.

## 5. Código

**Python (`pipelines/`)**
- Un paquete por contexto: `catalogo`, `indicadores`, `senales`, `panel`, `asistentes`, `comentarios`, `radar` y `exportar`. Un contexto no importa a otro; lo compartido va en `radar/comun/`. La prueba de arquitectura (T008-01) lo revisa.
- Los contextos se comunican con archivos en `data/curado/` (ADR-0003).
- Las rutas se arman con `radar.config.ruta()` y las llaves se leen con `radar.config.cargar_entorno()`.
- Módulos, funciones y columnas se nombran en español y con el lenguaje ubicuo.
- Cada comando nuevo se registra en `radar/cli.py`, con ayuda en español, y en la tabla de `pipelines/README.md`.
- Cada tabla curada nueva tiene sus columnas en `modelo-de-datos.md`, su `fuente_id` o identificador de corrida y una prueba en `tests/`.
- Resultados deterministas: semilla fija, orden estable de filas y columnas, y `float_format="%.4f"` al escribir CSV.
- Las pruebas no llaman a servicios externos; usan respuestas guardadas en `tests/datos/`.

**Sitio (`web/`)**
- Astro estático, Tailwind 4 con los tokens de `docs/diseno.md`, d3 y anime.js. Sin CDN, sin fuentes descargadas y sin llamadas a servicios externos.
- Todo dato visible sale de `web/public/datos/`. En los `.astro` no se escriben cifras.
- Antes de dar por terminada una sección, se revisa la lista de `docs/diseno.md` §12.

**Infraestructura (`infra/`)**
- Terraform con el perfil AWS `Fortino-IAM-Admin`. Antes de cada commit: `terraform fmt` y `terraform validate`.
- `terraform apply` lo corre solo quien opera la infraestructura, después de revisar el `plan`. El estado es local y no se versiona.

## 6. Datos

| Carpeta | ¿Se versiona? | Quién la escribe |
|---|---|---|
| `data/fuentes/` | Sí | Personas, al registrar una fuente: archivo original más su fila en `fuentes.csv` con URL, fecha y SHA-256. Un original nunca se edita |
| `data/referencia/` | Sí | Personas, con revisión. Cada fila dice su origen |
| `data/curado/` | Sí | Solo el código |
| `data/crudo/` | No | Las etapas con red. Se conserva en la computadora que lo generó |
| `data/privado/` | No | Panel y comentarios, que tienen datos personales |
| `web/public/datos/` y `web/public/descargas/` | Sí | Solo `make exportar`. Se versionan para que cualquier clon pueda compilar y desplegar |

- Fuera de `data/privado/` no hay nombres, usuarios, correos, teléfonos ni texto de comentarios.
- Las llaves solo van en `.env` (la plantilla es `.env.example`). `make verificar` busca patrones de llaves en los archivos del repositorio.

## 7. Commits

- Mensaje breve en español: `tipo: qué cambió (T00N-NN)`. Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore` y `build`.
  - `feat: interés de búsqueda mensual por destino (T003-04)`
  - `chore: toma T006-05`
  - `docs: aclara el corte de los cuadrantes`
- Una tarea, un commit, cuando se pueda.
- El mensaje no lleva líneas de coautoría ni firmas generadas por herramientas.
- `git pull --rebase` antes de cada push. En `main` no se reescribe la historia ni se usa `--force`.

## 8. Lo que no se hace

- Acceder a TikTok u otras plataformas con automatización o con cuentas ajenas (ADR-0004).
- Escribir cifras a mano en el sitio o en los entregables.
- Publicar algo que no pasó `make verificar`.
- Subir llaves, `data/crudo/` o `data/privado/`.
- Mencionar en el sitio o en los documentos las herramientas con que se construyó el proyecto (constitución, X).
- Abrir una tarea P1 mientras haya una P0 libre y desbloqueada.

## 9. Al cerrar una sesión de trabajo

- Cada tarea tomada queda en `[x]`, o vuelve a `[ ]` con una nota en su spec sobre lo que falta.
- Todo queda con push.
