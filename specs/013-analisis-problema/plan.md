# Plan 013 · Análisis del problema

## Enfoque

Un script, `analysis/01_problema.py`, con funciones puras de concentración en `analysis/concentracion.py`, probadas con un caso calculado a mano. Lee `data/curado/`, `data/referencia/` y los metadatos de `data/fuentes/fuentes.csv`. No usa red ni azar. Escribe tablas, figuras y el reporte en `reports/`.

Se corre desde la raíz:

```
uv run --project pipelines --extra analisis python analysis/01_problema.py
```

## Entradas

| Archivo | Uso |
|---|---|
| `data/curado/indicadores_oficiales_anual.csv` | A y C: llegadas, ocupación y estadía por centro y año |
| `data/curado/oferta_denue_municipio.csv` | B y C: establecimientos por municipio y rama |
| `data/curado/poi.csv` | B (recintos SIC por destino) y D (denominador) |
| `data/curado/poi_accesibilidad.csv` | D |
| `data/referencia/destinos.csv` | Pueblo Mágico, municipios y centro turístico de cada destino |
| `data/referencia/geo/municipios-puebla.geojson` | Nombre de cada municipio |
| `data/fuentes/fuentes.csv` | Fecha de consulta y URL (metadatos) |

## Salidas

| Archivo | Contenido |
|---|---|
| `reports/013_participacion_llegadas.csv` | Llegadas y participación por centro y año |
| `reports/013_concentracion_anual.csv` | HHI, Gini y participación de capital + Cholula por año |
| `reports/013_ocupacion_estadia.csv` | Ocupación y estadía por centro y año |
| `reports/013_oferta_denue_municipio.csv` | Establecimientos por municipio y rama, con participación |
| `reports/013_concentracion_oferta.csv` | HHI y participación de capital + Cholula por rama |
| `reports/013_recintos_sic_destino.csv` | Recintos SIC por destino y categoría |
| `reports/013_desajuste_destinos.csv` | Oferta cultural frente a demanda, con candidatos |
| `reports/013_cobertura_accesibilidad_destino.csv` y `_categoria.csv` | Cobertura de información |
| `reports/figuras/013_*.svg` y `.png` | Gráficas |
| `reports/01_problema.md` | Hallazgos y cifras clave (lo escribe el script) |

## Criterio de desajuste (C)

Un destino es **candidato a destino alternativo** si cumple las dos condiciones:

1. **Oferta cultural relevante:** es Pueblo Mágico y tiene al menos un recinto cultural registrado (DENUE 7121 o SIC).
2. **Baja demanda hotelera:** su ocupación 2025 está por debajo de la del Estado en 2025.

Se ordena por oferta cultural registrada (desc.) y después por ocupación (asc.). La estadía se reporta, pero no discrimina: todos los centros están entre 1.7 y 1.9 días.

## Gráficas

Estilo sobrio: fondo claro, texto casi negro, rejilla tenue, etiquetas directas y tramas además del color (capital y Cholula en azul liso; Pueblos Mágicos en naranja con trama; otros en gris). Metadatos fijos en SVG y PNG para que la salida sea idéntica entre corridas.

## Verificación

- `uv run --project pipelines pytest analysis/tests` (HHI y participación contra cálculo a mano).
- `cd pipelines && uv run pytest`, `uv run ruff check . ../analysis` y `uv run ruff format --check . ../analysis`.
- Dos corridas seguidas producen los mismos SHA-256 en `reports/` y `docs/pitch/figuras/`.
