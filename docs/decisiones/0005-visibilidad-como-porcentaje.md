# ADR-0005 · Visibilidad en asistentes como porcentaje sobre corridas repetidas

**Estado:** aceptada · 2026-10-15

## Contexto

Los asistentes conversacionales casi nunca repiten la misma lista de recomendaciones (SparkToro, 2026). Una sola respuesta no dice nada. Además, una cuenta personal (con memoria y ubicación) puede responder distinto que la API.

## Decisión

- Se mide el **porcentaje de corridas** en que aparece cada destino por segmento (proveedor, idioma, tono), con su intervalo de Wilson al 95 %. No se mide el «lugar en el ranking».
- Cada prompt se repite al menos 10 veces por asistente.
- Hay dos brazos: **controlado**, por API, con corpus fijo y búsqueda web habilitada; y **real**, con conversaciones de personas compartidas por enlace. Se comparan.
- Se registran las fuentes que cita cada respuesta.

## Consecuencias

- Los resultados son comparables entre destinos e idiomas, y los repetidos dan una medida de su incertidumbre.
- Tiene un costo por corrida que se controla con modelos ligeros y un tope de gasto en cada consola.
