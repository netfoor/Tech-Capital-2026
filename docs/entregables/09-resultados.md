# Resultados

Notas de resultados que alimentan los documentos de entrega. Cada cifra sale de `data/curado/`; si cambia la tabla, se regenera la nota.

## Interés de búsqueda frente a afluencia oficial (T003-05)

Datos: `interes_busqueda_mensual.csv` (Google Trends, MX, 2017-01 a 2026-09, reescalado contra Cholula) y `indicadores_oficiales_mensual.csv` (afluencia derivada del Observatorio Turístico).

- Chignahuapan: de 2022 a 2025 el interés de búsqueda promedia 41 en noviembre y 15 en enero a mayo, casi el triple. La afluencia oficial de noviembre (61 600 visitantes en promedio) está solo 28 % por encima del promedio de enero a mayo (48 200), frente a casi el triple en el interés. Coincide con la temporada de esferas navideñas; la lectura probable es que parte de esa atención se convierte en visitas de un día, que la serie oficial, derivada de llegadas a hoteles, no mide de forma directa.
- Correlación mensual entre interés y afluencia, sin marzo de 2020 a diciembre de 2021: Zacatlán 0.69, Tetela de Ocampo 0.60, Tlatlauquitepec 0.59, Cuetzalan 0.48, Pahuatlán 0.48, Teziutlán 0.26, Atlixco 0.18, Huejotzingo 0.18, Chignahuapan 0.12, Xicotepec −0.02, Huauchinango −0.23 y Cholula −0.33. La señal es moderada en unos destinos y débil donde hay eventos o visita de un día. Por eso la búsqueda es un componente del índice y no su único insumo.

![Chignahuapan en noviembre](figuras/chignahuapan-noviembre.png)

## Auditoría de asistentes (T006-12)

Datos: `asistentes_corridas.csv` (380 corridas al 2026-10-16: 160 de OpenAI con búsqueda web y 220 de Gemini con `google_search`).

- Consumo de tokens: OpenAI 3 751 668 de entrada y 537 029 de salida (23 000 de entrada por corrida en promedio, por el contexto de búsqueda); Gemini 7 190 de entrada y 307 059 de salida. El costo en pesos se calcula multiplicando por la tarifa vigente de cada proveedor al cierre de la corrida; la cifra final se anota aquí cuando se complete.
- Tasa de búsqueda: OpenAI buscó en 94.4 % de las corridas y Gemini en 0.9 %.
- Cholula es el destino más visible: aparece en 78 % de las respuestas. Le siguen Zacatlán, Cuetzalan y Atlixco (55 a 57 %). Teziutlán aparece en 6 % y Huauchinango en 11 %.
