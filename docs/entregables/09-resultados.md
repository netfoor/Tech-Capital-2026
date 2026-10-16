# Resultados

Notas de resultados que alimentan los documentos de entrega. Cada cifra sale de `data/curado/`; si cambia la tabla, se regenera la nota.

## Tablas generadas

<!-- generado:inicio -->
Periodo de referencia: 2025-07 a 2026-06.

**Radar por destino** (ordenado por brecha)

| Destino | Cuadrante | Atención | Desempeño | Brecha | Ocupación 12 m (%) |
|---|---|---|---|---|---|
| Cuetzalan | Atención sin estancia | 70.5 | 27.3 | 43.2 | 42.7 |
| Tlatlauquitepec | Por posicionar | 36.4 | 18.2 | 18.2 | 36.8 |
| Tetela de Ocampo | Por posicionar | 22.7 | 9.1 | 13.6 | 33.8 |
| Pahuatlán | Por posicionar | 13.6 | 0.0 | 13.6 | 32.2 |
| Chignahuapan | Consolidado | 72.7 | 63.6 | 9.1 | 44.5 |
| Huejotzingo | Atención sin estancia | 40.9 | 36.4 | 4.5 | 43.6 |
| Atlixco | Consolidado | 84.1 | 81.8 | 2.3 | 44.8 |
| Cholula | Consolidado | 100.0 | 100.0 | 0.0 | 57.8 |
| Xicotepec | Por posicionar | 36.4 | 45.5 | -9.1 | 43.8 |
| Huauchinango | Consolidado | 40.9 | 54.5 | -13.6 | 44.4 |
| Zacatlán | Consolidado | 59.1 | 90.9 | -31.8 | 53.0 |
| Teziutlán | Demanda poco visible | 22.7 | 72.7 | -50.0 | 44.5 |

**Visibilidad promedio de los Pueblos Mágicos en asistentes, por idioma**

| Idioma | Corridas por destino | Visibilidad promedio (%) |
|---|---|---|
| Español | 180 | 39.0 |
| Inglés | 80 | 29.5 |
| Francés | 41 | 35.4 |
| Coreano | 39 | 26.7 |
| Chino | 40 | 33.8 |

**Corridas de asistentes**

| Proveedor | Modelo | Corridas | Buscó en la web (%) | Tokens de entrada | Tokens de salida |
|---|---|---|---|---|---|
| gemini | gemini-3.8-flash | 220 | 0.9 | 7,190 | 307,059 |
| openai | gpt-5-mini-2025-08-07 | 160 | 94.4 | 3,751,668 | 537,029 |
<!-- generado:fin -->

## Interés de búsqueda frente a afluencia oficial (T003-05)

Datos: `interes_busqueda_mensual.csv` (Google Trends, MX, 2017-01 a 2026-09, reescalado contra Cholula) y `indicadores_oficiales_mensual.csv` (afluencia derivada del Observatorio Turístico).

- Chignahuapan: de 2022 a 2025 el interés de búsqueda promedia 41 en noviembre y 15 en enero a mayo, casi el triple. La afluencia oficial de noviembre (61 600 visitantes en promedio) está solo 28 % por encima del promedio de enero a mayo (48 200), frente a casi el triple en el interés. Coincide con la temporada de esferas navideñas; la lectura probable es que parte de esa atención se convierte en visitas de un día, que la serie oficial, derivada de llegadas a hoteles, no mide de forma directa.
- Correlación mensual entre interés y afluencia, sin marzo de 2020 a diciembre de 2021: Zacatlán 0.69, Tetela de Ocampo 0.60, Tlatlauquitepec 0.59, Cuetzalan 0.48, Pahuatlán 0.48, Teziutlán 0.26, Atlixco 0.18, Huejotzingo 0.18, Chignahuapan 0.12, Xicotepec −0.02, Huauchinango −0.23 y Cholula −0.33. La señal es moderada en unos destinos y débil donde hay eventos o visita de un día. Por eso la búsqueda es un componente del índice y no su único insumo.

![Chignahuapan en noviembre](figuras/chignahuapan-noviembre.png)

## Auditoría de asistentes (T006-12)

Datos: `asistentes_corridas.csv` (380 corridas al 2026-10-16: 160 de OpenAI con búsqueda web y 220 de Gemini con `google_search`).

- Consumo de tokens: OpenAI 3 751 668 de entrada y 537 029 de salida (23 000 de entrada por corrida en promedio, por el contexto de búsqueda); Gemini 7 190 de entrada y 307 059 de salida. Con la tarifa publicada por OpenAI para `gpt-5-mini` (0.25 USD por millón de tokens de entrada y 2.00 USD por millón de salida, consultada el 16 de octubre de 2026 en la documentación del modelo), los tokens de OpenAI suman unos 2.0 USD. Faltan por confirmar la tarifa de la herramienta de búsqueda de OpenAI, la de Gemini y el tipo de cambio, así que el costo total en pesos se anota cuando se tengan (T006-12).
- Tasa de búsqueda: OpenAI buscó en 94.4 % de las corridas y Gemini en 0.9 %.
- Cholula es el destino más visible: aparece en 78 % de las respuestas. Le siguen Zacatlán, Cuetzalan y Atlixco (55 a 57 %). Teziutlán aparece en 6 % y Huauchinango en 11 %.

## Revisión de sentido común del radar (T008-06)

Con dos componentes de atención (búsqueda y asistentes), cortes en 40.9 (atención) y 50.0 (desempeño):

- **Cuetzalan** queda en `atencion_sin_estancia` (brecha +43): es de los destinos más buscados y citados por los asistentes, pero su ocupación (42.7 %) está por debajo de la mediana. Es coherente con un destino de visita de un día o de fin de semana corto.
- **Teziutlán** queda en `demanda_poco_visible` (brecha −50): casi no aparece en asistentes (6 % de las respuestas) y tiene una ocupación por encima de la mediana de los Pueblos Mágicos con crecimiento de llegadas de 21.6 %. Es el caso más sorprendente; la explicación probable es demanda de negocios y de servicios, no turística, que no depende de contenido digital. Se confirma con el panel y con la ficha del destino.
- **Zacatlán** es `consolidado` con brecha −32: alta ocupación y alta visibilidad en asistentes, con búsqueda media.
- **Pahuatlán, Tetela de Ocampo y Tlatlauquitepec** quedan `por_posicionar`, de acuerdo con las cifras de ocupación más bajas del oficial (32 a 37 %).
- Con solo dos componentes no se puede medir la sensibilidad del cuadrante; se activa al sumar el panel o YouTube.
