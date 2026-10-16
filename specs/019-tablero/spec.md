# Spec 019 · Tablero institucional

| | |
|---|---|
| Contexto | Consola B2B para la Secretaría: agregados protegidos con ficha metodológica y linaje |
| Prioridad | P0 |
| Estado | Hecha (P0): cuatro módulos, linaje, CSV, moderación y semilla de demostración; Panorama y Experiencia muestran por ahora solo datos sintéticos etiquetados |
| Depende de | 014 (modelo y API), 002 (serie oficial); usa lo que dejen 012, 017 y 018 cuando existan |
| Habilita | 021 (MCP), 022 (intención → visita) |

## Bases que atiende

- §3 de la convocatoria: decisiones basadas en evidencia y distribución de los beneficios del turismo (módulo Oferta–demanda con destinos alternativos).
- §5: datos con procedencia (`metrics/definitions.yaml`, `core.metric_definition`, `core.data_lineage`), calidad y privacidad (supresión k).
- §8: prototipo demostrable desde el día 1 con datos públicos reales y, aparte, un conjunto sintético etiquetado.
- Turismo accesible e incluyente: módulo Inclusión con brechas de información de accesibilidad (§06.7) y el circuito cerrado de moderación (§06.8).

## Objetivo

Dar a la Secretaría un tablero en `/admin` con cuatro módulos (§09): **Panorama**, **Experiencia**, **Inclusión** y **Oferta–demanda**. Cada gráfico muestra su ficha metodológica (fórmula, n, fuente y limitación) y una tabla de datos alternativa. La Secretaría ve agregados, nunca personas: todo indicador que sale de personas suprime los grupos con menos de k personas (constitución XI) y lo sintético nunca se mezcla con lo real (constitución XII).

## Historias de usuario

**H1 (P0).** Como analista de la Secretaría, quiero ver dónde se concentra la demanda hotelera y qué destinos tienen cuartos libres, para orientar la promoción a destinos alternativos.
- Dado la serie oficial cargada, cuando pido `GET /b2b/supply-demand`, entonces veo por destino la ocupación de los últimos 12 meses publicados, los cuartos libres por día, la estadía, el crecimiento de llegadas y su participación; el índice Herfindahl-Hirschman (HHI) de llegadas por centro turístico con su serie anual; y la lista de candidatos a destino alternativo con la regla que los eligió. Cada cifra dice si es medida o derivada.

**H2 (P0).** Como analista, quiero saber qué tan completa es la información de accesibilidad del catálogo y qué barreras reporta la gente.
- Dado el catálogo, cuando pido `GET /b2b/accessibility-gaps?corredor_id=…`, entonces veo el porcentaje de lugares con información de accesibilidad (cobertura de información, no nivel de accesibilidad), por atributo y por estado, las barreras reportadas y aceptadas, el tiempo de moderación y prioridades sugeridas.

**H3 (P0).** Como analista, quiero ver visitas observadas, permanencia y satisfacción sin poder identificar a nadie.
- Dado `GET /b2b/metrics?modulo=panorama|experiencia`, entonces cada grupo trae `n`, cobertura e incertidumbre; los grupos con menos de k personas aparecen como suprimidos y sin valor; las filas sintéticas y reales van en grupos separados y marcados.

**H4 (P0).** Como revisor o jurado, quiero ver de dónde sale cada cifra.
- Dado `GET /metrics/{metric_id}/lineage`, entonces veo la ficha semántica del indicador, sus fuentes con URL, fecha de consulta y SHA-256, y el método de cálculo.

**H5 (P0).** Como analista, quiero moderar reportes de barrera desde el tablero y ver la brecha cambiar (§06.8).
- Dado un caso abierto en la cola, cuando lo acepto, entonces sale de la cola, el atributo cambia y el módulo Inclusión cuenta la barrera aceptada.

**H6 (P0).** Como analista, quiero exportar los datos de un módulo con sus metadatos.
- Dado `?formato=csv`, entonces recibo un CSV cuyas primeras líneas (`# …`) dicen indicador, fuente, versión, k, fecha de cálculo y si los datos son sintéticos.

## Requisitos funcionales

- **FR-019-01** `metrics/definitions.yaml` con la ficha semántica de §09 por indicador: `id`, `nombre`, `pregunta`, `formula`, `unidad`, `numerador`, `denominador`, `filtros`, `fuentes`, `frecuencia`, `cobertura`, `limitaciones`, `k_minimo`, `decision_potencial`, `procedencia`, `modulo` y `version`.
- **FR-019-02** Carga idempotente de las fichas a `core.metric_definition` y de sus fuentes a `core.data_lineage` (`entidad = metric_definition`). La semilla de 014 la llama después de la serie oficial.
- **FR-019-03** `GET /b2b/supply-demand` con datos públicos de `analytics.aggregate_metric` (serie de la spec 002): ocupación ponderada de los últimos 12 meses publicados, cuartos libres por día, estadía, crecimiento contra los 12 meses previos, participación, HHI de llegadas (12 meses y serie anual), serie mensual de ocupación, POI del catálogo por destino y candidatos a destino alternativo.
- **FR-019-04** `GET /b2b/accessibility-gaps?corredor_id=` con cobertura de información por destino, atributo y estado; barreras reportadas y aceptadas; tiempo mediano de moderación; prioridades sugeridas generadas desde los datos.
- **FR-019-05** `GET /b2b/metrics?modulo=panorama` (visitas observadas, visitantes distintos, permanencia mediana y cuartiles, cobertura y confianza) y `?modulo=experiencia` (satisfacción media por dimensión con intervalo bootstrap del 95 % y proporción de calificaciones bajas con intervalo de Wilson).
- **FR-019-06** Supresión k con `K_MINIMO` del entorno: un grupo con menos de k personas distintas sale con `suprimido = true` y sin valor. Si en una partición queda un solo grupo suprimido, se suprime también el siguiente más pequeño (supresión complementaria, §14).
- **FR-019-07** Ningún agregado mezcla filas sintéticas y reales: cada grupo lleva `is_synthetic` y se calcula solo con filas de ese tipo.
- **FR-019-08** `GET /metrics/{metric_id}/lineage`.
- **FR-019-09** `?formato=csv` en los cuatro endpoints de `/b2b`, con metadatos en líneas `#`.
- **FR-019-10** Autorización: `viewer`, `analista` y `admin` leen el tablero; `visitante` o sin cuenta recibe 403 o 401. La moderación sigue en `analista` y `admin` (spec 014).
- **FR-019-11** Tablero en `/admin` (`frontend/src/admin/`): inicio de sesión, cuatro módulos, cola de moderación, vista ejecutiva y vista técnica, banda «DATOS SINTÉTICOS DE DEMOSTRACIÓN» cuando un bloque es sintético, ficha metodológica y tabla de datos junto a cada gráfico.
- **FR-019-12** Semilla de demostración (`uv run python -m app.services.demo_tablero`): usuario analista con credenciales del entorno (`DEMO_ANALISTA_CORREO`, `DEMO_ANALISTA_CONTRASENA`) y personas, visitas, reseñas y reportes sintéticos (`is_synthetic = true`) con n ≥ k en algunos destinos y n < k en otro para mostrar la supresión.

## Requisitos no funcionales

- Ninguna respuesta del tablero trae coordenadas, `user_id`, correos, nombres ni texto de reseñas o reportes (salvo la descripción del reporte en la cola de moderación, que ya expone la spec 014 solo a moderadores).
- Resultados deterministas: el bootstrap usa semilla fija.
- Gráficos en SVG propio, con `role="img"`, título, descripción y tabla alternativa; navegación completa con teclado; nada depende solo del color (WCAG 2.2 AA).
- No se crean tablas nuevas: los agregados de personas se calculan al pedirlos desde `private` y solo sale el agregado.

## Fuera de alcance

- Módulos Flujos, Economía local, Sostenibilidad, Evaluación e Intención (P1/P2 de §09).
- Mapa del tablero y exportación PDF (P1).
- Servidor MCP (spec 021).

## Preguntas abiertas

- 2026-10-16. `core.metric_definition` no tiene columnas para toda la ficha de §09 (pregunta, numerador, filtros, cobertura, limitaciones, decisión). Para no abrir una migración en paralelo con 017, la tabla guarda nombre, descripción (la pregunta), fórmula, versión, unidad, denominador, procedencia, fuente principal y k; la ficha completa se sirve desde `metrics/definitions.yaml`, que está versionado. Si 021 necesita consultarla en SQL, se agrega una columna `ficha` JSONB.
- 2026-10-16. El HHI de llegadas se calcula sobre los centros turísticos con `nivel = destino`. «Resto del Estado» se excluye porque agrupa muchos municipios (contarlo como un centro inflaría el índice) y los subcentros de Cholula se excluyen porque ya están dentro de Cholula. La respuesta reporta la cobertura (llegadas de los centros entre llegadas del Estado). Acatzingo y Tepeaca solo tienen datos desde 2025: entran al índice desde ese año y su crecimiento sale como «sin evidencia suficiente».
- 2026-10-16. Ocupación, estadía y cuartos libres se calculan sobre valores medidos de la fuente (cuartos, llegadas y turistas noche), así que se marcan `medido`; la afluencia y la derrama los marca la fuente como derivados y así se muestran.
- 2026-10-16. Candidato a destino alternativo (regla v1): ocupación de 12 meses menor que la del Estado y cuartos libres por día mayores o iguales que la mediana de los destinos. Es una señal para revisar, no una recomendación causal.
- 2026-10-16. La k se aplica a indicadores que salen de personas (visitas, reseñas, reportes). La cobertura de información de accesibilidad describe lugares, no personas: se reporta con su n de lugares y sin supresión.
- 2026-10-16. Los agregados de Panorama y Experiencia se calculan al pedirlos en vez de guardarse en `analytics.aggregate_metric`, para no chocar con el pipeline de visitas de 017. Cuando 017 materialice la permanencia, el tablero puede leerla de ahí.
- 2026-10-16. Los reportes de barrera y los atributos que tocan un lugar sintético se cuentan en el bloque sintético aunque la persona que reporta sea real: lo que toca algo sintético se marca sintético.
- 2026-10-16. Pendiente (P1): selector de corredor en Inclusión (el endpoint ya acepta `corredor_id`), filtro de periodo en Panorama, mapa del tablero y exportación PDF.
- 2026-10-16. Las pruebas pueden usar otra base con `BASE_PRUEBAS` (por omisión `pueblaviva_test`) para que varias ramas corran pruebas a la vez.
