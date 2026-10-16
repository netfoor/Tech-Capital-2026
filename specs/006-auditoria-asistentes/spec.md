# Spec 006 · Auditoría de asistentes

| | |
|---|---|
| Contexto | Visibilidad en asistentes (núcleo) |
| Prioridad | P0 |
| Estado | Pendiente (accesos verificados el 2026-10-15: OpenAI con `web_search` y Gemini con `google_search`) |
| Depende de | 001 (términos y `detectar`), 005 (brazo real) |
| Habilita | 008 (componente de asistentes) y 009 (sección de asistentes) |

## Bases que atiende

DAT-06 y CAT-IA (la IA como objeto de estudio, con justificación, evidencia y explicabilidad), RUB-03 (innovación), FIN-09 y ENT-11 (documentación de los componentes con IA), H1 y H3 de la visión.

## Objetivo

Medir con método qué destinos de Puebla recomiendan los asistentes conversacionales, cómo cambia por idioma, por tono y por proveedor, y en qué fuentes se apoyan. La medición debe poder repetirse para evaluar el efecto de una campaña o del Tianguis.

## Historias de usuario

**H1 (P0).** Como Secretaría, quiero saber en qué porcentaje de respuestas aparece cada Pueblo Mágico cuando alguien pide recomendaciones sobre Puebla.
- Dado el corpus, cuando se ejecutan al menos 10 repeticiones por prompt y por asistente, entonces `asistentes_visibilidad.csv` tiene, para cada destino y segmento, n, k, porcentaje e intervalo de Wilson al 95 %.

**H2 (P0).** Como Secretaría, de cara al Tianguis, quiero ver cómo responde un asistente a un viajero o comprador de cada mercado.
- Dado el corpus en es, en, fr, ko y zh (con tono `comprador` incluido), cuando se calcula la visibilidad por idioma, entonces el sitio puede comparar idiomas para un mismo destino.

**H3 (P0).** Como área de promoción, quiero saber qué fuentes usan los asistentes para recomendar, para saber dónde tener presencia.
- Dadas las corridas con búsqueda, cuando se extraen las citas, entonces `asistentes_citas.csv` tiene la URL, el dominio y el tipo de dominio, y existe un resumen de los dominios más citados por idioma.

**H4 (P2).** Como ayuntamiento, quiero saber qué dicen mal o qué omiten los asistentes sobre mi destino.
- Dado un destino, cuando se revisan sus menciones, entonces se listan afirmaciones verificables (ubicación, distancia, horarios) marcadas como correctas, incorrectas o no verificables.

**H5 (P1).** Como analista, quiero comparar la API con las conversaciones reales de personas en sus cuentas.
- Dado el brazo real (spec 005), cuando se detectan menciones, entonces se reporta la visibilidad del brazo real junto a la del controlado en español, con la advertencia de n pequeño.

## Requisitos funcionales

- **FR-006-01** Corpus `data/referencia/prompts.csv` (`prompt_id, idioma, mercado, tono, texto, origen, revisado`) con 22 prompts:
  - es: 9 (casual, concreto y comprador);
  - en: 4;
  - fr, ko y zh: 3 cada uno.
  - Los prompts en otros idiomas los revisa alguien que hable el idioma o se coteja su traducción de ida y vuelta.
- **FR-006-02** Proveedores configurables por `.env`: `OPENAI_MODEL` (por defecto `gpt-5-mini`) con la herramienta `web_search`, y `GEMINI_MODEL` (por defecto `gemini-3.8-flash`) con la herramienta `google_search`. Sin instrucciones de sistema y con temperatura por defecto.
- **FR-006-03** Cada corrida guarda en `data/crudo/asistentes/<fecha>.jsonl`:
  - la respuesta cruda completa y su SHA-256;
  - el modelo reportado por el proveedor y los tokens;
  - si buscó (`busco`): en OpenAI, la presencia de un elemento `web_search_call`; en Gemini, `groundingMetadata.webSearchQueries` no vacío.
- **FR-006-04** Menciones:
  - es, en y fr con `catalogo.detectar`;
  - ko y zh con términos verificados y, para lo no reconocido, el extractor con salida estructurada (`docs/ia-responsable.md` §2).
  - Se guarda `metodo`.
- **FR-006-05** Citas:
  - OpenAI: anotaciones `url_citation`;
  - Gemini: `groundingChunks[].web` (título y URI); el dominio se toma del título y, si es una URL de redirección, se resuelve con una petición `HEAD` (P1).
  - Tipo de dominio con reglas: `*.gob.mx` → gobierno; lista de agencias de viaje, redes sociales y enciclopedias en `data/referencia/dominios.csv`.
- **FR-006-06** Modo `--plan` (sin llamadas) que imprime el número de corridas y los tokens estimados. Tope `RADAR_MAX_CORRIDAS` (por defecto 600).
- **FR-006-07** Reanudable: si se corta, no repite corridas que ya existen para el mismo prompt, proveedor, repetición y fecha.
- **FR-006-08** Tablas curadas: `asistentes_corridas.csv`, `asistentes_menciones.csv`, `asistentes_citas.csv`, `asistentes_visibilidad.csv` (segmentos: total, proveedor, idioma, tono, brazo y proveedor × idioma) y `asistentes_ejemplos.csv`. Lo crudo no se versiona.
- **FR-006-09** Validación de la detección con 60 respuestas revisadas a mano, estratificadas por idioma: precisión y exhaustividad.
- **FR-006-10** (P1) Brazo real con los datos de T005-09.

## Requisitos no funcionales

- La corrida principal (440 corridas) termina en menos de 2 horas, con pausas para respetar los límites de cada proveedor.
- El costo de la corrida principal se calcula a partir de los tokens registrados y se reporta en `09-resultados.md`.
- Las llaves se leen de `.env`; nunca aparecen en lo crudo.

## Fuera de alcance

- Las aplicaciones de consumo controladas con automatización: el brazo real cubre ese ángulo con personas.
- Otros asistentes sin API accesible para el equipo.

## Preguntas abiertas

- ¿Conviene un tercer brazo «sin búsqueda» (solo lo que el modelo sabe)? Es barato con Gemini: el mismo corpus sin la herramienta. Se agrega como P1 si sobra tiempo; contrasta memoria contra web.
