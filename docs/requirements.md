# Matriz de requisitos

Cada requisito de la convocatoria, la funcionalidad que lo atiende y cómo se comprueba. La convocatoria manda ([`bases/convocatoria-hackathon-puebla-turistica-360.pdf`](bases/convocatoria-hackathon-puebla-turistica-360.pdf)).

## Reto y objetivos (§2, §3)

| Requisito | Funcionalidad | Spec | Criterio de aceptación |
|---|---|---|---|
| Usar datos abiertos, IA y ciencia de datos | Catálogo multi-fuente, recomendador y análisis del problema | 012, 013, 015 | Al menos 4 fuentes externas documentadas más datos propios |
| Mejorar la experiencia antes, durante y después | Guardar y planear (antes), recorrido y check-in (durante), bitácora y reseña (después) | 016, 017, 018 | Las tres fases se recorren en la demo |
| Comprender y optimizar flujos | Visitas observadas, permanencia y destinos alternativos | 017, 019 | El tablero muestra permanencia con n y advertencia de muestra |
| Distribuir los beneficios | Término de diversidad territorial en el ranking; módulo Oferta–demanda | 015, 019 | La evaluación reporta la cobertura de destinos alternativos contra los baselines |
| Turismo accesible e incluyente | Atributos de accesibilidad verificables, restricciones duras y WCAG 2.2 AA | 012, 015, 020 | 0 violaciones de restricciones indispensables; axe sin errores en los flujos P0 |
| Decisiones basadas en evidencia | Tablero con fichas metodológicas y linaje | 019, 021 | Cada indicador tiene fórmula, denominador, fuente y k |

## Datos (§5)

| Requisito | Funcionalidad | Spec | Criterio |
|---|---|---|---|
| Proponer, obtener, documentar y justificar los datos | `data/catalog/data_catalog.csv` y `docs/source_cards.md` | 012 | Cada fuente con URL, licencia, fecha, campos, calidad, sesgos y script |
| Explicar preparación y procesamiento | Pipeline reproducible y `reports/calidad_datos.md` | 012 | `make datos` regenera todo; el reporte trae conteos, nulos, duplicados y matches |
| Respetar licencias, términos y privacidad | Atribución OSM y SIC; sin scraping; datos personales en `private` | 012, 020 | Atribución visible; prueba de que ninguna respuesta pública trae GPS crudo |
| Justificar la IA | Model cards del recomendador y de temas | 015 | Comparación contra baselines de popularidad y cercanía |

## Entregables y evaluación (§8, §9, §11, §16)

| Requisito | Funcionalidad | Spec | Criterio |
|---|---|---|---|
| Prototipo funcional o demostrable | `make demo` con datos semilla | todas | La demo de §17 corre de punta a punta sin conexión |
| Entregables de la §9 | [`ENTREGABLES.md`](ENTREGABLES.md) | 023 | Cada fila apunta a un archivo existente |
| Explicar qué componentes usan IA y sus límites (§16) | `docs/ia/` | 015, 023 | Una ficha por componente con función, datos, resultados y limitaciones |
| Viabilidad y escalamiento (§11) | `docs/viabilidad.md` con costos por escenario | 023 | Supuestos explícitos; fuentes nacionales replicables |
