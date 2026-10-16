# ADR-0002 · Sitio estático con datos JSON y manifiesto SHA-256

**Estado:** aceptada · 2026-10-15

## Contexto

La demostración debe funcionar sin depender de servicios en vivo. El jurado valora la trazabilidad de los datos, y el sitio no debe exponer llaves.

## Decisión

El sitio se compila con Astro a archivos estáticos. Todos los datos llegan como JSON generados por `radar exportar`, validados contra `contracts/` y listados en `manifiesto.json` con su SHA-256. El navegador verifica cada huella antes de dibujar.

## Consecuencias

- El costo de operación es casi nulo, el sitio es rápido y existe una versión sin conexión para la demostración.
- No hay consultas en vivo: actualizar los datos implica volver a exportar y desplegar. Para el piloto, la recolección programada (P2) automatiza ese ciclo.
