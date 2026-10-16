# Plan 006 · Auditoría de asistentes

## Dependencias

`uv sync --extra asistentes` (`openai`, `google-genai`). Llaves `OPENAI_API_KEY` y `GEMINI_API_KEY` en `.env`.

## Corpus inicial (`data/referencia/prompts.csv`)

| prompt_id | idioma | mercado | tono | texto |
|---|---|---|---|---|
| ES-C01 | es | MX | casual | Voy a ir a Puebla un fin de semana, ¿qué no me debo perder? |
| ES-C02 | es | MX | casual | ¿Qué pueblos mágicos me recomiendas visitar en Puebla? |
| ES-C03 | es | MX | casual | Quiero salir un día de la ciudad de Puebla, ¿a dónde puedo ir? |
| ES-C04 | es | MX | casual | Planea un viaje de 3 días por el estado de Puebla con lugares que no sean tan conocidos |
| ES-C05 | es | MX | casual | ¿Qué hay para hacer en Puebla en noviembre? |
| ES-K01 | es | MX | concreto | ¿Cuáles son los mejores pueblos de la Sierra Norte de Puebla para visitar? |
| ES-K02 | es | MX | concreto | Recomiéndame lugares con naturaleza y cascadas en Puebla |
| ES-K03 | es | MX | concreto | ¿Dónde puedo hacer turismo comunitario en Puebla? |
| ES-B01 | es | MX | comprador | Soy operador turístico. ¿Qué destinos de Puebla incluirías en un paquete cultural de 5 días y por qué? |
| EN-C01 | en | US | casual | I'm visiting Puebla, Mexico for a weekend. What shouldn't I miss? |
| EN-C02 | en | US | casual | What are the best small towns (Pueblos Mágicos) to visit near Puebla, Mexico? |
| EN-C03 | en | US | casual | Plan a 3-day trip around Puebla state, Mexico, with less touristy places |
| EN-B01 | en | US | comprador | I'm a tour operator building a 5-day cultural package in Puebla, Mexico. Which destinations would you include and why? |
| FR-C01 | fr | FR | casual | Je vais à Puebla au Mexique pour un week-end. Qu'est-ce que je ne dois pas manquer ? |
| FR-C02 | fr | FR | casual | Quels villages (Pueblos Mágicos) visiter autour de Puebla, au Mexique ? |
| FR-B01 | fr | FR | comprador | Je suis voyagiste. Quelles destinations de l'État de Puebla inclurais-tu dans un circuit culturel de 5 jours ? |
| KO-C01 | ko | KR | casual | 멕시코 푸에블라에 주말 여행을 가요. 꼭 가봐야 할 곳이 어디인가요? |
| KO-C02 | ko | KR | casual | 푸에블라 근처에서 가볼 만한 작은 마을(푸에블로 마히코)을 추천해 주세요. |
| KO-B01 | ko | KR | comprador | 저는 여행사 직원입니다. 멕시코 푸에블라주 5일 문화 패키지에 어떤 여행지를 넣으면 좋을까요? |
| ZH-C01 | zh | CN | casual | 我要去墨西哥普埃布拉过周末，有哪些地方不能错过？ |
| ZH-C02 | zh | CN | casual | 普埃布拉附近有哪些值得去的小镇（魔幻小镇）？ |
| ZH-B01 | zh | CN | comprador | 我是旅行社的产品经理，想设计墨西哥普埃布拉州五天的文化线路，你会包括哪些目的地？ |

**Corridas:** 22 prompts × 2 proveedores × 10 repeticiones = **440**.

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `radar/asistentes/proveedores.py` | Capa anticorrupción. `OpenAIConBusqueda` usa Responses API con `tools=[{"type": "web_search"}]`; `GeminiConBusqueda` usa `google-genai` con `tools=[{"google_search": {}}]`. Ambos devuelven un `RespuestaAsistente(texto, modelo, busco, citas[(url, titulo)], tokens_entrada, tokens_salida, crudo)` |
| `radar/asistentes/corridas.py` | Plan, ejecución reanudable, tope de corridas y escritura de JSONL |
| `radar/asistentes/menciones.py` | Detección por términos y extractor para ko y zh |
| `radar/asistentes/citas.py` | Dominio, tipo de dominio y resolución de redirecciones (P1) |
| `radar/asistentes/visibilidad.py` | Agregación por segmento con Wilson (usa `radar/comun/estadistica.py`) |
| `data/referencia/dominios.csv` | `dominio, tipo` para clasificar fuentes citadas |

## Algoritmo de ejecución

1. `radar asistentes plan`: lee el corpus y los proveedores, cuenta las corridas pendientes y estima los tokens (corrida de prueba × n).
2. `radar asistentes correr [--proveedor] [--idioma] [--repeticiones 10]`: recorre las combinaciones en orden aleatorio con semilla fija. Así, si se corta, la muestra queda balanceada. Hace una pausa de 1 a 2 s entre llamadas y hasta 3 reintentos con espera exponencial ante errores 429 o 5xx.
3. Cada respuesta se agrega como una línea al JSONL del día: `corrida_id = sha1(prompt_id|proveedor|modelo|repeticion|fecha)[:12]`.
4. `radar asistentes procesar`: lee los JSONL, detecta menciones y citas y escribe las cinco tablas curadas (`docs/dominio/modelo-de-datos.md`). Los ejemplos para el sitio salen de corridas de OpenAI con búsqueda: una por idioma, con semilla fija y un fragmento de máximo 600 caracteres.

## Visibilidad

- Por destino *d* y segmento *s*: `n` = corridas del segmento; `k` = corridas con al menos una mención de *d*; `visibilidad_pct = k / n × 100`; intervalo de Wilson al 95 %.
- **Participación en menciones:** las menciones de *d* entre el total de menciones de destinos del catálogo en el segmento. Es útil para el sitio.
- **Primer lugar** (P1): proporción de corridas en que *d* es el primer destino mencionado.

## Pruebas

- Respuestas simuladas de cada proveedor (sin red) en `tests/datos/asistentes/`: extracción de texto, de `busco` y de citas.
- Menciones: casos por idioma, incluidos «普埃布拉» (estado, que no debe contar como capital) y «乔卢拉» (Cholula).
- Reanudación: correr dos veces el plan con lo crudo existente no genera duplicados.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Costo mayor al esperado | `--plan` y tope de corridas; modelos ligeros; límite de gasto en cada consola |
| El modelo por defecto deja de existir | Modelo configurable; cada corrida registra el modelo real |
| Gemini decide no buscar | Se reporta la tasa de `busco` por segmento; la visibilidad se puede separar por `busco` |
| Errores de transliteración | Validación manual (FR-006-09) y método registrado |
| Términos de uso de las respuestas con búsqueda | Lo crudo no se versiona ni se publica; el sitio solo muestra métricas y fragmentos de OpenAI. Antes de mostrar texto de Gemini se revisan sus requisitos de visualización de resultados con búsqueda |
