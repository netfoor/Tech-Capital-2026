# Evaluación offline del recomendador inclusivo

> **DATOS SINTÉTICOS DE DEMOSTRACIÓN.** Los perfiles de solicitud son sintéticos y el catálogo también.
> No hay retroalimentación de usuarios reales todavía: estas cifras miden el comportamiento del algoritmo, no la satisfacción de visitantes.

- Fecha de corrida: 2026-10-16
- Catálogo: `backend/tests/datos/poi_sintetico.csv (SINTÉTICO)`: 40 atractivos y 7 servicios (baños).
- Perfiles de ruta: n = 40 (semilla 2026); planes multi-día: n = 12.
- Generado por `analysis/02_eval_recomendador.py`. Detalle por perfil en `reports/eval_recomendador.csv` y `reports/eval_recomendador_multidia.csv`.
- Violaciones medidas por el verificador independiente (`backend/app/recommender/verificador.py`), el mismo para todos los métodos.

## Rutas: motor contra baselines (todos los perfiles)

| Método | n | Perfiles con ≥1 violación | Violaciones indispensables (escalones / pendiente / baño / descansos) | Otras violaciones | Rutas vacías | Paradas (media) | Cobertura alternativos | Zonas distintas | Popularidad media | Coincidencia de intereses | Tiempo usado / disponible | Latencia p50 / p95 (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Motor inclusivo | 40 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.52 | 0.74 | 3.49 | 0.41 | 0.54 | 0.76 | 3.4 / 433.1 |
| Baseline popularidad | 40 | 33 (82 %) | 185 (86 / 73 / 10 / 16) | 0 | 0 | 5.30 | 0.00 | 3.40 | 0.80 | 0.25 | 0.87 | 5.3 / 264.3 |
| Baseline cercanía | 40 | 33 (82 %) | 171 (89 / 56 / 10 / 16) | 0 | 0 | 5.20 | 0.06 | 3.55 | 0.71 | 0.30 | 0.90 | 7.7 / 289.3 |
| Baseline popularidad + filtro ingenuo | 40 | 33 (82 %) | 154 (59 / 69 / 10 / 16) | 0 | 0 | 4.92 | 0.02 | 3.35 | 0.78 | 0.24 | 0.85 | 4.6 / 270.3 |
| Ablación: motor sin diversidad | 40 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.48 | 0.49 | 3.18 | 0.52 | 0.55 | 0.75 | 3.4 / 388.2 |
| Ablación: motor sin pertinencia | 40 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.45 | 0.85 | 3.36 | 0.35 | 0.43 | 0.75 | 4.7 / 249.5 |

## Solo perfiles con alguna restricción indispensable (n = 34)

| Método | n | Perfiles con ≥1 violación | Violaciones indispensables (escalones / pendiente / baño / descansos) | Otras violaciones | Rutas vacías | Paradas (media) | Cobertura alternativos | Zonas distintas | Popularidad media | Coincidencia de intereses | Tiempo usado / disponible | Latencia p50 / p95 (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Motor inclusivo | 34 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.24 | 0.73 | 3.18 | 0.42 | 0.51 | 0.73 | 3.0 / 127.0 |
| Baseline popularidad | 34 | 33 (97 %) | 185 (86 / 73 / 10 / 16) | 0 | 0 | 5.47 | 0.00 | 3.56 | 0.80 | 0.26 | 0.88 | 5.7 / 264.3 |
| Baseline cercanía | 34 | 33 (97 %) | 171 (89 / 56 / 10 / 16) | 0 | 0 | 5.29 | 0.06 | 3.65 | 0.71 | 0.30 | 0.91 | 7.7 / 289.3 |
| Baseline popularidad + filtro ingenuo | 34 | 33 (97 %) | 154 (59 / 69 / 10 / 16) | 0 | 0 | 5.03 | 0.03 | 3.50 | 0.78 | 0.24 | 0.87 | 4.0 / 270.3 |
| Ablación: motor sin diversidad | 34 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.18 | 0.51 | 3.00 | 0.52 | 0.53 | 0.72 | 3.1 / 145.7 |
| Ablación: motor sin pertinencia | 34 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.15 | 0.84 | 3.03 | 0.36 | 0.41 | 0.72 | 3.3 / 90.0 |

## Solo perfiles con «sin escalones» (n = 26)

| Método | n | Perfiles con ≥1 violación | Violaciones indispensables (escalones / pendiente / baño / descansos) | Otras violaciones | Rutas vacías | Paradas (media) | Cobertura alternativos | Zonas distintas | Popularidad media | Coincidencia de intereses | Tiempo usado / disponible | Latencia p50 / p95 (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Motor inclusivo | 26 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.08 | 0.74 | 3.00 | 0.43 | 0.57 | 0.73 | 2.7 / 485.9 |
| Baseline popularidad | 26 | 26 (100 %) | 145 (86 / 39 / 7 / 13) | 0 | 0 | 5.38 | 0.00 | 3.62 | 0.80 | 0.29 | 0.89 | 5.2 / 420.9 |
| Baseline cercanía | 26 | 26 (100 %) | 140 (89 / 31 / 7 / 13) | 0 | 0 | 5.12 | 0.08 | 3.65 | 0.70 | 0.33 | 0.91 | 5.1 / 289.3 |
| Baseline popularidad + filtro ingenuo | 26 | 26 (100 %) | 114 (59 / 35 / 7 / 13) | 0 | 0 | 4.81 | 0.04 | 3.54 | 0.77 | 0.27 | 0.87 | 3.2 / 355.4 |
| Ablación: motor sin diversidad | 26 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.00 | 0.52 | 2.92 | 0.53 | 0.58 | 0.70 | 3.1 / 388.2 |
| Ablación: motor sin pertinencia | 26 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 2.96 | 0.85 | 2.80 | 0.37 | 0.45 | 0.71 | 3.3 / 249.5 |

## Cómo leer las columnas

- **Violaciones indispensables**: paradas sin acceso sin escalones confiable, con pendiente no confiable o mayor, tramos de más de 90 min sin baño accesible y tramos continuos más largos que el intervalo de descanso pedido. Objetivo: 0.
- **Otras violaciones**: tiempo total, horario verificable y presupuesto conocido.
- **Cobertura alternativos**: proporción de paradas en destinos alternativos (media de rutas no vacías).
- **Zonas distintas**: celdas de 500 m distintas por ruta.
- **Coincidencia de intereses**: proporción de paradas cuyo texto coincide con algún interés según la misma similitud TF-IDF que usa el motor; favorece al motor por construcción y se reporta solo como control.
- **Latencia**: mínimo de 3 corridas por perfil (criterio de `timeit`, que reduce el ruido de otros procesos) en una laptop de desarrollo; p50 y p95 sobre los perfiles. No es determinista y cambia con la carga de la máquina.
- **Ablaciones**: el mismo motor con el peso de diversidad (y la penalización por repetir zona) en 0, o con el peso de pertinencia en 0. Miden cuánto aporta cada término; las restricciones duras siguen activas.

## Multi-día

| Plan | Lugares | Días × h | Restricciones | Asignados (motor / ingenuo) | Distancia por lugar m (motor / ingenuo) | Cruces entre días (motor / ingenuo) | Duplicados | Violaciones |
|---|---|---|---|---|---|---|---|---|
| plan-01 | 9 | 2 × 8 | sin_escalones | 5 / 5 | 585 / 3865 | 0 / 1 | 0 | 0 |
| plan-02 | 12 | 3 × 8 | sin_escalones+descansos_45 | 2 / 2 | 0 / 8292 | 0 / 0 | 0 | 0 |
| plan-03 | 9 | 3 × 6 | banio_accesible+descansos_45 | 9 / 4 | 837 / 225 | 0 / 0 | 0 | 0 |
| plan-04 | 15 | 2 × 6 | ninguna | 13 / 4 | 783 / 7960 | 0 / 0 | 0 | 0 |
| plan-05 | 14 | 3 × 6 | sin_escalones | 7 / 7 | 433 / 4576 | 0 / 0 | 0 | 0 |
| plan-06 | 9 | 3 × 8 | sin_escalones | 5 / 4 | 388 / 4546 | 0 / 0 | 0 | 0 |
| plan-07 | 16 | 3 × 8 | descansos_30 | 16 / 8 | 613 / 716 | 1 / 3 | 0 | 0 |
| plan-08 | 11 | 2 × 8 | banio_accesible+descansos_30 | 8 / 3 | 546 / 420 | 0 / 0 | 0 | 0 |
| plan-09 | 14 | 3 × 6 | banio_accesible | 14 / 5 | 719 / 524 | 1 / 0 | 0 | 0 |
| plan-10 | 16 | 2 × 6 | sin_escalones | 4 / 4 | 210 / 814 | 0 / 0 | 0 | 0 |
| plan-11 | 16 | 2 × 6 | descansos_30 | 12 / 5 | 770 / 641 | 0 / 0 | 0 | 0 |
| plan-12 | 12 | 3 × 8 | sin_escalones+descansos_30 | 6 / 4 | 575 / 521 | 1 / 1 | 0 | 0 |

Totales: 101 lugares asignados contra 55 del orden ingenuo; 628 m por lugar asignado contra 2491 m; cruces entre días 3 contra 5; duplicados 0; violaciones indispensables 0.
El orden ingenuo es la lista del usuario partida en días consecutivos, con la misma simulación (horarios, descansos y baños), sin reordenar.

## Fallos y límites observados

- Rutas vacías del motor: 1 de 40.
  - perfil-23 (6 h, sin_escalones+banio_accesible+pendiente_6, presupuesto «gratis»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); pendiente del acceso de hasta 6 %; baño accesible a lo largo de la ruta (0 parada[s] de baño). 7 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
- Rutas del motor que usan menos de la mitad del tiempo: 4 de 40. Suele pasar cuando la restricción deja pocos lugares con dato confiable: el motor prefiere una ruta corta a una que viole una necesidad.
  - perfil-03: 1 parada(s), 106 de 360 min, restricciones sin_escalones+banio_accesible+descansos_30, presupuesto «alto».
  - perfil-17: 3 parada(s), 110 de 360 min, restricciones sin_escalones+pendiente_8, presupuesto «alto».
  - perfil-19: 1 parada(s), 57 de 180 min, restricciones sin_escalones+descansos_45+pendiente_6, presupuesto «bajo».
  - perfil-27: 2 parada(s), 69 de 360 min, restricciones sin_escalones+pendiente_8, presupuesto «bajo».
- Paradas por ruta: el motor arma 3.52 en promedio contra 5.30 de la baseline de popularidad. La diferencia es el costo de no violar restricciones y de insertar descansos y baños.
- La distancia es en línea recta × 1.3; la pendiente entre paradas no se mide.
- El catálogo de esta corrida es sintético: las cifras no describen lugares reales.
