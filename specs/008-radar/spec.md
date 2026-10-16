# Spec 008 · Radar

| | |
|---|---|
| Contexto | Análisis (núcleo) |
| Prioridad | P0 (índices, brecha y cuadrantes) · P1 (modelo con rezago y escenarios de derrama) |
| Estado | Pendiente |
| Depende de | 002, y al menos dos de 003, 004, 005 y 006 |
| Habilita | 009 y 011 |

## Bases que atiende

RUB-02 y CAT-DAT («transformar los datos en conocimiento accionable»), RUB-05 y FIN-11 (impacto), OBJ-04, OBJ-05 y OBJ-07, CAT-SOS (desconcentración de flujos) y H1 y H2 de la visión.

## Objetivo

Para cada Pueblo Mágico, poner en una misma vista cuánta atención digital recibe y cómo le va realmente. A partir de eso se clasifica en un cuadrante con una recomendación distinta, y en P1 se estima cuánto podría crecer su derrama y si la atención anticipa las llegadas.

## Historias de usuario

**H1 (P0).** Como área de promoción, quiero ver qué destinos tienen poca atención para su desempeño.
- Dados los componentes disponibles, cuando corre `radar radar calcular`, entonces `radar_destinos.csv` tiene para los 12 Pueblos Mágicos el índice de atención, el índice de desempeño, la brecha y el cuadrante, junto con los componentes y su n.

**H2 (P0).** Como funcionario, quiero entender por qué un destino está en un cuadrante.
- Dado un destino, cuando consulto su fila, entonces veo cada componente en percentil, su valor bruto y la regla de corte. Si quitar un componente cambia su cuadrante, se marca como «sensible».

**H3 (P0).** Como jurado, quiero ver que los índices no son una caja negra.
- Dado el método, cuando leo «Cómo se hizo», entonces encuentro las fórmulas de esta spec y la tabla de componentes.

**H4 (P1).** Como Secretaría, quiero saber cuánto podría crecer un destino con capacidad disponible.
- Dado un destino con ocupación por debajo de la mediana de los Pueblos Mágicos, cuando se calcula el escenario, entonces `escenarios_derrama.csv` da los cuartos, turistas, visitantes y derrama adicionales por mes si alcanzara la mediana, con la metodología de la Secretaría y los supuestos explícitos.

**H5 (P1).** Como analista, quiero saber si el interés de búsqueda anticipa las llegadas.
- Dados el interés de búsqueda y las llegadas, cuando se evalúa con origen móvil, entonces `modelo_rezago.csv` dice por destino si el modelo mejora a la línea base estacional y en cuánto.

## Definiciones

**Universo.** Los 12 Pueblos Mágicos. La capital se muestra como referencia y no entra en los percentiles.

**Periodo de referencia.** Los últimos 12 meses publicados por el observatorio. Hoy son de 2025-07 a 2026-06.

**Desempeño**
- `ocupacion_12m` = Σ cuartos ocupados / Σ cuartos disponibles × 100 en el periodo de referencia.
- `cuartos_libres_dia_12m` = Σ (disponibles − ocupados) / días del periodo.
- `crecimiento_llegadas_pct` = llegadas de los 12 meses / llegadas de los 12 previos − 1.
- `indice_desempeno` = percentil de `ocupacion_12m` entre los 12.

**Componentes de atención** (percentil entre los 12, con empates promediados; `pctl = (rango − 1) / (n − 1) × 100`)

| Componente | Valor bruto | Fuente |
|---|---|---|
| `atencion_busqueda` | Media de `interes_ajustado` (MX) en el periodo de referencia | 003 |
| `atencion_video` | Proporción de resultados de las consultas genéricas de YouTube que mencionan el destino | 004 |
| `atencion_panel` | `presencia_pct` del panel | 005 |
| `atencion_asistentes` | `visibilidad_pct` en el brazo controlado, todas las corridas | 006 |

- `indice_atencion` = media de los percentiles disponibles; requiere al menos 2 componentes.
- `brecha` = `indice_atencion − indice_desempeno`.

**Cuadrantes.** El corte de cada índice es su mediana entre los 12, para que queden 6 y 6. En el desempeño, que es un solo percentil, la mediana es 50. En la atención, que es un promedio de percentiles, se calcula y se publica en `radar.json` (`cortes`).

| Atención | Desempeño | Cuadrante | Recomendación genérica |
|---|---|---|---|
| ≥ corte | ≥ corte | `consolidado` | Mantener; medir la saturación |
| ≥ corte | < corte | `atencion_sin_estancia` | Convertir la atención en pernocta: motivos para quedarse y resolver fricciones |
| < corte | ≥ corte | `demanda_poco_visible` | Crecer con contenido; la demanda existe |
| < corte | < corte | `por_posicionar` | Prioridad de promoción si la experiencia reportada es buena |

**Sensibilidad.** Se recalcula el cuadrante omitiendo cada componente, uno a la vez. Si cambia en algún caso, el destino es `sensible`.

## Requisitos funcionales

- **FR-008-01** `radar radar calcular` lee solo `data/curado/` y escribe `radar_destinos.csv`.
- **FR-008-02** Los componentes ausentes se dejan vacíos, sin imputar, y se anotan en `notas`.
- **FR-008-03** Prueba de arquitectura: ningún módulo de contexto importa otro contexto (ver `docs/dominio/mapa-de-contextos.md`).
- **FR-008-04** (P1) Escenarios de derrama con la cadena: cuartos → turistas noche (densidad) → llegadas (estadía) → visitantes (factor de afluencia) → derrama (derrama por visitante), con los promedios del destino en el periodo de referencia.
- **FR-008-05** (P1) Modelo con rezago: `log(llegadas_t) ~ efectos de mes + tendencia + interés_t + interés_{t−1}`. Origen móvil con prueba en 2023, 2024 y 2025, entrenando con 2017–2019 y 2022 hasta el año anterior. Línea base: llegadas del mismo mes del año anterior. Métrica: MAPE.

## Fuera de alcance

- Pesos «expertos» distintos entre componentes: todos pesan igual y se muestran por separado.
- Causalidad: el modelo con rezago muestra asociación temporal, no efecto causal.

## Preguntas abiertas

- ¿Se pondera la visibilidad en asistentes por idioma según el peso de cada mercado en las llegadas internacionales? Necesita datos por país de origen que no están en la serie oficial; queda como P2.
