# Visión del producto

## En una frase

El turista decide en TikTok, en Google y en los asistentes conversacionales. El Radar de Atención Turística mide qué ve ahí sobre cada destino de Puebla y lo cruza con la ocupación y la derrama reales, para que la Secretaría de Desarrollo Turístico decida dónde y cómo promover.

## Problema

1. **La decisión de viaje ocurre en canales que el estado no mide.** El Observatorio Turístico de la propia Secretaría ubica a las redes sociales como el principal medio por el que el visitante se entera de Puebla. Sin embargo, ningún indicador oficial registra qué contenido ve la gente ni qué le recomiendan los asistentes.
2. **La promoción se evalúa por alcance, no por resultado.** Los balances públicos reportan campañas e impresiones. No hay forma de saber si una campaña o un creador de contenido movió visitantes a un destino.
3. **Los beneficios se concentran.** La capital recibe cerca del 60 % de la afluencia estatal. Los 12 Pueblos Mágicos tienen menos ocupación y menos gasto por visitante, y varios tienen ocupación hotelera de 32–36 %, es decir, capacidad disponible.
4. **La medición oficial no ve al visitante de un día.** La afluencia y la derrama publicadas se derivan de las llegadas a hotel con un factor fijo. El excursionista que llega por un video y regresa el mismo día no aparece en la medición directa.
5. **Hay una fecha que importa.** En marzo de 2027 Puebla recibe el Tianguis Turístico México: citas de negocio de la Secretaría con compradores y operadores de México y de otros países. Llegar con datos sobre qué destinos están subexpuestos y por qué es un diferenciador.

La evidencia y las fuentes de cada punto están en [`evidencia.md`](evidencia.md).

## Usuarios y beneficiarios

| Quién | Necesidad | Qué obtiene del radar |
|---|---|---|
| Secretaría de Desarrollo Turístico: área de promoción | Decidir campañas, creadores y mensajes por destino | Ranking de destinos por cuadrante (atención frente a ocupación), fricciones detectadas y contenido que funciona |
| Secretaría: planeación y observatorio | Medir el resultado de la promoción y complementar su estadística | Series de atención digital por destino y mes, modelo con rezago, metodología reproducible |
| Secretaría en el Tianguis Turístico 2027 | Argumentos para que compradores y operadores incluyan destinos en sus paquetes | Ficha por destino, visibilidad del destino en asistentes por idioma de cada mercado |
| Ayuntamientos de Pueblos Mágicos | Saber cómo se les ve y qué les reclaman los visitantes | Ficha del destino, comentarios clasificados y fuentes que citan los asistentes |
| Prestadores locales (beneficiario) | Más visitantes que pernocten | Promoción dirigida a destinos con capacidad disponible |
| Visitante (beneficiario) | Información correcta y suficiente antes de viajar | La Secretaría corrige y amplía lo que se ve en redes y asistentes, sobre todo de los destinos menos visibles |

## Hipótesis que el prototipo pone a prueba

| ID | Hipótesis | Cómo se prueba | Spec |
|---|---|---|---|
| H1 | La visibilidad de los Pueblos Mágicos en asistentes y en TikTok se concentra en pocos destinos y no corresponde a su capacidad disponible | Porcentaje de visibilidad por destino frente a ocupación y cuartos libres | 005, 006, 008 |
| H2 | El interés de búsqueda anticipa las llegadas de turistas en al menos algunos destinos, mejor que una línea base estacional | Modelo con rezago y validación por origen móvil | 003, 008 |
| H3 | Los asistentes recomiendan distinto según el idioma; en idiomas de mercados meta los Pueblos Mágicos aparecen menos que en español | Visibilidad por idioma (es, en, fr, ko, zh) | 006 |
| H4 | Los comentarios revelan fricciones concretas por destino que ayudan a explicar la diferencia entre atención y estancia | Distribución de categorías por destino y cuadrante | 004, 005, 007 |

Cualquier resultado es útil. Si una hipótesis no se sostiene, se reporta así (constitución, VI).

## Propuesta de valor

- **Una fuente nueva:** qué se ve en TikTok y qué responden los asistentes sobre cada destino, en cinco idiomas, con las fuentes que citan.
- **Conectada con lo que ya mide el estado:** la serie mensual 2017–2026 del Observatorio Turístico, sin pedir datos privados.
- **Accionable:** cuatro cuadrantes por destino, con una recomendación distinta para cada uno.
  - **Consolidado:** alta atención y alta ocupación. Mantener.
  - **Atención sin estancia:** alta atención y baja ocupación. Resolver fricciones y ofrecer motivos para pernoctar.
  - **Demanda poco visible:** baja atención y alta ocupación. Crecer con contenido.
  - **Por posicionar:** baja atención y baja ocupación. Prioridad de promoción si la experiencia es buena.
- **Medible antes y después:** la misma medición repetida permite evaluar una campaña o el efecto del Tianguis.

## Alcance de la versión demostrable

**Incluye (P0)**
- Catálogo de los 12 Pueblos Mágicos y la capital, con claves INEGI y mapa.
- Serie oficial mensual 2017–2026 ingerida y validada.
- Interés de búsqueda mensual por destino.
- Auditoría de asistentes: corpus de prompts en cinco idiomas, al menos dos proveedores, corridas repetidas, menciones y fuentes citadas.
- Panel piloto de TikTok con consentimiento y protocolo reproducible.
- Radar: índices, cuadrantes y fichas por destino.
- Sitio desplegado y documentos de entrega.

**Fortalece (P1)**
- YouTube con comentarios y su clasificación validada.
- Modelo con rezago contra línea base.
- Escenarios de derrama potencial.
- Brazo «real» de la auditoría: enlaces de conversaciones de personas reales.

**Después del hackathon (P2)**
- Recolección programada en la nube.
- Carga de grabaciones del panel desde un formulario.
- Reporte de omisiones y errores de los asistentes por destino.
- Extensión a otros destinos.

## Métricas de éxito de la demostración

- Los 12 Pueblos Mágicos con radar completo: al menos tres de cuatro componentes de atención con datos.
- Al menos 400 respuestas de asistentes analizadas, en al menos tres idiomas y dos proveedores.
- Al menos 15 participantes en el panel piloto.
- Toda cifra del sitio con procedencia comprobable: el manifiesto SHA-256 coincide.
- El sitio carga en menos de 3 segundos en un teléfono y funciona sin conexión en la demostración de respaldo.

## Del hackathon al piloto

1. **Hackathon (octubre de 2026):** prototipo con panel piloto y corridas puntuales.
2. **Piloto con la Secretaría (noviembre de 2026 a marzo de 2027):** medición mensual, panel recurrente, fichas para las citas del Tianguis y medición antes y después.
3. **Operación:** la Secretaría alimenta el radar con las estadísticas de sus campañas y de los creadores que contrata; se extiende a otros destinos y estados.
