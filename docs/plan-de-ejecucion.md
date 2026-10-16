# Plan de ejecución · Puebla Viva 360

Orden de trabajo, dependencias y carriles. El producto está definido en [`producto/contexto-maestro.txt`](producto/contexto-maestro.txt); las secciones citadas (§NN) son de ese documento.

## Specs

| Spec | Qué | Prioridad | Depende de |
|---|---|---|---|
| 001 Catálogo de destinos | 12 Pueblos Mágicos con claves INEGI (reutilizada) | P0 | — |
| 002 Indicadores oficiales | Serie hotelera 2017–2026 (reutilizada) | P0 | 001 |
| 012 Ingesta y catálogo del corredor | DENUE, SIC, OSM y Pueblos Mágicos → POI con accesibilidad; `data_catalog.csv`, fichas de fuente y reporte de calidad (§08) | P0 | 001 |
| 013 Análisis del problema | Concentración hotelera (HHI), oferta, desajuste y brecha de información de accesibilidad (§02.3) | P0 | 002, 012 |
| 014 API y modelo de datos | Entidades (§13.2), endpoints P0 (§13.3), JWT con roles | P0 | fundación |
| 015 Recomendador inclusivo | Elegibilidad dura, ranking, secuenciación, explicación, multi-día; baselines y evaluación (§10.1) | P0 | 012, 014 |
| 016 PWA del visitante | Lista y mapa, ficha, guardar en mi mapa, planear, recorrido, bitácora y reseña (§05) | P0 | 014 |
| 017 Recorridos y visitas | Sesión consentida, muestras, detección de paradas, visitas con confianza, trazas sintéticas (§07) | P0 | 014 |
| 018 Reseñas, barreras y moderación | Reseña por dimensiones, reporte de barrera, moderación que actualiza la ficha (§06.8) | P0 | 014 |
| 019 Tablero institucional | Panorama, Experiencia, Inclusión y Oferta–demanda; `backend/metrics/definitions.yaml`; agregados con k (§09, §11) | P0 | 013, 017, 018 |
| 020 Privacidad, seguridad y accesibilidad | Consentimientos, ARCO, EXIF, pruebas de autorización, axe y WCAG 2.2 AA (§06.1, §14) | P0 | 016 |
| 021 Servidor MCP | `get_destination_metrics`, `get_accessibility_gaps`, `get_data_lineage` (§11) | P1 | 019 |
| 022 Importar, compartir e intención | Pegar enlace, Web Share Target, enlace de solo lectura, intención → visita (§04.4, §09.I) | P1 | 016, 019 |
| 023 Entregables y pitch | Documentos de la §9 de la convocatoria, guion, preguntas y respaldo sin conexión (§22, §23) | P0 | todas |

## Carriles paralelos

| Carril | Specs |
|---|---|
| Datos | 012 → 013 |
| Backend | 014 → 017, 018 → 019 → 021 |
| Inteligencia | 015 |
| Frontend | 016 → 020, 022 |
| Entrega | 023 (empieza en cuanto haya resultados de 013) |

## Ruta crítica para la demo

**fundación → 012 → 014 → 015 → 016 → 018 → 019 → 023**

La escena de valor (§06.8) recorre todas: ruta con restricciones → reporte de barrera → moderación → la ficha cambia → el tablero muestra la brecha → la siguiente recomendación la considera.

## Reglas de coordinación

1. Cada spec se trabaja en su rama (`feat/NNN-nombre`) y entra a `main` por pull request.
2. La primera commit de la rama crea o completa `spec.md`, `plan.md` y `tasks.md` de su carpeta.
3. Si cambia el modelo de datos o un endpoint, el PR lo dice en su descripción con `contrato:`.
4. Nada entra a `main` sin pasar `make verificar` y la CI.
5. `STATUS.md` se actualiza en cada PR.
