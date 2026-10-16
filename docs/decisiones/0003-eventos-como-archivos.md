# ADR-0003 · Eventos de dominio como archivos fechados

**Estado:** aceptada · 2026-10-15

## Contexto

Los contextos se comunican cuando una etapa termina: hay una serie oficial nueva, una auditoría cerrada o un radar recalculado. No hay usuarios concurrentes ni flujos en tiempo real.

## Decisión

Un evento es un archivo publicado en `data/curado/` (o una corrida cruda fechada en `data/crudo/`) y su registro en el manifiesto. El orden de ejecución lo define `make datos`. No se usa bus de mensajes ni colas.

## Consecuencias

- Hay menos piezas que operar, y el historial de eventos es el propio historial de git.
- Si el piloto requiere disparos automáticos, EventBridge puede invocar las mismas etapas sin cambiar el dominio.
