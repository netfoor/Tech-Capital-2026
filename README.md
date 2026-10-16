# Radar de Atención Turística — Puebla

Herramienta de datos para la Secretaría de Desarrollo Turístico del Estado de Puebla. Mide cómo aparecen los destinos poblanos en los lugares donde hoy se decide un viaje y cruza esa atención con lo que pasa en cada destino. Los lugares son TikTok, YouTube, el buscador de Google y los asistentes conversacionales. Lo que pasa en el destino se mide con ocupación hotelera, llegadas de turistas y derrama.

Proyecto del equipo DreamHack para el Hackathon «Puebla Turística 360°: datos que transforman experiencias», de Tech Capital 2026. Lo organizan SECIHTI Puebla y la Secretaría de Desarrollo Turístico, con la Red Intelligentia.

---

## El problema

El turista ya no descarga la aplicación de turismo de un estado. Decide a dónde ir viendo videos o preguntándole a un asistente. Hoy nadie mide qué encuentra ahí sobre Puebla ni si esa atención se convierte en visitas.

- El propio Observatorio Turístico de la Secretaría reporta que las **redes sociales son el principal medio por el que el visitante se entera de la ciudad de Puebla: 39.7 %**, por encima de amigos y familiares (32.9 %). Es el informe de vacaciones de verano 2024.
- Los **12 Pueblos Mágicos** recibieron el 28.8 % de la afluencia estatal en 2025, pero todos tienen **menor ocupación hotelera y menor derrama por visitante** que la capital. Pahuatlán, Tetela de Ocampo y Tlatlauquitepec estuvieron entre 32 y 36 % de ocupación.
- Los informes públicos de promoción digital reportan **impresiones**, no visitantes ni derrama.
- En la serie oficial, la afluencia y la derrama se **derivan** de la llegada de turistas a hoteles. El visitante que va y regresa el mismo día no se mide de forma directa.
- En marzo de 2027 Puebla es sede del **Tianguis Turístico México** (9 al 12 de marzo). Ahí la Secretaría se reúne con compradores y operadores de México y de otros países.

El detalle y las fuentes están en [`docs/producto/evidencia.md`](docs/producto/evidencia.md).

## La propuesta

| | |
|---|---|
| **Qué** | Un radar que muestra, por destino, cuánta atención digital recibe y cómo se compara con su desempeño real. Detecta qué destinos tienen capacidad disponible y poca visibilidad, y qué destinos atraen miradas pero no estancias. |
| **Cómo** | Genera una fuente de datos que hoy no existe y la une con datos oficiales. Se recoge qué aparece en TikTok mediante un panel de personas reales con consentimiento, qué responden los asistentes en cinco idiomas y qué citan, qué se busca en Google y qué se ve en YouTube, incluidos los comentarios. Todo se cruza con la serie mensual 2017–2026 del Observatorio Turístico. |
| **Dónde** | Una plataforma web con cuentas para la Secretaría (radar, fichas por destino, asistentes y redes) y una página pública que explica el problema, el método y los datos. |
| **Para qué** | Para que la Secretaría decida dónde y cómo invertir su promoción, llegue al Tianguis 2027 con fichas por destino respaldadas por datos y mida el efecto antes y después. |

Visión completa: [`docs/producto/vision.md`](docs/producto/vision.md).

## Cómo se trabaja en este repositorio

El proyecto se desarrolla **guiado por especificaciones** y con un **modelo de dominio explícito**:

1. [`specs/constitucion.md`](specs/constitucion.md): principios que ninguna tarea puede romper.
2. [`docs/bases/trazabilidad.md`](docs/bases/trazabilidad.md): cada requisito de la convocatoria, y dónde y cómo se cumple.
3. [`docs/dominio/`](docs/dominio/): lenguaje ubicuo, contextos delimitados, mapa de contextos y modelo de datos.
4. [`docs/arquitectura.md`](docs/arquitectura.md) y [`docs/decisiones/`](docs/decisiones/): componentes, flujo de datos y decisiones registradas.
5. [`specs/`](specs/): una carpeta por funcionalidad con `spec.md` (qué y por qué), `plan.md` (cómo) y `tasks.md` (pasos verificables).
6. [`contracts/`](contracts/): esquemas JSON de los datos publicados. Son el contrato entre el análisis y el sitio.
7. [`AGENTS.md`](AGENTS.md): reglas de ejecución para quien tome una tarea.

El orden de ejecución, las dependencias y la ruta crítica están en [`docs/plan-de-ejecucion.md`](docs/plan-de-ejecucion.md).

## Especificaciones

| Spec | Contexto | Prioridad | Estado |
|---|---|---|---|
| [001 Catálogo de destinos](specs/001-catalogo-destinos/spec.md) | Catálogo territorial | P0 | En curso: semilla lista |
| [002 Indicadores oficiales](specs/002-indicadores-oficiales/spec.md) | Desempeño turístico | P0 | En curso: ingesta lista |
| [003 Tendencias de búsqueda](specs/003-tendencias-busqueda/spec.md) | Atención digital | P0 | Pendiente |
| [004 YouTube](specs/004-youtube/spec.md) | Atención digital | P1 | Pendiente |
| [005 Panel y TikTok](specs/005-panel-tiktok/spec.md) | Panel ciudadano | P0 | Pendiente |
| [006 Auditoría de asistentes](specs/006-auditoria-asistentes/spec.md) | Visibilidad en asistentes | P0 | Pendiente |
| [007 Clasificación de comentarios](specs/007-comentarios/spec.md) | Atención digital | P1 | Pendiente |
| [008 Radar](specs/008-radar/spec.md) | Análisis | P0 | Pendiente |
| [009 Sitio: página pública y plataforma](specs/009-sitio/spec.md) | Publicación | P0 | En curso: andamiaje con acceso |
| [010 Infraestructura](specs/010-infraestructura/spec.md) | Plataforma | P0 | En curso: Terraform con Cognito |
| [011 Entregables y presentación](specs/011-entregables/spec.md) | Entregables | P0 | Pendiente |

P0 = indispensable para la demostración, P1 = la fortalece, P2 = continuidad posterior.

## Estructura

```
├── AGENTS.md                  Reglas para ejecutar tareas
├── Makefile                   Comandos del proyecto (make ayuda)
├── .env.example               Plantilla de llaves; la copia .env no se versiona
├── contracts/                 Esquemas JSON de los datos publicados
├── data/
│   ├── fuentes/               Documentos oficiales originales y registro de fuentes (no se editan)
│   ├── referencia/            Catálogo de destinos y geometrías INEGI
│   ├── curado/                Tablas limpias generadas por los pipelines
│   └── crudo/, privado/       Respuestas de API y datos del panel (fuera de git)
├── docs/
│   ├── bases/                 Convocatoria y matriz de trazabilidad
│   ├── producto/              Visión y evidencia del problema
│   ├── dominio/               Modelo de dominio
│   ├── decisiones/            Registro de decisiones de arquitectura
│   ├── entregables/           Documentos exigidos por la convocatoria
│   ├── arquitectura.md
│   ├── diseno.md              Sistema visual del sitio
│   ├── ia-responsable.md      Componentes con IA, función y límites
│   └── plan-de-ejecucion.md
├── infra/                     Terraform (AWS)
├── pipelines/                 Python con uv: ingesta, análisis y exportación
├── specs/                     Constitución y especificaciones por funcionalidad
└── web/                       Página pública y plataforma (Astro, acceso con Cognito)
```

## Puesta en marcha

Requisitos: [uv](https://docs.astral.sh/uv/), Node.js ≥ 22.22, Terraform ≥ 1.9 y AWS CLI con el perfil `Fortino-IAM-Admin`.

```bash
cp .env.example .env                 # llenar las llaves; .env nunca se versiona
make instalar                        # dependencias de pipelines y del sitio
make datos                           # regenera data/curado desde las fuentes
make verificar                       # pruebas y validación de contratos
make web                             # compila el sitio en web/dist
make desplegar                       # sube el sitio (requiere infra aplicada)
```

Para ver el detalle de cada paso: `make ayuda`.

## Datos

Cada cifra que aparece en el sitio viene de un archivo en `data/curado/` generado por código. Cada fuente tiene registrada su URL, fecha de consulta y huella SHA-256 en [`data/fuentes/fuentes.csv`](data/fuentes/fuentes.csv). Los datos de personas del panel no se versionan; solo se publican agregados.

## Equipo

Equipo de tres estudiantes con un profesor tutor, con perfiles en ciencia de datos e IA, nube y despliegue, y economía y derecho.

## Propiedad intelectual

De acuerdo con la sección 14 de la convocatoria, la propiedad intelectual permanece con sus autores. Los organizadores reciben una autorización de uso no exclusiva, gratuita y no comercial, solo para difusión. La licencia del código está pendiente de decisión del equipo; mientras tanto, todos los derechos quedan reservados.
