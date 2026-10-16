# Plan 019 · Tablero institucional

## Enfoque

El tablero lee tres cosas: la serie oficial ya cargada en `analytics.aggregate_metric` (Oferta–demanda), el catálogo de `core` (Inclusión) y, solo como agregados, las tablas de `private` (Panorama y Experiencia). Toda la lógica de cálculo vive en `app/services/metricas.py`, con funciones puras que se prueban contra valores calculados a mano. El router `app/api/b2b.py` solo valida parámetros, aplica el rol y da formato JSON o CSV.

## Archivos

| Archivo | Contenido |
|---|---|
| `backend/metrics/definitions.yaml` | Ficha semántica de cada indicador (§09) |
| `backend/app/services/definiciones.py` | Lectura del YAML y carga a `core.metric_definition` y `core.data_lineage` |
| `backend/app/services/metricas.py` | Oferta–demanda, Inclusión, Panorama, Experiencia, supresión k, intervalos y linaje |
| `backend/app/api/b2b.py` | `GET /b2b/supply-demand`, `/b2b/accessibility-gaps`, `/b2b/metrics` y `GET /metrics/{id}/lineage`; `?formato=csv` |
| `backend/app/services/demo_tablero.py` | Usuario analista de demo y datos sintéticos etiquetados |
| `frontend/src/admin/` | Tablero: sesión, módulos, gráficos SVG, ficha, tabla alternativa y moderación |

## Decisiones

- **Rol lector.** `viewer`, `analista` y `admin` (`requiere_rol`). La cola de moderación conserva la regla de 014 (`analista`, `admin`); el tablero la oculta a `viewer`.
- **Ventana de 12 meses.** Los 12 últimos periodos en que el Estado tiene llegadas mayores que cero. La ocupación se pondera (Σ ocupados / Σ disponibles), no es el promedio de porcentajes. Cuartos libres por día = (Σ disponibles − Σ ocupados) / días de la ventana. Estadía = Σ turistas noche / Σ llegadas. El crecimiento exige 12 meses con dato en ambas ventanas.
- **HHI.** Σ (100 · sᵢ)², con sᵢ la participación de cada centro con `nivel = destino` en las llegadas. Escala 0–10 000. Serie anual con el número de meses de cada año (2026 es parcial).
- **Supresión.** n = personas distintas del grupo. Si n < k: `suprimido = true`, `valor = null`. Supresión complementaria si en una partición queda un único suprimido.
- **Sintético.** Cada consulta agrupa por `is_synthetic` de la fila de hecho (visita, reseña, caso); la respuesta separa los grupos y el tablero los dibuja en bloques distintos con la banda.
- **Incertidumbre.** Media por dimensión con bootstrap percentil del 95 % (1 000 remuestreos, semilla 2026); proporción de calificaciones bajas (≤ 2) con intervalo de Wilson.
- **CSV.** Líneas de metadatos `# clave: valor` y después la tabla. Con `float_format` de cuatro decimales.
- **Gráficos.** SVG propio sin dependencias: barras horizontales y líneas. Cada gráfico tiene `<title>`, `<desc>`, texto con el valor (no solo color) y un botón «Ver tabla de datos».

## Pruebas

- `tests/test_metricas.py`: HHI y ocupación contra un fixture pequeño calculado a mano; crecimiento sin evidencia cuando faltan meses; candidatos; Wilson y bootstrap.
- `tests/test_tablero.py`: autorización (sin cuenta 401, visitante 403, viewer 200); supresión k; supresión complementaria; ninguna respuesta con coordenadas, `user_id` ni correos; separación sintético/real; CSV con metadatos; linaje.
- `frontend/src/admin/*.test.tsx`: inicio de sesión, módulos, banda sintética, supresión visible y tabla alternativa.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Sin catálogo real (012 aún no integrado) | Oferta–demanda no depende del catálogo; Inclusión dice «sin catálogo cargado» |
| Sin personas reales en la base | Panorama y Experiencia muestran «sin evidencia suficiente» en lo real y el bloque sintético aparte |
| Reconstrucción por diferencias | Supresión complementaria y sin totales que incluyan grupos suprimidos |
