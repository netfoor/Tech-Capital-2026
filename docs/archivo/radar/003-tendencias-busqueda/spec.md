# Spec 003 · Tendencias de búsqueda

| | |
|---|---|
| Contexto | Atención digital |
| Prioridad | P0 |
| Estado | Pendiente (acceso verificado desde una red residencial el 2026-10-15) |
| Depende de | 001 (términos y, en P1, temas de Trends) |
| Habilita | 008 (componente de búsqueda y modelo con rezago) |

## Bases que atiende

DAT-01, DAT-03 y DAT-04, RUB-02, CAT-DAT («indicadores o predicciones»), H2 de la visión.

## Objetivo

Obtener una serie mensual comparable del interés de búsqueda de cada destino en México, de enero de 2017 al último mes cerrado. Sirve para medir la atención por destino y para probar si anticipa las llegadas de turistas.

## Historias de usuario

**H1 (P0).** Como analista, quiero el interés de búsqueda mensual de los 12 Pueblos Mágicos en una misma escala.
- Dado el catálogo, cuando corre `uv run radar senales trends`, entonces `interes_busqueda_mensual.csv` tiene una serie por destino con `interes_ajustado` comparable entre destinos (todos reescalados al mismo término ancla).

**H2 (P0).** Como revisor, quiero poder reconstruir cada número.
- Dada una fila, cuando busco su `consulta_id`, entonces existe la respuesta cruda en `data/crudo/trends/` con términos, región, rango de fechas y fecha de consulta.

**H3 (P1).** Como analista, quiero saber cuánto varía Trends entre consultas para no sobreinterpretar.
- Dado un lote repetido otro día, cuando se comparan, entonces se reporta su correlación y su diferencia media.

**H4 (P1).** Como Secretaría, quiero el interés desde los mercados del Tianguis.
- Dada la región `US`, cuando se consulta, entonces existe la serie en esa región para los destinos con volumen suficiente.

## Requisitos funcionales

- **FR-003-01** Lotes de hasta 5 términos, cada uno con el término ancla (`Cholula` por defecto, configurable).
- **FR-003-02** Destinos de bajo volumen (interés del ancla de 0 a 1 en el lote): **ancla de segundo nivel** encadenada. Por ejemplo, con Cuetzalan reescalado previamente contra Cholula.
- **FR-003-03** Reescalado por lote: `factor = media(ancla en el lote de referencia) / media(ancla en el lote)` sobre todo el rango, y `interes_ajustado = interes × factor`. La media del rango es más estable que el cociente de un solo mes.
- **FR-003-04** Respuestas crudas en `data/crudo/trends/<consulta_id>.json` y tabla curada versionada.
- **FR-003-05** Pausa configurable entre lotes (60 s por defecto) y hasta 3 reintentos con espera exponencial ante error 429.
- **FR-003-06** Reproducción del hallazgo exploratorio: pico de noviembre en Chignahuapan frente a su afluencia oficial (gráfica para la spec 011).
- **FR-003-07** (P1) Región `US` y repetición de lotes para medir la variabilidad.

## Requisitos no funcionales

- Se ejecuta desde una red residencial (ADR-0008); desde la nube no se intenta.
- Todos los lotes de una corrida usan el mismo rango de fechas y la misma zona horaria (`tz=360`).

## Fuera de alcance

- Interés semanal o diario.
- Consultas relacionadas o temas en ascenso (se pueden explorar después).

## Preguntas abiertas

- Si la capital se incluye, «Puebla» es ambiguo. Se usa el tema de la ciudad si la T001-07 lo encuentra; si no, la capital queda fuera de este componente.
