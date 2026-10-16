# ADR-0004 · Panel con consentimiento en lugar de extracción automatizada

**Estado:** aceptada · 2026-10-15

## Contexto

Interesa saber qué muestra TikTok a personas reales, porque los resultados de una cuenta con historial difieren de los de una cuenta nueva. La API de investigación de TikTok no está disponible para México. Automatizar una cuenta con sesión iniciada va contra los términos de la plataforma, puede bloquear la cuenta y choca con la convocatoria: §5 pide datos «cuya utilización sea legal», §7 dice que los mentores revisan «la legitimidad de las fuentes» y §16 exige uso responsable.

## Decisión

El dato de TikTok se obtiene con un panel: personas que, con consentimiento informado, hacen búsquedas fijas en su propia cuenta y registran los primeros resultados con capturas. La extracción de las capturas puede apoyarse en un modelo de visión, validado con una muestra revisada por personas. Las búsquedas de prueba del equipo se hacen a ritmo humano y en pocas sesiones.

## Consecuencias

- Los datos son legítimos y reflejan la personalización real, y además se conoce el rango de edad y la región de cada participante.
- La muestra es pequeña y no aleatoria; se reporta así. Para escalar, el piloto propone un panel mensual y, más adelante, las estadísticas de las campañas propias de la Secretaría.
