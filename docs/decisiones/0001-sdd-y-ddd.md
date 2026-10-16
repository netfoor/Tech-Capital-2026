# ADR-0001 · Desarrollo guiado por especificaciones con modelo de dominio explícito

**Estado:** aceptada · 2026-10-15

## Contexto

El proyecto se construye en pocos días, con integrantes que pueden rotar y con ejecución paralela de tareas. Sin un acuerdo escrito, cada quien interpretaría la convocatoria, los datos y los nombres a su manera.

## Decisión

- Cada funcionalidad tiene `spec.md` (qué y por qué), `plan.md` (cómo) y `tasks.md` (pasos con verificación). Nada se implementa sin ellos.
- El dominio se modela con contextos delimitados, un lenguaje ubicuo y un modelo de datos publicado. Cada contexto tiene su propio módulo de código.
- La matriz de trazabilidad conecta cada requisito de la convocatoria con una spec.

## Consecuencias

- Cualquier persona puede tomar una tarea sin contexto previo: todo lo necesario está en la spec y en los documentos del dominio.
- Cambiar el comportamiento cuesta un paso más, porque primero se actualiza la spec. A cambio, los entregables de la convocatoria se generan casi solos.
