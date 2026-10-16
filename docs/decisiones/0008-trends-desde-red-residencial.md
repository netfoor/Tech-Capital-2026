# ADR-0008 · Google Trends desde una red residencial

**Estado:** aceptada · 2026-10-15

## Contexto

Google Trends no tiene una API oficial abierta. La biblioteca `pytrends` funciona desde una conexión residencial, pero desde direcciones de nube responde con error 429. Se comprobó el 15 de octubre de 2026.

## Decisión

- La etapa `radar senales trends` se ejecuta en la computadora de un integrante, con pausas entre lotes, y guarda cada respuesta cruda en `data/crudo/trends/`. El resultado curado se versiona.
- Si en el piloto se necesita automatizar, se evalúa la API oficial de Google Trends en cuanto esté disponible para la cuenta.

## Consecuencias

- La serie se actualiza a mano una vez al mes, lo cual basta para una variable mensual.
- Queda documentado quién y cuándo la generó (`fecha_consulta`).
