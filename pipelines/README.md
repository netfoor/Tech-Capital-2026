# Pipelines

Paquete `radar` (Python ≥ 3.11, gestionado con [uv](https://docs.astral.sh/uv/)). Se encarga de la ingesta, la limpieza, el análisis y la exportación de datos del radar.

```bash
uv sync                          # instala dependencias base
uv sync --extra senales          # Google Trends y YouTube (spec 003 y 004)
uv sync --extra asistentes       # OpenAI y Gemini (spec 006 y 007)
uv run radar --help              # comandos disponibles
uv run pytest                    # pruebas
uv run ruff check .              # estilo
```

## Comandos

| Comando | Qué hace | Spec |
|---|---|---|
| `radar fuentes` | Comprueba la SHA-256 de cada fuente registrada | 002 |
| `radar catalogo` | Valida `data/referencia/destinos.csv` | 001 |
| `radar indicadores` | Lee el PDF del Observatorio Turístico y escribe `data/curado/indicadores_oficiales_*.csv` | 002 |
| `radar resumen --anio 2025` | Muestra el resumen anual por destino | 002 |
| `radar radar calcular` | Escribe `data/curado/radar_destinos.csv` con los componentes disponibles | 008 |

Cada spec que agrega una etapa nueva añade su comando en esta tabla.

## Organización

```
src/radar/
├── config.py          Rutas del repositorio y carga de .env
├── texto.py           Normalización de nombres
├── fuentes.py         Registro de fuentes y SHA-256
├── catalogo.py        Contexto: catálogo territorial
├── indicadores/       Contexto: desempeño turístico (Sectur Puebla / DataTur)
├── senales/           Contexto: atención digital (Trends, YouTube)            ← spec 003, 004
├── panel/             Contexto: panel ciudadano y TikTok                       ← spec 005
├── asistentes/        Contexto: visibilidad en asistentes                       ← spec 006
├── comentarios/       Clasificación de comentarios                              ← spec 007
├── radar/             Contexto: análisis (índices, cuadrantes, modelo)          ← spec 008
└── exportar/          Publicación: JSON del sitio y manifiesto                  ← spec 009
```

Cada módulo de contexto solo lee las tablas publicadas de otros contextos (en `data/curado/`) y no importa su código interno. Así los límites del dominio se mantienen en el código.
