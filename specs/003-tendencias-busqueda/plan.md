# Plan 003 · Tendencias de búsqueda

## Dependencias

`uv sync --extra senales`. Instala `pytrends` y `httpx`. `TrendReq` se crea sin `retries` ni `backoff_factor`: con urllib3 2 esos parámetros fallan (`method_whitelist`). Los reintentos y las pausas se programan en `trends.py`.

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `radar/senales/__init__.py` | — |
| `radar/senales/trends.py` | Capa anticorrupción de Trends: arma lotes, consulta, guarda lo crudo y reescala |
| `radar/cli.py` | Comando `senales trends [--geo MX] [--desde 2017-01-01] [--pausa 60]` |

## Diseño de lotes

```
Lote A: Cholula + Zacatlán + Chignahuapan + Atlixco + Cuetzalan
Lote B: Cholula + Huauchinango + Teziutlán + Xicotepec + Huejotzingo
Lote C: Cholula + Cuetzalan + Tlatlauquitepec + Tetela de Ocampo + Pahuatlán
```
- El lote A fija la referencia y Cholula es el ancla de primer nivel.
- En el lote C, Cuetzalan sirve como ancla de segundo nivel si Cholula aplasta a los destinos pequeños (interés menor a 1 en la mayoría de los meses). En ese caso, el reescalado de C se hace contra Cuetzalan y luego se multiplica por el factor de Cuetzalan en A.
- Los términos se toman de `trends_temas.csv` (T001-07) cuando hay tema verificado; si no, se usa `terminos_es[0]`.

## Algoritmo

1. Para cada lote: `TrendReq(hl="es-MX", tz=360)`, `build_payload(términos, timeframe="2017-01-01 <último día del mes cerrado>", geo=geo)`, `interest_over_time()`.
2. Guardar lo crudo: `{consulta_id, terminos, geo, timeframe, fecha_consulta, filas}`. El `consulta_id` es `trends-<geo>-<lote>-<AAAAMMDD>`.
3. Pasar a formato largo `(destino_id, termino, geo, periodo, interes, ancla, consulta_id, fecha_consulta)`.
4. Calcular `factor` por lote y `interes_ajustado`.
5. Para destinos que aparecen en más de un lote (Cuetzalan), conservar el valor del lote de referencia.
6. Escribir `data/curado/interes_busqueda_mensual.csv`.

## Pruebas

- Prueba unitaria del reescalado con datos sintéticos: dos lotes con el ancla a escalas distintas dan series iguales después del ajuste.
- Prueba del encadenamiento de anclas.
- La prueba de integración no llama a Trends: usa una respuesta cruda guardada en `tests/datos/trends_muestra.json`.

## Exploración previa

El 15 de octubre de 2026 se consultaron Zacatlán, Chignahuapan, Cuetzalan, Atlixco y Cholula (2017-01 a 2026-09, geo MX). La correlación mensual con la afluencia oficial, sin 2020, fue:

| Destino | r |
|---|---|
| Zacatlán | 0.56 |
| Cuetzalan | 0.51 |
| Atlixco | 0.21 |
| Chignahuapan | 0.14 |
| Cholula | 0.10 |

La señal es moderada en algunos destinos y débil donde hay eventos que la afluencia oficial no capta. Estas cifras se recalculan aquí con el método formal.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Error 429 o cambio en el servicio | Pausas, reintentos y lo crudo guardado; la tabla curada versionada sirve aunque Trends falle el día de la demostración |
| Términos ambiguos | Temas de Trends (T001-07) y revisión visual de picos atípicos |
