# Plan 008 · Radar

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `radar/radar/desempeno.py` | Periodo de referencia y métricas de desempeño desde `indicadores_oficiales_mensual.csv` |
| `radar/radar/atencion.py` | Carga de cada componente (si existe su tabla), valor bruto y percentil |
| `radar/radar/indices.py` | Índices, brecha, cuadrantes y sensibilidad |
| `radar/radar/escenarios.py` | (P1) Escenarios de derrama |
| `radar/radar/rezago.py` | (P1) Modelo con rezago y línea base |
| `radar/comun/estadistica.py` | Percentiles con empates y Wilson (compartido) |
| `tests/test_arquitectura.py` | Revisa las importaciones entre contextos con `ast` |

## Entradas

| Tabla | Obligatoria | Componente |
|---|---|---|
| `indicadores_oficiales_mensual.csv` | Sí | Desempeño |
| `interes_busqueda_mensual.csv` | No | `atencion_busqueda` y modelo |
| `presencia_youtube.csv` | No | `atencion_video` |
| `presencia_panel.csv` | No | `atencion_panel` |
| `asistentes_visibilidad.csv` | No | `atencion_asistentes` |
| `opinion_agregada.csv` | No | Notas de la ficha (fricciones) |

## Salidas

`radar_destinos.csv`, `escenarios_derrama.csv` (P1) y `modelo_rezago.csv` (P1). Columnas en `docs/dominio/modelo-de-datos.md`.

## Detalle del escenario de derrama

Para el destino *d*, con promedios mensuales del periodo de referencia:

```
Δ               = mediana_PM(ocupacion_12m) − ocupacion_12m(d)        (solo si Δ > 0)
cuartos_extra   = Δ / 100 × cuartos_disponibles_mes(d)
turistas_noche  = cuartos_extra × densidad_ocupacion(d)
llegadas_extra  = turistas_noche / estadia_promedio(d)
visitantes      = llegadas_extra × factor_afluencia(d)                (2.222 en la serie oficial)
derrama_extra   = visitantes × derrama_por_visitante(d)
```

Se publica por mes y anualizado, con el texto «estimación con la metodología de la Secretaría; supone que la estructura de gasto no cambia».

## Detalle del modelo con rezago

- Se ajusta por destino con mínimos cuadrados ordinarios (`numpy.linalg.lstsq`; no hace falta otra dependencia).
- Variables: 11 indicadoras de mes, tendencia lineal, `interes_t` e `interes_{t−1}` estandarizados.
- Se excluyen marzo de 2020 a diciembre de 2021 del entrenamiento y de la prueba.
- Para cada año de prueba Y ∈ {2023, 2024, 2025}: se entrena con todos los meses válidos anteriores a Y y se predicen los 12 meses de Y.
- Se reportan el MAPE del modelo, el de la línea base y `mejora_pct = (MAPE_base − MAPE_modelo) / MAPE_base × 100`.
- Interpretación: «mejora» si `mejora_pct > 10` en al menos 2 de 3 años; si no, «sin evidencia de mejora».

## Pruebas

- Percentiles con empates y con n = 12.
- Cuadrantes en los cuatro casos y bandera de sensibilidad.
- Escenario con números de juguete verificables a mano.
- Modelo: con datos sintéticos donde el interés sí anticipa, el modelo mejora a la línea base; con ruido, no.
- Arquitectura: falla si `radar/asistentes` importa `radar/panel`, por ejemplo.
