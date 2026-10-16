# Spec 013 · Análisis del problema

| | |
|---|---|
| Contexto | Análisis (lee `data/curado/` y `data/referencia/`; no escribe en `data/`) |
| Prioridad | P0 |
| Estado | Hecha: A–D con datos; E y F pendientes por falta de datos |
| Depende de | 002 (indicadores oficiales), 012 (catálogo del corredor) |
| Habilita | Entregable 2 (`docs/entregables/02_problema.md`), entregable 9 (evidencia de análisis y resultados) y el pitch |

## Bases que atiende

- Convocatoria: «Definición del problema y beneficiarios» y «Evidencia de análisis y resultados».
- Contexto maestro: §02.1, §02.3 (A–F), §02.4, §02.5 y §22 (entregables 2 y 9).
- Constitución III (cada cifra con procedencia) y VI (honestidad estadística).

## Objetivo

Medir con datos reales y reproducibles las cuatro piezas del problema: la demanda hotelera se concentra en pocos polos, la oferta también, hay destinos con oferta cultural y baja demanda, y casi no hay información de accesibilidad. Cada cifra sale de un script determinista y lleva fuente, fecha de consulta, denominador y limitaciones.

## Historias de usuario

**H1 (P0).** Como jurado, quiero ver cuánto se concentra la demanda hotelera y desde cuándo.
- Dado `data/curado/indicadores_oficiales_anual.csv`, cuando corre el análisis, entonces `reports/` tiene la participación de llegadas por centro turístico y el HHI y el Gini por año 2017–2026.

**H2 (P0).** Como Secretaría, quiero una lista ordenada de destinos alternativos con un criterio explícito.
- Dado el cruce de oferta cultural (DENUE 7121, SIC, Pueblo Mágico) y ocupación 2025, cuando corre el análisis, entonces `reports/013_desajuste_destinos.csv` marca candidatos y el reporte explica la regla.

**H3 (P0).** Como persona con una necesidad de movilidad, quiero saber cuánta información de accesibilidad existe.
- Dado `poi_accesibilidad.csv`, cuando corre el análisis, entonces el reporte muestra el % de POI con algún atributo por destino y categoría como «cobertura de información», nunca como «nivel de accesibilidad».

**H4 (P0).** Como equipo del pitch, quiero 4–6 cifras clave con su fuente y 3–4 gráficas listas.
- Dado `reports/01_problema.md`, cuando se abre, entonces tiene la sección «Cifras clave para el pitch» y las figuras están en `docs/pitch/figuras/`.

## Requisitos funcionales

- **FR-013-01** `analysis/01_problema.py` corre sin red, es determinista y escribe todo en `reports/` (tablas CSV con `float_format="%.4f"`, figuras SVG y PNG en `reports/figuras/` y `reports/01_problema.md`). Copia las figuras más fuertes a `docs/pitch/figuras/`.
- **FR-013-02** A) Participación por centro, HHI y Gini de llegadas por año; series anuales de ocupación y estadía por centro; capital y Cholula frente a Pueblos Mágicos.
- **FR-013-03** B) Establecimientos DENUE por municipio y rama, y su concentración; recintos SIC por destino.
- **FR-013-04** C) Tabla de desajuste oferta–demanda con criterio explícito.
- **FR-013-05** D) Cobertura de información de accesibilidad por destino y categoría, y de baños.
- **FR-013-06** E) y F) quedan documentados como pendientes: no hay datos descargados del Censo por AGEB ni de un modelo de elevación.
- **FR-013-07** `reports/01_problema.md` lo escribe el script; incluye «Cifras clave para el pitch».

## Definiciones

- **Participación** de un centro en un año: llegadas del centro / llegadas del Estado (`centro_ot = Estado`, que es la suma de los centros más «Resto del Estado»).
- **HHI**: suma de los cuadrados de las participaciones (escala 0–1; multiplicado por 10,000 en la escala usual) sobre un panel fijo de centros con serie completa 2017–2026. Las participaciones se normalizan dentro del panel. «Resto del Estado» no entra porque agrega muchos centros.
- **Gini**: coeficiente de Gini de las llegadas sobre el mismo panel.
- **Oferta cultural registrada** de un destino: establecimientos DENUE SCIAN 7121 en sus municipios más recintos del SIC dentro de su zona del catálogo (spec 012).

## Fuera de alcance

- Inferir causas: una correlación no es causa.
- E) Censo 2020 por AGEB (PCDISC_MOT) y F) pendiente con DEM: no hay datos en el repositorio. Se harán cuando exista una spec de ingesta.

## Preguntas abiertas

- 2026-10-16. El script lee `data/fuentes/fuentes.csv` solo para tomar la fecha de consulta y la URL de cada fuente (metadatos, no datos). Es la opción conservadora: así ninguna fecha se escribe a mano.
- 2026-10-16. Acatzingo y Tepeaca solo tienen serie desde 2025. Para comparar años, el HHI y el Gini usan el panel de 16 centros con serie completa; las participaciones sobre el Estado sí incluyen a los 18.
- 2026-10-16. Los recintos del SIC por destino se cuentan solo dentro de las zonas del catálogo (círculo de 1.5 km o corredor), porque `data/curado/` no tiene el SIC estatal completo.
