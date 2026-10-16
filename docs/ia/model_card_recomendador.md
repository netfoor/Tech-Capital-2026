# Ficha del modelo · Recomendador inclusivo de itinerarios

| | |
|---|---|
| Componente | `backend/app/recommender/` (spec 015) |
| Versión | `015-v1` |
| Tipo | Optimización combinatoria con restricciones duras (orienteering con ventanas de tiempo) más ranking multiobjetivo con similitud de texto TF-IDF |
| Estado | MVP implementado; evaluado offline con perfiles y catálogo **sintéticos** |
| Evaluación | [`reports/eval_recomendador.md`](../../reports/eval_recomendador.md), generado por `analysis/02_eval_recomendador.py` |

## 1. Propósito

Armar un itinerario a pie para una persona con tiempo, intereses, presupuesto y necesidades de acceso, y repartir lugares guardados en varios días. Debe:

1. **No violar nunca** una restricción indispensable: sin escalones, pendiente máxima, baño accesible a lo largo de la ruta y descansos cada N minutos.
2. Explicar por qué recomienda cada parada, qué datos faltan y qué alternativas hay.
3. Repartir visitas hacia destinos menos saturados sin sacrificar pertinencia (bases, distribución de beneficios).

No decide por la persona ni certifica accesibilidad: ordena opciones con la información disponible y dice qué no sabe.

## 2. Por qué es IA pertinente y no decorativa

- **El problema es combinatorio.** Elegir de 40 lugares cuáles visitar y en qué orden, con horarios, tiempo total, descansos y baños, es una variante del *orienteering problem with time windows* (NP-difícil). Una lista ordenada por popularidad o un chatbot no garantizan factibilidad: la evaluación muestra que las baselines de popularidad y cercanía violan restricciones indispensables en 33 de 40 perfiles (82 %).
- **Restricciones como garantía, no como sugerencia.** La elegibilidad dura y el simulador de línea de tiempo hacen imposible que una ruta incluya un lugar sin dato confiable de acceso sin escalones, o un tramo más largo que el intervalo de descanso pedido. Un verificador independiente lo comprueba en pruebas con cientos de solicitudes aleatorias.
- **Explicable por construcción.** Cada término del puntaje es interpretable (pertinencia, cercanía, diversidad, calidad de información, esfuerzo) y se reporta por parada en `metricas.puntajes`. El motivo de cada parada se arma con esos términos y con la procedencia del dato de accesibilidad.
- **Medido contra líneas base y con ablaciones**, no afirmado.

## 3. Datos

| Entrada | Origen | Uso |
|---|---|---|
| `poi.csv` | Spec 012 (DENUE, SIC, OSM y auditoría propia) | Nombre, categoría, descripción, coordenadas, horario `opening_hours`, rango de costo |
| `poi_accesibilidad.csv` | Spec 012: OSM, prestador, comunidad y equipo verificador | `acceso_sin_escalones`, `banio_accesible`, `pendiente_pct` con origen, fecha, confianza y estado |
| `popularidad`, `es_destino_alternativo` | Columnas opcionales; si faltan, regla de polos saturados (`puebla`, `cholula`) del boletín estatal citado en §02 | Término de diversidad territorial |
| Solicitud del visitante | Formulario de la PWA (spec 016) | Horas, punto de partida opcional, intereses, presupuesto y restricciones funcionales. No se piden ni se infieren diagnósticos (§06.5) |

En la evaluación de esta versión **no había catálogo curado todavía**: se usó un catálogo sintético de 40 atractivos y 7 baños con nombres inventados en zonas plausibles del corredor Centro Histórico → Cholula (`backend/tests/datos/`, `is_synthetic=true`, generado con semilla por `analysis/02a_catalogo_sintetico.py`). Las cifras no describen lugares reales.

## 4. Variables y algoritmo

**Etapa 1. Elegibilidad dura** (`elegibilidad.py`)

- Un atributo **cumple** si `valor=si` con estado `verificado`, o `sin_verificar` con confianza ≥ 0.6. **No cumple** con `valor=no`, `limitado` o estado `reportado` (barrera reportada), sin importar la confianza. Sin dato o con confianza menor es **desconocido**.
- Con `sin_escalones` o `pendiente_max_pct`: lo que no cumple se excluye; lo desconocido no entra en la ruta y se ofrece en `alternativos`, marcado «sin verificar».
- Horario: parser conservador de `opening_hours`. Si no se interpreta, el lugar no se descarta y lleva la advertencia «horario sin verificar». Sin día de la semana, la ventana es la intersección de los días en que abre.
- Presupuesto: un costo conocido mayor que el presupuesto excluye; un costo desconocido entra con la advertencia «costo sin verificar».
- Duración: se excluye lo que no cabe ni con la visita sola.

**Etapa 2. Ranking multiobjetivo** (`ranking.py`, pesos en `config.py`)

```
puntuacion = 0.40·pertinencia + 0.20·cercania + 0.20·diversidad + 0.10·calidad − 0.10·esfuerzo
```

| Término | Cálculo |
|---|---|
| pertinencia | Coseno TF-IDF entre los intereses expandidos a un vocabulario controlado (12 intereses) y el texto del lugar (nombre, categoría con peso doble, subcategoría, descripción), normalizado al máximo del catálogo. 0.5 si no hay intereses |
| cercania | `1 − minutos_desde_origen / (tiempo_disponible / 2)`, acotado a [0, 1]. Sin punto de partida, el origen es el centroide de los 10 lugares más pertinentes |
| diversidad | `0.5·es_destino_alternativo + 0.5·(1 − popularidad)` |
| calidad | `0.8·confianza media de los tres atributos clave (sin_verificar vale la mitad) + 0.2·horario interpretable` |
| esfuerzo | `0.5·min(pendiente/15, 1) + 0.5·min(minutos/60, 1)`; pendiente desconocida = 0.3 |

Al construir la ruta, la utilidad se ajusta estilo MMR: −0.08 por cada parada ya en la misma zona de 500 m y −0.10 por cada parada de la misma categoría. Tope de una comida, un café y un mercado por ruta.

**Etapa 3. Secuenciación** (`secuencia.py`)

- Simulador de línea de tiempo: caminata, espera, visita, descanso y baño. Tiempo peatonal = haversine × 1.3 a 4.5 km/h. Estancias típicas por categoría (museo 60 min, templo 25, mirador 20…).
- Descansos: si una actividad haría pasar el tiempo continuo del intervalo pedido, se inserta un descanso de 10 min (o una pausa dentro de la visita). Una espera de 10 min o más cuenta como descanso.
- Baños: si el siguiente tramo dejaría más de 90 min sin acceso a un baño accesible confiable, se inserta el baño que menos desvía (entre los 5 más cercanos). El baño también debe cumplir las restricciones de acceso y tener horario interpretable. Si no hay, la ruta no es factible: se acorta.
- Optimización: inserción voraz por `utilidad / (Δt + 1)^0.5` en la mejor posición, seguida de 2-opt tras cada inserción.

**Etapa 4. Explicación** (`explicacion.py`): «Te lo recomendamos porque…» por parada (intereses que coinciden, cercanía, destino alternativo, procedencia del dato de accesibilidad), resumen de la ruta, datos desconocidos y alternativas.

**Multi-día** (`multidia.py`): k-means++ con semilla 2026 y asignación por arrepentimiento con capacidad de horas por día, secuenciación por día con los horarios de ese día de la semana y reubicación de lo que no cupo. Métricas: distancia contra el orden ingenuo, cruces de segmentos entre días y no asignados con motivo.

**Determinismo**: sin aleatoriedad salvo la semilla del k-means; desempates por `poi_id`. La misma solicitud da la misma ruta aunque cambie el orden del catálogo (probado).

## 5. Resultados de la evaluación offline

Perfiles de solicitud **sintéticos**, n = 40 (semilla 2026; incluye la escena de valor §06.8), sobre el catálogo sintético. Violaciones medidas por un verificador independiente del motor. Fuente: [`reports/eval_recomendador.md`](../../reports/eval_recomendador.md).

| Método | Perfiles con ≥1 violación indispensable | Violaciones indispensables | Paradas (media) | Cobertura de destinos alternativos | Zonas distintas | Popularidad media de las paradas | Tiempo usado / disponible |
|---|---|---|---|---|---|---|---|
| **Motor inclusivo** | **0 de 40** | **0** | 3.35 | **0.75** | 3.28 | **0.40** | 0.77 |
| Baseline popularidad | 33 de 40 | 185 | 5.30 | 0.00 | 3.40 | 0.80 | 0.86 |
| Baseline cercanía | 33 de 40 | 188 | 5.60 | 0.05 | 3.75 | 0.72 | 0.90 |
| Baseline popularidad + filtro ingenuo* | 33 de 40 | 155 | 4.92 | 0.02 | 3.35 | 0.78 | 0.85 |
| Ablación: sin diversidad | 0 de 40 | 0 | 3.27 | 0.50 | 3.03 | 0.52 | 0.74 |
| Ablación: sin pertinencia | 0 de 40 | 0 | 3.42 | 0.86 | 3.36 | 0.35 | 0.76 |

\* Excluye solo los lugares con `valor=no` y trata la falta de dato como «accesible», el error que la constitución (XIII) prohíbe.

Latencia del motor: p50 3.8 ms y p95 79.8 ms (mínimo de 3 corridas por perfil en una laptop de desarrollo; cambia con la carga de la máquina, ver el reporte). Requisito: p95 < 1 s.

Multi-día, n = 12 planes sintéticos: 99 lugares asignados contra 55 del orden ingenuo; 605 m por lugar asignado contra 2 491 m; 1 cruce entre días contra 5; 0 duplicados; 0 violaciones indispensables.

Pruebas: 67 pruebas unitarias del recomendador (`backend/tests/test_recomendador_*.py`), entre ellas la propiedad «ninguna violación» sobre 240 solicitudes aleatorias en 12 catálogos aleatorios con casos frontera y 80 solicitudes sobre el catálogo sintético.

### Lectura honesta

- **La garantía funciona**: 0 violaciones indispensables contra 155 a 188 de las baselines. La baseline con filtro ingenuo aún tiene 60 paradas sin acceso sin escalones confiable: tratar la falta de dato como «accesible» es el error que el motor evita.
- **Tiene costo**: el motor arma menos paradas (3.35 contra 5.30) y usa menos tiempo (77 % contra 86 %), porque excluye lugares sin dato confiable e inserta descansos y baños. En perfiles con muchas restricciones la ruta puede quedar corta o vacía (1 ruta vacía y 5 que usan menos de la mitad del tiempo; detalle en el reporte).
- **La diversidad territorial depende del término de diversidad**: sin él, la cobertura de destinos alternativos baja de 0.75 a 0.50 y la popularidad media sube de 0.40 a 0.52. En zonas distintas por ruta el motor queda por debajo de las baselines porque arma menos paradas.
- **Sin pertinencia** la cobertura de alternativos sube a 0.86, pero la coincidencia con los intereses baja de 0.56 a 0.44: hay una tensión real entre pertinencia y distribución, y los pesos actuales son un punto intermedio, no un óptimo calibrado.
- La «coincidencia de intereses» usa la misma similitud que optimiza el motor; favorece al motor por construcción y no prueba satisfacción.
- En el multi-día el orden ingenuo a veces recorre menos metros por lugar (planes 03, 08, 09 y 12), pero asigna muchos menos lugares.

## 6. Limitaciones

- **Distancias en línea recta** × 1.3, sin red peatonal (OSMnx queda como mejora), sin pendiente de los tramos entre paradas ni estado de banquetas. La pendiente evaluada es la del acceso del lugar.
- **Solo a pie**: no modela transporte. Un día que mezcla Puebla y Cholula supone caminar entre ellas.
- **Estancias típicas** por categoría como supuesto, no medidas; la spec 017 podrá calibrarlas con permanencia observada.
- **Pesos sin calibrar** con usuarios: son un supuesto documentado. No hay retroalimentación de usuarios reales todavía; si la hay en el hackathon se reportará aparte con su n.
- **Evaluación sintética**: catálogo y perfiles sintéticos. Hay que repetirla con `data/curado/poi.csv` cuando la spec 012 lo publique (el script lo detecta solo).
- El parser de horarios no interpreta feriados, meses ni `sunrise`; en esos casos el horario queda «sin verificar».
- La heurística no garantiza el óptimo global del orienteering.

## 7. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Que la ruta haga creer que un lugar es accesible | Solo entran lugares con dato confiable; el motivo dice quién lo afirma y con qué confianza; lo no verificado se ofrece aparte con esa etiqueta |
| Dato desactualizado (rampa clausurada) | Gana el registro más reciente; un `reportado` excluye siempre; el flujo de barreras (spec 018) actualiza la ficha y la siguiente recomendación ya lo considera |
| Que la diversidad empuje a lugares poco pertinentes | Peso de diversidad acotado (0.20) y ablación reportada; el usuario edita la ruta |
| Concentrar aún más la demanda en polos | Término de diversidad y penalización por repetir zona; cobertura de alternativos medida contra baselines |
| Estigmatizar zonas con poca información | La falta de dato se muestra como «sin verificar», nunca como «no accesible»; la brecha se reporta como cobertura de información (§06.7) |
| Inferir condiciones de salud | Las restricciones son funcionales, opcionales y no se guardan con la ruta; el motor no infiere nada de trayectorias |

## 8. Cómo reproducir

```bash
cd backend
uv run pytest -q tests/test_recomendador_*.py
uv run python ../analysis/02a_catalogo_sintetico.py   # regenera el catálogo sintético
uv run python ../analysis/02_eval_recomendador.py     # escribe reports/eval_recomendador.*
```
