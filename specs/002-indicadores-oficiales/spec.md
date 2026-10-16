# Spec 002 · Indicadores oficiales

| | |
|---|---|
| Contexto | Desempeño turístico |
| Prioridad | P0 |
| Estado | En curso: ingesta y validaciones listas |
| Depende de | 001 |
| Habilita | 008, 009, 011 |

## Bases que atiende

DAT-01 a DAT-04 (§5: fuente oficial, calidad, preparación y procedencia), RUB-02, CAT-DAT (reproducibilidad) y ENT-04 a ENT-06.

## Objetivo

Tener la serie mensual oficial 2017–2026 de cada destino como tabla limpia, con la procedencia de cada indicador (medido o derivado) y comprobaciones que demuestren que la lectura del PDF es exacta.

## Historias de usuario

**H1 (P0).** Como analista, quiero la serie mensual por destino e indicador para calcular el desempeño de los últimos 12 meses.
- Dado el PDF del Observatorio Turístico, cuando corre `uv run radar indicadores`, entonces se escribe `indicadores_oficiales_mensual.csv` con 22 centros, 9 indicadores y periodos de 2017-01 al último mes publicado.

**H2 (P0).** Como jurado o revisor, quiero confiar en que los números corresponden a la fuente.
- Dado el PDF, cuando se suman los meses de cada indicador aditivo, entonces coinciden con el «Acumulado» del PDF, salvo los meses en blanco de la fuente, que se reportan como huecos.
- Dado un mes con cuartos, la ocupación coincide con ocupados entre disponibles (±0.6 puntos).

**H3 (P0).** Como analista, quiero saber qué indicadores son medidos y cuáles derivados para no presentar una estimación como si fuera medición.
- Dado el glosario del PDF, cuando se ingiere, entonces afluencia y derrama quedan como `derivado` y el resto como `medido`.

**H4 (P0).** Como equipo, quiero documentar cómo se deriva la afluencia.
- Dado el resultado, cuando corre la ingesta, entonces `factor_afluencia_por_centro.csv` reporta el factor más frecuente y la proporción de meses que lo usan.

**H5 (P1).** Como Secretaría, quiero actualizar la serie cuando se publique un PDF nuevo sin tocar código.
- Dado un PDF nuevo registrado en `fuentes.csv`, cuando se cambia `FUENTE_ID` (o se pasa `--fuente`), entonces la ingesta corre igual y la comparación con la versión anterior reporta las diferencias.

## Requisitos funcionales

- **FR-002-01** Lectura del PDF con `pdfplumber` (tabla de 16 columnas por página).
- **FR-002-02** Corrección de nombres cortados o mezclados en celdas: «Cd.Puebla», «Izúcar de Matamo», «rCousartos disponibles».
- **FR-002-03** Exclusión de meses no publicados del último año: después del último mes con llegadas mayores que cero en «Estado».
- **FR-002-04** Tablas `indicadores_oficiales_mensual.csv`, `indicadores_oficiales_anual.csv` y `factor_afluencia_por_centro.csv` con las columnas de `docs/dominio/modelo-de-datos.md`.
- **FR-002-05** Comprobaciones: acumulados, unicidad, coherencia de la ocupación y SHA-256 de la fuente.
- **FR-002-06** (P1) Opción `--fuente <fuente_id>` y reporte de diferencias contra la tabla anterior.

## Requisitos no funcionales

- La ingesta completa tarda menos de 60 segundos en una laptop.
- El resultado es determinista: la misma fuente produce la misma SHA-256 de salida.

## Fuera de alcance

- Datos por establecimiento o por categoría de hotel (no se publican).
- Imputar meses faltantes.

## Preguntas abiertas

- Confirmar con la Secretaría el método de la afluencia: el factor 2.222 (3.333 en la capital) y si existe una medición directa de excursionistas.
