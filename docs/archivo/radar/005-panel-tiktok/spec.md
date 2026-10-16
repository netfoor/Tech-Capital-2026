# Spec 005 · Panel ciudadano y TikTok

| | |
|---|---|
| Contexto | Panel ciudadano |
| Prioridad | P0 (panel piloto) · P1 (lector automático de capturas) |
| Estado | Pendiente |
| Depende de | 001 |
| Habilita | 006 (brazo real), 007 (comentarios de TikTok) y 008 (componente del panel) |

## Bases que atiende

DAT-01 y DAT-03 (datos propios cuando la naturaleza del proyecto lo requiere), DAT-05 y USO-01 (privacidad y consentimiento), RUB-03 (innovación: una fuente que no existe) y ADR-0004.

## Objetivo

Saber qué destinos de Puebla muestra TikTok a personas reales, con su cuenta y su historial, cuando buscan a dónde ir en Puebla. La recolección es legítima, consentida, reproducible y anonimizada.

## Historias de usuario

**H1 (P0).** Como participante, quiero saber qué se hará con mis datos antes de aceptar.
- Dado el aviso de privacidad (`consentimiento.md`), cuando lo acepto en el formulario, entonces queda registrada la versión del aviso y la fecha; sin aceptación no puedo enviar capturas.

**H2 (P0).** Como participante, quiero instrucciones simples que me tomen menos de 10 minutos.
- Dado el protocolo (`protocolo.md`), cuando lo sigo, entonces hago cuatro búsquedas fijas en mi cuenta, capturo los primeros 12 resultados de cada una y contesto cinco preguntas.

**H3 (P0).** Como analista, quiero las observaciones codificadas y anónimas.
- Dadas las capturas, cuando se codifican, entonces `panel_observaciones.csv` tiene una fila por resultado: sesión, participante `Pnn`, rango de edad, región, consulta, posición, destino detectado, vistas visibles y tipo de contenido. No tiene nombres, usuarios ni texto libre.

**H4 (P0).** Como analista, quiero la presencia de cada destino en el panel.
- Dadas las observaciones, cuando se agrega, entonces para cada destino se calcula la proporción de sesiones en que aparece entre los 12 primeros resultados de al menos una consulta, con n e intervalo de Wilson.

**H5 (P1).** Como equipo, quiero leer las capturas automáticamente para que el panel crezca.
- Dadas las capturas, cuando corre el lector, entonces su coincidencia con la codificación manual del 20 % de las capturas es ≥ 0.9 en el destino.

**H6 (P1).** Como responsable de la spec 006, quiero las conversaciones de los participantes con su asistente habitual.
- Dado el formulario, cuando la persona comparte el enlace o el texto de su conversación, entonces se registra para el brazo real, con su permiso de publicación.

## Requisitos funcionales

- **FR-005-01** `specs/005-panel-tiktok/consentimiento.md`: aviso de privacidad simplificado (versión `v1`).
- **FR-005-02** `specs/005-panel-tiktok/protocolo.md`: consultas, número de resultados, capturas y preguntas (versión `v1`).
- **FR-005-03** Formulario de recolección con los campos del protocolo. Las capturas se suben a una carpeta privada del equipo y nunca al repositorio.
- **FR-005-04** Plantilla de codificación `data/privado/panel/codificacion.csv` y reglas de codificación (destino, tipo de contenido, vistas).
- **FR-005-05** `radar panel consolidar`: valida la codificación, anonimiza y escribe `panel_observaciones.csv` y `presencia_panel.csv` (`destino_id, n_sesiones, k_sesiones, presencia_pct, ic95_bajo, ic95_alto`).
- **FR-005-06** Sesión piloto del equipo antes de convocar, para medir el tiempo y ajustar el protocolo (búsquedas a ritmo humano, pocas sesiones).
- **FR-005-07** (P1) Lector automático de capturas con un modelo con visión y validación contra la codificación manual.
- **FR-005-08** Resultados por rango de edad solo si cada grupo tiene n ≥ 5.

## Requisitos no funcionales

- **Meta:** al menos 15 participantes para la demostración y 30 si el tiempo alcanza.
- **Diversidad:** al menos tres rangos de edad y al menos dos regiones de residencia (Puebla y otro estado).
- Las capturas se eliminan el 31 de diciembre de 2026.

## Fuera de alcance

- Extracción automatizada de TikTok con cuentas ajenas o con bots (ADR-0004).
- Representatividad estadística nacional: es un panel de conveniencia y se reporta así.

## Preguntas abiertas

- ¿Se agrega Instagram con el mismo protocolo? Solo si sobra tiempo; la encuesta del observatorio agrupa Instagram, TikTok y Facebook.
