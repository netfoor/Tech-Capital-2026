# Componentes con inteligencia artificial

La convocatoria pide explicar qué componentes usan IA, cuál es su función y cuáles son sus principales limitaciones (§16), y documentar modelo, configuración, variables, resultados y límites (§9). Este documento cumple ambas cosas. Se actualiza cuando cambia un modelo, un parámetro o un resultado de validación.

## Resumen

| # | Componente | Papel de la IA | Por qué hace falta | Spec | Prioridad |
|---|---|---|---|---|---|
| 1 | Auditoría de asistentes | **Objeto de estudio:** se mide qué recomiendan | Los asistentes ya son un canal de decisión de viaje y nadie mide su efecto sobre los destinos de Puebla | 006 | P0 |
| 2 | Extractor de menciones (coreano y chino) | Herramienta: reconoce destinos escritos con otros alfabetos | La búsqueda por términos no reconoce, por ejemplo, «乔卢拉» como Cholula | 006 | P0 |
| 3 | Clasificador de comentarios | Herramienta: asigna intención, experiencia o fricción | Leer miles de comentarios a mano no escala; con una regla de palabras clave se pierde el sentido | 007 | P1 |
| 4 | Lector de capturas del panel | Herramienta: lee posición, destino y vistas en capturas de resultados de TikTok | Permite que el panel crezca sin codificación manual | 005 | P1 |
| 5 | Modelo con rezago | Ciencia de datos (regresión), no IA generativa | Prueba si el interés de búsqueda anticipa las llegadas | 008 | P1 |

Un chatbot no es parte de la solución. Ningún componente decide por la Secretaría: todos producen evidencia que una persona revisa.

---

## 1. Auditoría de asistentes

| Campo | Valor |
|---|---|
| Función | Responder prompts del corpus para medir la visibilidad de cada destino y las fuentes citadas |
| Proveedores y modelos | OpenAI, Responses API, modelo por defecto `gpt-5-mini` con la herramienta `web_search`. Google Gemini API, modelo por defecto `gemini-3.8-flash` con la herramienta `google_search`. Los modelos se configuran en `.env` (`OPENAI_MODEL`, `GEMINI_MODEL`) y cada corrida registra el modelo real que respondió |
| Parámetros | Temperatura por defecto del proveedor (se busca reproducir el uso real). Sin instrucciones de sistema. Una conversación por corrida |
| Entradas | Texto del prompt (corpus en `data/referencia/prompts.csv`) |
| Salidas | Respuesta cruda (JSONL con huella), menciones por destino y citas con dominio |
| Variables que se reportan | Visibilidad por destino y segmento con intervalo de Wilson al 95 %, si buscó en la web, número de fuentes y tipo de dominio |
| Validación | La detección de menciones se compara con una revisión manual de 60 respuestas estratificadas por idioma. Meta: precisión y exhaustividad ≥ 0.95 en español e inglés, y ≥ 0.85 en coreano y chino |
| Limitaciones | Los asistentes cambian de versión sin aviso, por eso cada corrida se fecha. La API no tiene la memoria ni la ubicación de una cuenta personal, y eso se compara con el brazo real. El asistente decide si busca o no. Las respuestas varían mucho entre corridas, y por eso se mide un porcentaje sobre repeticiones |
| Datos personales | Ninguno en el brazo controlado. En el brazo real solo se usa el texto de la respuesta y el prompt; el enlace se guarda en privado si la persona no autoriza publicarlo |

## 2. Extractor de menciones

| Campo | Valor |
|---|---|
| Función | Para respuestas en coreano y chino, devolver la lista de destinos del catálogo mencionados, con su orden |
| Modelo | Google Gemini, con salida estructurada en JSON Schema y una lista cerrada de `destino_id`. Se usó Gemini y no OpenAI porque el crédito de OpenAI se agotó durante la primera auditoría (decisión del 16 de octubre de 2026) |
| Entradas | Texto de la respuesta y lista de destinos con sus nombres |
| Validación | Revisión manual de todas las respuestas en coreano y chino de la primera tanda. Se reportan precisión y exhaustividad |
| Limitaciones | Puede confundir destinos con nombres parecidos. Una mención ambigua se marca como `revisar` y no se cuenta |

## 3. Clasificador de comentarios

| Campo | Valor |
|---|---|
| Función | Asignar a cada comentario una categoría (`intencion`, `experiencia_positiva`, `experiencia_negativa`, `friccion`, `pregunta`, `otro`) y, si aplica, una subcategoría de fricción (`precio`, `acceso`, `seguridad`, `saturacion`, `servicios`, `clima`, `otro`) |
| Modelo | v2: OpenAI `gpt-5-mini` sin búsqueda (el crédito de Gemini se agotó); v1: Gemini. Salida JSON validada con esquema. Prompt versionado en `pipelines/src/radar/comentarios/prompt_v2.md` (v1 se conserva) |
| Entradas | Texto del comentario sin nombres de usuario ni menciones `@`, y el nombre del destino |
| Validación | Muestra de 120 comentarios estratificada por destino. Dos personas la etiquetan de forma independiente. Se reporta κ entre personas y κ del clasificador contra el consenso. **Umbral para usarlo: κ ≥ 0.6** |
| Resultados | Solo agregados por destino con n ≥ 5. **Estado: validación preliminar (17 de octubre de 2026).** Ver el detalle abajo |
| Limitaciones | Ironía, regionalismos, comentarios que mezclan idiomas, y sesgo de quien comenta (no representa a todos los visitantes) |
| Datos personales | Los comentarios se guardan en `data/privado/` y no se publican. Antes de enviarlos a la API se eliminan nombres de usuario y menciones. Se usa la API comercial; los términos sobre entrenamiento con los datos enviados no están verificados en la consola del proveedor |

**Validación del clasificador de comentarios (T007-03 y T007-05).**

1. **v1 (16 de octubre).** Con 64 etiquetas de una persona, κ = 0.31. El clasificador mandaba a `otro` los comentarios que valoran el lugar sin decir si fueron o quieren ir.
2. **Etiquetas humanas (17 de octubre).** Dos etiquetas humanas (`etiqueta_a`, `etiqueta_b`) y su consenso sobre 117 comentarios estratificados por destino. Acuerdo entre personas: κ = 0.59.
3. **Taxonomía v2.** Al revisar se vio que muchos comentarios elogian el paisaje o el pueblo sin hablar de una visita. Se agregó la categoría `imagen_destino` (valora el lugar sin decir que fue ni que quiere ir; el término viene de la literatura de «imagen de destino»).
4. **Tercera etiqueta y consenso final.** Una tercera etiqueta (`etiqueta_c`) la puso un modelo de IA (Claude) con la taxonomía v2, a petición del equipo. El consenso final parte del humano y solo lo cambia con dos reglas: (a) valora el lugar sin visita ni intención → `imagen_destino`; (b) habla del video, del creador o de otro lugar → `otro`. Cambió 31 de 117 etiquetas. La tercera etiqueta coincide con el consenso humano en κ = 0.63.
5. **Resultado v2.** κ del clasificador contra el consenso final = **0.72** (umbral 0.6). Contra el consenso solo humano, contando `imagen_destino` como `otro`, κ = 0.53.

**Límites de esta validación.** El prompt v2 y la nueva categoría se definieron después de ver esta misma muestra, y el consenso final incluye una etiqueta de IA. Por eso el 0.72 es optimista. Para darlo por validado falta etiquetar una muestra nueva, que nadie haya visto, con dos personas (T007-08). Mientras tanto, las proporciones se presentan como exploratorias.

## 4. Lector de capturas del panel

| Campo | Valor |
|---|---|
| Función | Leer de cada captura de resultados la posición, el texto visible, las vistas y el destino |
| Modelo | Modelo con visión de OpenAI o Gemini, con salida estructurada |
| Validación | Se compara con la codificación manual del 20 % de las capturas. Meta: ≥ 0.9 de coincidencia en el destino y ≥ 0.8 en las vistas |
| Limitaciones | Capturas recortadas o con poca resolución; vistas abreviadas («1.2M») |
| Datos personales | Las capturas pueden mostrar nombres de creadores; no se publican. Se pide a los participantes que no capturen su propio perfil |

## 5. Modelo con rezago

| Campo | Valor |
|---|---|
| Función | Estimar el logaritmo de las llegadas de turistas del mes con efectos de mes calendario, tendencia e interés de búsqueda del mismo mes y del mes anterior |
| Línea base | Ingenua estacional: el mismo mes del año anterior |
| Validación | Origen móvil: se entrena hasta el año *t* y se prueba en *t+1*, para 2022–2025, excluyendo 2020 y 2021 del entrenamiento. Métrica: MAPE |
| Resultado esperado | Por destino: «mejora sobre la línea base» o «sin evidencia de mejora» |
| Limitaciones | Correlación, no causa. Pocos años. El interés de búsqueda de los destinos pequeños es ruidoso |

---

## Registro de cambios

| Fecha | Cambio |
|---|---|
| 2026-10-15 | Versión inicial. Accesos verificados: OpenAI con `web_search` y Gemini con `google_search` responden con fuentes |
