# 4. Inventario y documentación de las fuentes de datos

> Generado por `uv run radar entregables` desde `data/fuentes/fuentes.csv` y `data/referencia/inventario_fuentes.csv`. No se edita a mano.

## Datos del Observatorio Turístico a junio 2026 (con glosario) (`sectur-ot-2026-06`)

- **Qué:** Serie mensual 2017-2026 por centro turístico: cuartos; llegadas; ocupación; afluencia; derrama
- **Por qué:** Es la medición oficial de desempeño turístico por destino y mes
- **De dónde:** [Secretaría de Desarrollo Turístico del Estado de Puebla](https://sectur.puebla.gob.mx/observatorioturistico/documentospdf/DatosOT%20a%20junio%202026%20glosario.pdf), consultado el 2026-10-15
- **Cómo:** Descarga del PDF y extracción de tablas con pdfplumber
- **Calidad:** Oficial; afluencia y derrama son estimaciones derivadas de las llegadas a hotel
- **Preparación:** indicadores_oficiales_mensual.csv e indicadores_oficiales_anual.csv
- **Evidencia:** `data/fuentes/sectur-puebla/datos-ot-a-junio-2026.pdf` · SHA-256 `5f9dd7418a12a1c5…`

## Informe Observatorio Turístico vacaciones de verano 2024 (`sectur-obs-verano-2024`)

- **Qué:** Medio por el que el visitante se enteró del destino (redes sociales 39.7 %)
- **Por qué:** Muestra que las redes sociales son un medio principal de información del visitante
- **De dónde:** [Secretaría de Desarrollo Turístico del Estado de Puebla](https://sectur.puebla.gob.mx/observatorioturistico/documentospdf/RESULTADOSOBSERVTAORIOTURISTICODEPUEBLA2024VERANO.pdf), consultado el 2026-10-15
- **Cómo:** Lectura del informe y transcripción de la cifra
- **Calidad:** Oficial; encuesta del Observatorio
- **Preparación:** data/referencia/evidencia_externa.csv
- **Evidencia:** `data/fuentes/sectur-puebla/observatorio-verano-2024.pdf` · SHA-256 `02478dcf25d57046…`

## Resultados del Observatorio Turístico informe 2024 (con BUAP) (`sectur-obs-2024-buap`)

- **Qué:** Medio por el que se enteró (TV 46.6 %; redes sociales 28.8 %)
- **Por qué:** Contrasta la importancia de la TV y las redes en otro levantamiento
- **De dónde:** [Secretaría de Desarrollo Turístico del Estado de Puebla / BUAP](https://sectur.puebla.gob.mx/observatorioturistico/documentospdf/RESULTADOS-OBSERVATORIO-TURISTICO.pdf), consultado el 2026-10-15
- **Cómo:** Lectura del informe
- **Calidad:** Oficial; levantamiento distinto al de verano
- **Preparación:** Se cita en docs/producto/evidencia.md
- **Evidencia:** `data/fuentes/sectur-puebla/observatorio-2024-buap.pdf` · SHA-256 `facf3e59ff1ead34…`

## Estudio de mercado en el sector turístico (octubre 2020) (`sectur-mercado-2020`)

- **Qué:** Vías para enterarse de sitios turísticos (redes sociales 46.7 %); red más usada (Facebook 66.3 %)
- **Por qué:** Antecedente de cómo se entera el visitante de los sitios de interés
- **De dónde:** [Secretaría de Turismo del Estado de Puebla / BEAP S.C.](https://sectur.puebla.gob.mx/observatorioturistico/documentospdf/estudiodemercadoturistico.pdf), consultado el 2026-10-15
- **Cómo:** Lectura del informe
- **Calidad:** Oficial; de 2020
- **Preparación:** Se cita en docs/producto/evidencia.md
- **Evidencia:** `data/fuentes/sectur-puebla/estudio-de-mercado-2020.pdf` · SHA-256 `1e1cf3d34f02e01c…`

## Marco Geoestadístico diciembre 2025 vía servicio web del Catálogo Único de Claves Geoestadísticas (`inegi-mg-2025-12`)

- **Qué:** Límites municipales de Puebla simplificados al 4 % para el mapa
- **Por qué:** Une todas las tablas por clave municipal y dibuja el mapa
- **De dónde:** [INEGI](https://gaia.inegi.org.mx/wscatgeo/v2/geo/mgem/21), consultado el 2026-10-15
- **Cómo:** Descarga del Marco Geoestadístico y simplificación al 4 %
- **Calidad:** Oficial
- **Preparación:** data/referencia/geo/ y geo/*.json del sitio
- **Evidencia:** `data/referencia/geo/municipios-puebla.geojson` · SHA-256 `c7793cbd12b6df0d…`

## Localidades cabecera municipal (latitud; longitud; altitud) (`inegi-cabeceras`)

- **Qué:** Coordenadas de cada destino del catálogo
- **Por qué:** Ubica cada destino en el mapa
- **De dónde:** [INEGI](https://gaia.inegi.org.mx/wscatgeo/v2/localidades/{cvegeo_mun}0001), consultado el 2026-10-15
- **Cómo:** Coordenadas de la cabecera de cada destino
- **Calidad:** Oficial
- **Preparación:** data/referencia/destinos.csv
- **Evidencia:** `data/referencia/destinos.csv` · SHA-256 `…`

## Turismo eje estratégico para el desarrollo y posicionamiento de Puebla (`gob-pue-balance-2025`)

- **Qué:** Balance 2025: visitantes; derrama; ocupación; 249 experiencias comunitarias; 12 Pueblos Mágicos; campañas digitales reportadas en impresiones
- **Por qué:** Muestra que la promoción se reporta por impresiones
- **De dónde:** [Gobierno del Estado de Puebla](https://puebla.gob.mx/index.php/noticias/item/22151-turismo-eje-estrategico-para-el-desarrollo-y-posicionamiento-de-puebla), consultado el 2026-10-06
- **Cómo:** Lectura del comunicado
- **Calidad:** Oficial; comunicado de prensa
- **Preparación:** Se cita en docs/producto/evidencia.md
- **Evidencia:** Sin archivo

## Desarrollo Turístico presenta acciones de promoción rumbo al Mundial 2026 (`gob-pue-mundial-2026`)

- **Qué:** La Secretaría colabora con creadores de contenido y no reporta indicadores de resultado
- **Por qué:** Muestra que la promoción con creadores no reporta resultados
- **De dónde:** [Gobierno del Estado de Puebla](https://puebla.gob.mx/index.php/noticias/item/22350-desarrollo-turistico-presenta-acciones-de-promocion-rumbo-al-mundial-2026), consultado el 2026-10-15
- **Cómo:** Lectura del comunicado
- **Calidad:** Oficial; comunicado de prensa
- **Preparación:** Se cita en docs/producto/evidencia.md
- **Evidencia:** Sin archivo

## Tianguis Turístico 2027 se llevará a cabo en Puebla (`tianguis-2027`)

- **Qué:** Fechas (9 al 12 de marzo de 2027); expositores; compradores; derrama esperada
- **Por qué:** Fecha y escala del escaparate al que apunta el proyecto
- **De dónde:** [Poblanerías (prensa)](https://www.poblanerias.com/2026/08/tianguis-turistico-2027-en-puebla/), consultado el 2026-10-06
- **Cómo:** Lectura de la nota
- **Calidad:** Prensa; cifras de expectativa
- **Preparación:** data/referencia/evidencia_externa.csv
- **Evidencia:** Sin archivo

## Gobierno del Estado impulsa innovación y creatividad con Tech Capital 2026 y FICTI (`tc-2026-turismo-digital`)

- **Qué:** Turismo digital como tema central de Tech Capital 2026 rumbo al Tianguis 2027
- **Por qué:** Contexto del tema central del evento
- **De dónde:** [Soy Universitario (prensa)](https://soyuniversitario.com/gobierno-del-estado-impulsa-innovacion-y-creatividad-con-tech-capital-2026-y-ficti/), consultado el 2026-10-06
- **Cómo:** Lectura de la nota
- **Calidad:** Prensa
- **Preparación:** Se cita en docs/producto/evidencia.md
- **Evidencia:** Sin archivo

## AIs are highly inconsistent when recommending brands or products (`sparktoro-2026`)

- **Qué:** Método: medir porcentaje de visibilidad con muchos prompts repetidos
- **Por qué:** Fundamenta medir la visibilidad como porcentaje sobre corridas repetidas
- **De dónde:** [SparkToro / Gumshoe](https://sparktoro.com/blog/new-research-ais-are-highly-inconsistent-when-recommending-brands-or-products-marketers-should-take-care-when-tracking-ai-visibility/), consultado el 2026-10-15
- **Cómo:** Lectura del estudio
- **Calidad:** Estudio privado; muestra de voluntarios
- **Preparación:** Diseño de la auditoría de asistentes
- **Evidencia:** Sin archivo

## AI search engines cite Reddit; YouTube; and LinkedIn most (`peec-2026`)

- **Qué:** Fuentes más citadas por los asistentes con búsqueda
- **Por qué:** Contexto de las fuentes que citan los asistentes con búsqueda
- **De dónde:** [Search Engine Land (estudio de Peec AI)](https://searchengineland.com/ai-search-engines-cite-reddit-youtube-and-linkedin-most-study-473138), consultado el 2026-10-15
- **Cómo:** Lectura del estudio
- **Calidad:** Estudio privado
- **Preparación:** Se cita en docs/producto/evidencia.md
- **Evidencia:** Sin archivo

## El 74 % de los viajeros mexicanos ya utiliza inteligencia artificial para planear sus viajes (`booking-2025-mx`)

- **Qué:** Uso de asistentes en la planeación de viajes en México
- **Por qué:** Contexto de uso de IA en la planeación de viajes
- **De dónde:** [Booking.com](https://news.booking.com/es-mx/el-74-de-los-viajeros-mexicanos-ya-utiliza-inteligencia-artificial-para-planear-sus-viajes-revela-bookingcom-en-estudio/), consultado el 2026-10-15
- **Cómo:** Lectura del estudio
- **Calidad:** Estudio privado; encuesta
- **Preparación:** Se cita en docs/producto/evidencia.md
- **Evidencia:** Sin archivo

## TikTok Research Tools: Access and Eligibility (`tiktok-research-api`)

- **Qué:** Elegibilidad de la API de investigación (no disponible para México)
- **Por qué:** Justifica el panel con consentimiento en lugar de extracción
- **De dónde:** [TikTok](https://developers.tiktok.com/products/research-api/), consultado el 2026-10-15
- **Cómo:** Lectura de los términos de la API
- **Calidad:** Términos de la plataforma
- **Preparación:** docs/decisiones/0004-panel-con-consentimiento.md
- **Evidencia:** Sin archivo

## Interés de búsqueda de Google Trends, consultas con ancla (`google-trends`)

- **Qué:** Componente de búsqueda de la atención digital: interés mensual por destino, normalizado con un destino ancla entre tandas
- **Por qué:** Señal pública de intención de viaje por destino
- **De dónde:** Equipo del proyecto con datos de Google Trends
- **Cómo:** Consultas a Google Trends en tandas con un destino ancla desde una red residencial
- **Calidad:** Muestreo de Google; escala relativa
- **Preparación:** interes_busqueda_mensual.csv
- **Evidencia:** Sin archivo

## Auditoría de asistentes conversacionales (`asistentes-auditoria`)

- **Qué:** Componente de asistentes: visibilidad de cada destino y fuentes citadas, a partir de corridas fechadas sobre un corpus de prompts
- **Por qué:** Mide la visibilidad de cada destino en asistentes conversacionales
- **De dónde:** Equipo del proyecto
- **Cómo:** Corridas repetidas con semilla fija en OpenAI y Gemini
- **Calidad:** Generada por el equipo; varía con la versión del modelo
- **Preparación:** asistentes_corridas.csv; asistentes_menciones.csv; asistentes_citas.csv; asistentes_visibilidad.csv
- **Evidencia:** Sin archivo
