# Spec 007 · Clasificación de comentarios

| | |
|---|---|
| Contexto | Opinión del visitante |
| Prioridad | P1 |
| Estado | Pendiente |
| Depende de | 004 (comentarios de YouTube) y 005 (comentarios de TikTok, P1) |
| Habilita | 008 (fricciones en fichas y apoyo a la lectura de cuadrantes) |

## Bases que atiende

DAT-06 y CAT-IA (IA pertinente y validada contra personas), DAT-05 y USO-01 (privacidad), H4 de la visión y OBJ-03 (experiencia del visitante).

## Objetivo

Convertir comentarios públicos en señales por destino: quién quiere ir, quién ya fue y cómo le fue, y qué fricciones menciona (precio, acceso, seguridad, saturación, servicios, clima). Solo se publican agregados.

## Historias de usuario

**H1 (P1).** Como área de promoción, quiero las fricciones más mencionadas de cada destino para saber qué resolver o qué aclarar en la comunicación.
- Dado un destino con al menos 30 comentarios, cuando se clasifica, entonces su ficha muestra la proporción por categoría y las tres subcategorías de fricción más frecuentes (celdas con n ≥ 5).

**H2 (P1).** Como jurado o revisor, quiero evidencia de que el clasificador es confiable.
- Dada una muestra de 120 comentarios etiquetada por dos personas, cuando se compara con el clasificador, entonces se reportan κ entre personas, κ del clasificador contra el consenso y la matriz de confusión. El clasificador solo se usa si su κ es de al menos 0.6.

**H3 (P1).** Como persona que comentó un video, no quiero aparecer en ningún resultado.
- Dado cualquier archivo publicado, cuando se revisa, entonces no contiene texto literal de comentarios, nombres de usuario ni identificadores de canal.

## Requisitos funcionales

- **FR-007-01** Taxonomía fija:
  - categorías: `intencion`, `experiencia_positiva`, `experiencia_negativa`, `friccion`, `pregunta` y `otro`;
  - subcategorías de fricción: `precio`, `acceso`, `seguridad`, `saturacion`, `servicios`, `clima` y `otro`.
- **FR-007-02** Prompt de clasificación versionado (`prompt_v1.md`) con definiciones y dos ejemplos por categoría, y salida estructurada validada con JSON Schema.
- **FR-007-03** Antes de enviar un comentario a la API se eliminan las menciones `@usuario`, URLs, correos y teléfonos.
- **FR-007-04** Muestra de validación estratificada por destino (120 comentarios), etiquetada de forma independiente por dos personas en `data/privado/comentarios/validacion.csv`.
- **FR-007-05** Tablas `opinion_agregada.csv` (n ≥ 5 por celda) y `validacion_clasificador.json`.
- **FR-007-06** Comando `radar comentarios clasificar` (reanudable) y `radar comentarios validar`.

## Fuera de alcance

- Análisis de sentimiento continuo o de emociones finas.
- Respuesta a comentarios.

## Preguntas abiertas

- Si el κ queda por debajo de 0.6, ¿se simplifica la taxonomía (por ejemplo, fusionar `pregunta` con `intencion`) y se vuelve a validar? Sí, una vez; si sigue bajo, el componente no se publica y se reporta así.
