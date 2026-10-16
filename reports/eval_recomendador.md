# Evaluación offline del recomendador inclusivo

> **DATOS SINTÉTICOS DE DEMOSTRACIÓN.** Los perfiles de solicitud son sintéticos. El catálogo sintético también; el curado viene de fuentes abiertas (spec 012).
> No hay retroalimentación de usuarios reales todavía: estas cifras miden el comportamiento del algoritmo, no la satisfacción de visitantes.

- Fecha de corrida: 2026-10-16
- Generado por `analysis/02_eval_recomendador.py`. Detalle por perfil en `reports/eval_recomendador.csv` y `reports/eval_recomendador_multidia.csv` (columna `catalogo`).
- Violaciones medidas por el verificador independiente (`backend/app/recommender/verificador.py`), el mismo para todos los métodos.

## Catálogo curado (spec 012)

- Catálogo: `data/curado/poi.csv` (datos reales; perfiles sintéticos): 1976 atractivos y 15 servicios (baños).
- Cobertura de datos de accesibilidad utilizables en 1340 atractivos (sin alojamiento): acceso sin escalones 3.0 %, baño accesible 0.0 %, pendiente 0.0 %.
- Perfiles de ruta: n = 40 (semilla 2026); planes multi-día: n = 12.

### Rutas: motor contra baselines (todos los perfiles)

| Método | n | Perfiles con ≥1 violación | Violaciones indispensables (escalones / pendiente / baño / descansos) | Otras violaciones | Rutas vacías | Paradas (media) | Cobertura alternativos | Zonas distintas | Popularidad media | Coincidencia de intereses | Tiempo usado / disponible | Latencia p50 / p95 (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Motor inclusivo | 40 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 25 | 1.32 | 0.47 | 2.87 | 0.57 | 0.63 | 0.26 | 19.3 / 154.1 |
| Baseline popularidad | 40 | 32 (80 %) | 219 (147 / 50 / 8 / 14) | 0 | 0 | 5.92 | 0.60 | 2.30 | 0.50 | 0.17 | 0.90 | 20.1 / 131.1 |
| Baseline cercanía | 40 | 32 (80 %) | 237 (154 / 61 / 8 / 14) | 0 | 0 | 6.00 | 0.68 | 2.00 | 0.46 | 0.19 | 0.91 | 22.3 / 145.9 |
| Baseline popularidad + filtro ingenuo | 40 | 32 (80 %) | 219 (147 / 50 / 8 / 14) | 0 | 0 | 5.92 | 0.60 | 2.33 | 0.50 | 0.17 | 0.90 | 21.1 / 136.5 |
| Ablación: motor sin diversidad | 40 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 25 | 1.35 | 0.47 | 2.00 | 0.57 | 0.63 | 0.26 | 21.9 / 119.6 |
| Ablación: motor sin pertinencia | 40 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 25 | 1.43 | 0.47 | 3.20 | 0.57 | 0.31 | 0.26 | 20.4 / 144.9 |

### Solo perfiles con alguna restricción indispensable (n = 32)

| Método | n | Perfiles con ≥1 violación | Violaciones indispensables (escalones / pendiente / baño / descansos) | Otras violaciones | Rutas vacías | Paradas (media) | Cobertura alternativos | Zonas distintas | Popularidad media | Coincidencia de intereses | Tiempo usado / disponible | Latencia p50 / p95 (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Motor inclusivo | 32 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 25 | 0.44 | 0.29 | 1.71 | 0.66 | 0.64 | 0.10 | 18.9 / 148.9 |
| Baseline popularidad | 32 | 32 (100 %) | 219 (147 / 50 / 8 / 14) | 0 | 0 | 5.88 | 0.59 | 2.28 | 0.50 | 0.18 | 0.90 | 20.1 / 123.4 |
| Baseline cercanía | 32 | 32 (100 %) | 237 (154 / 61 / 8 / 14) | 0 | 0 | 6.16 | 0.69 | 1.97 | 0.46 | 0.20 | 0.92 | 24.6 / 145.9 |
| Baseline popularidad + filtro ingenuo | 32 | 32 (100 %) | 219 (147 / 50 / 8 / 14) | 0 | 0 | 5.88 | 0.59 | 2.31 | 0.50 | 0.17 | 0.90 | 22.3 / 120.0 |
| Ablación: motor sin diversidad | 32 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 25 | 0.44 | 0.29 | 1.43 | 0.66 | 0.64 | 0.10 | 19.3 / 119.6 |
| Ablación: motor sin pertinencia | 32 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 25 | 0.47 | 0.29 | 1.86 | 0.66 | 0.43 | 0.10 | 18.1 / 144.9 |

### Solo perfiles con «sin escalones» (n = 25)

| Método | n | Perfiles con ≥1 violación | Violaciones indispensables (escalones / pendiente / baño / descansos) | Otras violaciones | Rutas vacías | Paradas (media) | Cobertura alternativos | Zonas distintas | Popularidad media | Coincidencia de intereses | Tiempo usado / disponible | Latencia p50 / p95 (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Motor inclusivo | 25 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 21 | 0.24 | 0.00 | 1.50 | 0.80 | 0.75 | 0.06 | 16.5 / 148.9 |
| Baseline popularidad | 25 | 25 (100 %) | 190 (147 / 26 / 5 / 12) | 0 | 0 | 5.88 | 0.68 | 2.32 | 0.46 | 0.18 | 0.90 | 21.1 / 131.1 |
| Baseline cercanía | 25 | 25 (100 %) | 205 (154 / 34 / 5 / 12) | 0 | 0 | 6.16 | 0.80 | 1.68 | 0.40 | 0.20 | 0.92 | 24.2 / 137.6 |
| Baseline popularidad + filtro ingenuo | 25 | 25 (100 %) | 190 (147 / 26 / 5 / 12) | 0 | 0 | 5.88 | 0.68 | 2.36 | 0.46 | 0.17 | 0.90 | 22.7 / 136.5 |
| Ablación: motor sin diversidad | 25 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 21 | 0.24 | 0.00 | 1.00 | 0.80 | 0.75 | 0.06 | 16.5 / 119.6 |
| Ablación: motor sin pertinencia | 25 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 21 | 0.24 | 0.00 | 1.50 | 0.80 | 0.75 | 0.06 | 15.4 / 147.4 |

### Cómo leer las columnas

- **Violaciones indispensables**: paradas sin acceso sin escalones confiable, con pendiente no confiable o mayor, tramos de más de 90 min sin baño accesible y tramos continuos más largos que el intervalo de descanso pedido. Objetivo: 0.
- **Otras violaciones**: tiempo total, horario verificable y presupuesto conocido.
- **Cobertura alternativos**: proporción de paradas en destinos alternativos (media de rutas no vacías).
- **Zonas distintas**: celdas de 500 m distintas por ruta.
- **Coincidencia de intereses**: proporción de paradas cuyo texto coincide con algún interés según la misma similitud TF-IDF que usa el motor; favorece al motor por construcción y se reporta solo como control.
- **Latencia**: mínimo de 3 corridas por perfil (criterio de `timeit`, que reduce el ruido de otros procesos) en una laptop de desarrollo; p50 y p95 sobre los perfiles. No es determinista y cambia con la carga de la máquina.
- **Ablaciones**: el mismo motor con el peso de diversidad (y la penalización por repetir zona) en 0, o con el peso de pertinencia en 0. Miden cuánto aporta cada término; las restricciones duras siguen activas.

### Multi-día

| Plan | Lugares | Días × h | Restricciones | Asignados (motor / ingenuo) | Distancia por lugar m (motor / ingenuo) | Cruces entre días (motor / ingenuo) | Duplicados | Violaciones |
|---|---|---|---|---|---|---|---|---|
| plan-01 | 9 | 2 × 8 | sin_escalones+descansos_30 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 |
| plan-02 | 13 | 2 × 8 | descansos_45 | 4 / 3 | 557 / 5399 | 0 / 0 | 0 | 0 |
| plan-03 | 15 | 3 × 8 | sin_escalones+banio_accesible | 1 / 1 | 0 / 0 | 0 / 0 | 0 | 0 |
| plan-04 | 14 | 3 × 6 | sin_escalones+banio_accesible+descansos_30 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 |
| plan-05 | 8 | 2 × 6 | sin_escalones+descansos_45 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 |
| plan-06 | 14 | 2 × 8 | banio_accesible | 3 / 2 | 356 / 0 | 0 / 0 | 0 | 0 |
| plan-07 | 16 | 3 × 6 | ninguna | 7 / 6 | 1011 / 4318 | 0 / 1 | 0 | 0 |
| plan-08 | 11 | 3 × 6 | ninguna | 6 / 6 | 673 / 673 | 0 / 0 | 0 | 0 |
| plan-09 | 14 | 3 × 6 | banio_accesible+descansos_30 | 4 / 3 | 160 / 0 | 0 / 0 | 0 | 0 |
| plan-10 | 15 | 2 × 6 | ninguna | 7 / 5 | 911 / 3529 | 0 / 0 | 0 | 0 |
| plan-11 | 14 | 2 × 6 | sin_escalones | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 |
| plan-12 | 13 | 2 × 6 | sin_escalones+banio_accesible | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 |

Totales: 32 lugares asignados contra 26 del orden ingenuo; 670 m por lugar asignado contra 2453 m; cruces entre días 0 contra 1; duplicados 0; violaciones indispensables 0.
El orden ingenuo es la lista del usuario partida en días consecutivos, con la misma simulación (horarios, descansos y baños), sin reordenar.

### Fallos y límites observados

- Rutas vacías del motor: 25 de 40.
  - perfil-01 (4 h, sin_escalones+descansos_30, presupuesto «bajo»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); descansos cada 30 min (0 programados). 32 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-03 (6 h, sin_escalones+banio_accesible+descansos_30, presupuesto «alto»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); descansos cada 30 min (0 programados); baño accesible a lo largo de la ruta (0 parada[s] de baño). 25 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-04 (4 h, pendiente_8, presupuesto «bajo»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: pendiente del acceso de hasta 8 %. 892 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-05 (4 h, sin_escalones+descansos_45, presupuesto «alto»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); descansos cada 45 min (0 programados). 10 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-06 (2 h, sin_escalones, presupuesto «alto»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6). 10 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-08 (2 h, sin_escalones, presupuesto «alto»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6). 20 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-09 (5 h, sin_escalones+banio_accesible, presupuesto «bajo»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); baño accesible a lo largo de la ruta (0 parada[s] de baño). 87 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-11 (4 h, sin_escalones+descansos_45, presupuesto «alto»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); descansos cada 45 min (0 programados). 10 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-12 (4 h, sin_escalones+descansos_45, presupuesto «medio»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); descansos cada 45 min (0 programados). 10 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-13 (3 h, sin_escalones, presupuesto «bajo»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6). 32 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-14 (6 h, descansos_60+pendiente_6, presupuesto «alto»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: pendiente del acceso de hasta 6 %; descansos cada 60 min (0 programados). 1096 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-15 (6 h, sin_escalones+descansos_30+pendiente_8, presupuesto «gratis»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); pendiente del acceso de hasta 8 %; descansos cada 30 min (0 programados). 613 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-17 (6 h, sin_escalones+pendiente_8, presupuesto «alto»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); pendiente del acceso de hasta 8 %. 1066 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-19 (3 h, sin_escalones+descansos_45+pendiente_6, presupuesto «bajo»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); pendiente del acceso de hasta 6 %; descansos cada 45 min (0 programados). 20 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-20 (5 h, sin_escalones+descansos_60, presupuesto «gratis»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); descansos cada 60 min (0 programados). 23 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-22 (3 h, sin_escalones, presupuesto «gratis»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6). 15 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-23 (6 h, sin_escalones+descansos_30, presupuesto «bajo»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); descansos cada 30 min (0 programados). 29 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-24 (2 h, sin_escalones+descansos_30+pendiente_8, presupuesto «sin tope»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); pendiente del acceso de hasta 8 %; descansos cada 30 min (0 programados). 456 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-25 (2 h, sin_escalones, presupuesto «bajo»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6). 32 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-26 (5 h, sin_escalones+banio_accesible, presupuesto «medio»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); baño accesible a lo largo de la ruta (0 parada[s] de baño). 9 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-27 (6 h, sin_escalones+pendiente_8, presupuesto «bajo»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); pendiente del acceso de hasta 8 %. 31 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-31 (4 h, sin_escalones, presupuesto «sin tope»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6). 13 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-34 (6 h, sin_escalones, presupuesto «bajo»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6). 107 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-37 (6 h, pendiente_6, presupuesto «alto»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: pendiente del acceso de hasta 6 %. 1326 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
  - perfil-38 (4 h, banio_accesible+pendiente_8, presupuesto «alto»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: pendiente del acceso de hasta 8 %; baño accesible a lo largo de la ruta (0 parada[s] de baño). 856 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
- Rutas del motor que usan menos de la mitad del tiempo: 3 de 40. Suele pasar cuando la restricción deja pocos lugares con dato confiable: el motor prefiere una ruta corta a una que viole una necesidad.
  - perfil-07: 1 parada(s), 78 de 360 min, restricciones banio_accesible, presupuesto «alto».
  - perfil-16: 1 parada(s), 30 de 120 min, restricciones sin_escalones+banio_accesible, presupuesto «medio».
  - perfil-40: 1 parada(s), 30 de 360 min, restricciones sin_escalones+banio_accesible+descansos_60, presupuesto «alto».
- Paradas por ruta: el motor arma 1.32 en promedio contra 5.92 de la baseline de popularidad. La diferencia es el costo de no violar restricciones y de insertar descansos y baños.
- La distancia es en línea recta × 1.3; la pendiente entre paradas no se mide.
- Catálogo real con perfiles sintéticos: las rutas vacías reflejan la falta de datos de accesibilidad en las fuentes abiertas, no un error del motor. Se reportan como brecha de información (§06.7).

## Catálogo sintético

- Catálogo: `backend/tests/datos/poi_sintetico.csv` (SINTÉTICO): 40 atractivos y 7 servicios (baños).
- Cobertura de datos de accesibilidad utilizables en 40 atractivos (sin alojamiento): acceso sin escalones 67.5 %, baño accesible 17.5 %, pendiente 45.0 %.
- Perfiles de ruta: n = 40 (semilla 2026); planes multi-día: n = 12.

### Rutas: motor contra baselines (todos los perfiles)

| Método | n | Perfiles con ≥1 violación | Violaciones indispensables (escalones / pendiente / baño / descansos) | Otras violaciones | Rutas vacías | Paradas (media) | Cobertura alternativos | Zonas distintas | Popularidad media | Coincidencia de intereses | Tiempo usado / disponible | Latencia p50 / p95 (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Motor inclusivo | 40 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.52 | 0.74 | 3.49 | 0.41 | 0.54 | 0.76 | 6.9 / 59.0 |
| Baseline popularidad | 40 | 33 (82 %) | 185 (86 / 73 / 10 / 16) | 0 | 0 | 5.30 | 0.00 | 3.40 | 0.80 | 0.25 | 0.87 | 13.0 / 80.4 |
| Baseline cercanía | 40 | 33 (82 %) | 171 (89 / 56 / 10 / 16) | 0 | 0 | 5.20 | 0.06 | 3.55 | 0.71 | 0.30 | 0.90 | 12.3 / 88.7 |
| Baseline popularidad + filtro ingenuo | 40 | 33 (82 %) | 154 (59 / 69 / 10 / 16) | 0 | 0 | 4.92 | 0.02 | 3.35 | 0.78 | 0.24 | 0.85 | 9.7 / 54.3 |
| Ablación: motor sin diversidad | 40 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.48 | 0.49 | 3.18 | 0.52 | 0.55 | 0.75 | 7.1 / 54.8 |
| Ablación: motor sin pertinencia | 40 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.45 | 0.85 | 3.36 | 0.35 | 0.43 | 0.75 | 8.3 / 51.6 |

### Solo perfiles con alguna restricción indispensable (n = 34)

| Método | n | Perfiles con ≥1 violación | Violaciones indispensables (escalones / pendiente / baño / descansos) | Otras violaciones | Rutas vacías | Paradas (media) | Cobertura alternativos | Zonas distintas | Popularidad media | Coincidencia de intereses | Tiempo usado / disponible | Latencia p50 / p95 (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Motor inclusivo | 34 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.24 | 0.73 | 3.18 | 0.42 | 0.51 | 0.73 | 6.2 / 46.5 |
| Baseline popularidad | 34 | 33 (97 %) | 185 (86 / 73 / 10 / 16) | 0 | 0 | 5.47 | 0.00 | 3.56 | 0.80 | 0.26 | 0.88 | 13.1 / 80.4 |
| Baseline cercanía | 34 | 33 (97 %) | 171 (89 / 56 / 10 / 16) | 0 | 0 | 5.29 | 0.06 | 3.65 | 0.71 | 0.30 | 0.91 | 12.6 / 88.7 |
| Baseline popularidad + filtro ingenuo | 34 | 33 (97 %) | 154 (59 / 69 / 10 / 16) | 0 | 0 | 5.03 | 0.03 | 3.50 | 0.78 | 0.24 | 0.87 | 9.0 / 54.3 |
| Ablación: motor sin diversidad | 34 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.18 | 0.51 | 3.00 | 0.52 | 0.53 | 0.72 | 6.1 / 54.8 |
| Ablación: motor sin pertinencia | 34 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.15 | 0.84 | 3.03 | 0.36 | 0.41 | 0.72 | 7.5 / 39.7 |

### Solo perfiles con «sin escalones» (n = 26)

| Método | n | Perfiles con ≥1 violación | Violaciones indispensables (escalones / pendiente / baño / descansos) | Otras violaciones | Rutas vacías | Paradas (media) | Cobertura alternativos | Zonas distintas | Popularidad media | Coincidencia de intereses | Tiempo usado / disponible | Latencia p50 / p95 (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Motor inclusivo | 26 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.08 | 0.74 | 3.00 | 0.43 | 0.57 | 0.73 | 6.0 / 46.5 |
| Baseline popularidad | 26 | 26 (100 %) | 145 (86 / 39 / 7 / 13) | 0 | 0 | 5.38 | 0.00 | 3.62 | 0.80 | 0.29 | 0.89 | 12.6 / 82.0 |
| Baseline cercanía | 26 | 26 (100 %) | 140 (89 / 31 / 7 / 13) | 0 | 0 | 5.12 | 0.08 | 3.65 | 0.70 | 0.33 | 0.91 | 10.1 / 59.2 |
| Baseline popularidad + filtro ingenuo | 26 | 26 (100 %) | 114 (59 / 35 / 7 / 13) | 0 | 0 | 4.81 | 0.04 | 3.54 | 0.77 | 0.27 | 0.87 | 7.5 / 54.6 |
| Ablación: motor sin diversidad | 26 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 3.00 | 0.52 | 2.92 | 0.53 | 0.58 | 0.70 | 5.5 / 54.8 |
| Ablación: motor sin pertinencia | 26 | 0 (0 %) | 0 (0 / 0 / 0 / 0) | 0 | 1 | 2.96 | 0.85 | 2.80 | 0.37 | 0.45 | 0.71 | 6.6 / 39.7 |

### Cómo leer las columnas

- **Violaciones indispensables**: paradas sin acceso sin escalones confiable, con pendiente no confiable o mayor, tramos de más de 90 min sin baño accesible y tramos continuos más largos que el intervalo de descanso pedido. Objetivo: 0.
- **Otras violaciones**: tiempo total, horario verificable y presupuesto conocido.
- **Cobertura alternativos**: proporción de paradas en destinos alternativos (media de rutas no vacías).
- **Zonas distintas**: celdas de 500 m distintas por ruta.
- **Coincidencia de intereses**: proporción de paradas cuyo texto coincide con algún interés según la misma similitud TF-IDF que usa el motor; favorece al motor por construcción y se reporta solo como control.
- **Latencia**: mínimo de 3 corridas por perfil (criterio de `timeit`, que reduce el ruido de otros procesos) en una laptop de desarrollo; p50 y p95 sobre los perfiles. No es determinista y cambia con la carga de la máquina.
- **Ablaciones**: el mismo motor con el peso de diversidad (y la penalización por repetir zona) en 0, o con el peso de pertinencia en 0. Miden cuánto aporta cada término; las restricciones duras siguen activas.

### Multi-día

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

### Fallos y límites observados

- Rutas vacías del motor: 1 de 40.
  - perfil-23 (6 h, sin_escalones+banio_accesible+pendiente_6, presupuesto «gratis»): No encontramos una ruta que cumpla todas tus necesidades con los datos que tenemos. No relajamos ninguna restricción indispensable. Respeta: sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6); pendiente del acceso de hasta 6 %; baño accesible a lo largo de la ruta (0 parada[s] de baño). 7 lugar(es) quedaron fuera porque falta verificar su accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar».
- Rutas del motor que usan menos de la mitad del tiempo: 4 de 40. Suele pasar cuando la restricción deja pocos lugares con dato confiable: el motor prefiere una ruta corta a una que viole una necesidad.
  - perfil-03: 1 parada(s), 106 de 360 min, restricciones sin_escalones+banio_accesible+descansos_30, presupuesto «alto».
  - perfil-17: 3 parada(s), 110 de 360 min, restricciones sin_escalones+pendiente_8, presupuesto «alto».
  - perfil-19: 1 parada(s), 57 de 180 min, restricciones sin_escalones+descansos_45+pendiente_6, presupuesto «bajo».
  - perfil-27: 2 parada(s), 69 de 360 min, restricciones sin_escalones+pendiente_8, presupuesto «bajo».
- Paradas por ruta: el motor arma 3.52 en promedio contra 5.30 de la baseline de popularidad. La diferencia es el costo de no violar restricciones y de insertar descansos y baños.
- La distancia es en línea recta × 1.3; la pendiente entre paradas no se mide.
- Catálogo sintético: las cifras no describen lugares reales.
