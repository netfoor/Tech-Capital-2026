# Plan 015 · Recomendador inclusivo

## Enfoque

El recomendador es un problema de **orienteering con ventanas de tiempo y restricciones duras**: elegir qué lugares visitar y en qué orden para maximizar la utilidad dentro del tiempo disponible, sin violar nunca una necesidad de acceso. Se resuelve en cuatro etapas (contexto maestro, §10.1) con código puro de Python, determinista y sin servicios externos.

## Archivos

| Archivo | Contenido |
|---|---|
| `backend/app/recommender/tipos.py` | Contrato con la spec 014: solicitudes, candidatos, paradas y respuestas |
| `backend/app/recommender/config.py` | Pesos, velocidades, estancias por categoría y umbrales, documentados |
| `backend/app/recommender/geo.py` | Haversine, tiempo peatonal y celda de zona |
| `backend/app/recommender/horarios.py` | Parser conservador de `opening_hours` |
| `backend/app/recommender/elegibilidad.py` | Etapa 1: filtros duros y clasificación de lugares sin dato |
| `backend/app/recommender/ranking.py` | Etapa 2: TF-IDF de intereses y puntuación multiobjetivo |
| `backend/app/recommender/secuencia.py` | Etapa 3: simulador de línea de tiempo, inserción voraz y 2-opt |
| `backend/app/recommender/explicacion.py` | Etapa 4: motivos, datos desconocidos y resumen |
| `backend/app/recommender/motor.py` | `recomendar()` |
| `backend/app/recommender/multidia.py` | `planear_multidia()` |
| `backend/app/recommender/baselines.py` | Popularidad, cercanía y popularidad con filtro ingenuo |
| `backend/app/recommender/verificador.py` | Verificador independiente de restricciones para pruebas y evaluación |
| `backend/app/recommender/carga.py` | Lectura de `poi.csv` y `poi_accesibilidad.csv` (contrato de la spec 012) |
| `analysis/02a_catalogo_sintetico.py` | Genera el catálogo sintético de prueba en `backend/tests/datos/` |
| `analysis/02_eval_recomendador.py` | Evaluación offline contra baselines |

## Decisiones

- **Dato confiable**: `valor=si` con estado `verificado`, o `sin_verificar` con confianza ≥ 0.6. `valor=no`, `limitado` o estado `reportado` excluyen siempre. Sin dato (o confianza baja) no entra en la ruta y se ofrece como alternativa «sin verificar».
- **Descansos**: el simulador lleva un contador de actividad continua (caminar, visitar o esperar menos que un descanso). Si una actividad lo rebasa, inserta un descanso de 10 min antes; parte caminatas y visitas largas con pausas.
- **Baños**: el contador se reinicia al llegar y al salir de un lugar con baño accesible confiable. Si el siguiente tramo lo rebasa, se inserta el baño confiable que menos desvía; si no hay, la ruta no es factible. El punto de partida cuenta como acceso.
- **Pertinencia**: TF-IDF propio sobre nombre, categoría (peso doble), subcategoría y descripción, con expansión de intereses a un vocabulario controlado. Coseno normalizado al máximo del catálogo.
- **Selección**: en cada paso se inserta el candidato y la posición con mayor `utilidad / (Δt + 1)^0.5`; la utilidad se ajusta con penalización por repetir zona o categoría (diversidad tipo MMR). Después de cada inserción, 2-opt sobre el orden.
- **Multi-día**: k = días; k-means++ con semilla 2026, asignación por arrepentimiento con capacidad de horas por día, secuenciación por día y reubicación de lo que no cupo.
- **Verificador independiente**: recalcula las violaciones desde la línea de tiempo y el catálogo, sin usar la lógica del simulador. Es la fuente de verdad de pruebas y evaluación.

## Pruebas

- `backend/tests/test_recomendador_horarios.py`: formatos válidos, días, `off`, `24/7` y casos no interpretables.
- `backend/tests/test_recomendador_motor.py`: elegibilidad, presupuesto, tiempo, explicación, determinismo y alternativas.
- `backend/tests/test_recomendador_propiedades.py`: cientos de solicitudes aleatorias con semilla; 0 violaciones indispensables.
- `backend/tests/test_recomendador_multidia.py`: sin duplicados, capacidad por día, motivos y métricas.
- `backend/tests/test_recomendador_baselines.py`: las baselines corren y el verificador detecta sus violaciones.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Distancia en línea recta subestima la caminata real | Factor de desvío 1.3 y velocidad conservadora; OSMnx como mejora |
| Catálogo real con pocos datos de accesibilidad: rutas cortas | Se informa como resultado y como brecha (spec 019), no se relaja la restricción |
| Pertinencia evaluada con la misma similitud que la optimiza | Se reporta como métrica interna, con esa advertencia |
