# Material para la mentoría

La convocatoria (§7) pide presentar siete elementos: problemática, usuario o beneficiario, hipótesis, solución, datos, metodología y tecnologías. Los mentores validan la relevancia del problema, la suficiencia de los datos, la legitimidad de las fuentes y si el proyecto puede llegar a un prototipo demostrable.

## 1. Problemática

El turista decide a dónde ir en redes sociales y, cada vez más, preguntándole a un asistente conversacional. La Secretaría de Desarrollo Turístico no mide qué ve la gente ahí sobre cada destino ni si su promoción digital se convierte en visitas.

Mientras tanto:
- la capital concentra el 59.9 % de la afluencia estatal;
- los 12 Pueblos Mágicos tienen menor ocupación y menor derrama por visitante, y algunos están entre 32 y 36 % de ocupación;
- la afluencia oficial se deriva de las llegadas a hotel con un factor fijo, así que el visitante de un día no se mide de forma directa.

Fuentes en [`../producto/evidencia.md`](../producto/evidencia.md).

## 2. Usuario y beneficiarios

- **Usuaria principal:** la Secretaría de Desarrollo Turístico, en sus áreas de promoción, planeación y observatorio, y en las citas de negocio del Tianguis Turístico 2027.
- **Otros usuarios:** los ayuntamientos de los Pueblos Mágicos.
- **Beneficiarios:**
  - prestadores locales, porque la promoción se dirige a donde hay capacidad;
  - visitantes, porque encuentran información correcta y suficiente de más destinos.

## 3. Hipótesis

| ID | Hipótesis |
|---|---|
| H1 | La visibilidad de los Pueblos Mágicos en asistentes y en TikTok se concentra en pocos destinos y no corresponde a su capacidad disponible |
| H2 | El interés de búsqueda anticipa las llegadas de turistas en algunos destinos mejor que una línea base estacional |
| H3 | Los asistentes recomiendan distinto según el idioma; en coreano y chino los Pueblos Mágicos aparecen menos que en español |
| H4 | Los comentarios revelan fricciones concretas por destino que ayudan a explicar la diferencia entre atención y estancia |

## 4. Solución propuesta

El Radar de Atención Turística, una herramienta de datos que:
1. mide la atención digital de cada destino en cuatro canales: búsqueda, YouTube, panel de TikTok y asistentes en cinco idiomas;
2. la cruza con la ocupación oficial;
3. clasifica cada destino en un cuadrante con una recomendación;
4. produce fichas por destino para las citas del Tianguis 2027 y permite medir antes y después de una campaña.

Se publica como un sitio con datos verificables.

## 5. Datos

| Familia | Fuente | Tipo | Estado |
|---|---|---|---|
| Desempeño oficial | Observatorio Turístico de la Secretaría (DataTur y estimaciones propias), mensual 2017–2026, 22 centros | Oficial | Ingerida y validada |
| Territorio | INEGI: Marco Geoestadístico de diciembre de 2025 y cabeceras municipales | Oficial | Lista |
| Perfil del visitante | Informes del observatorio 2020 y 2024 (medio por el que se enteró) | Oficial | Lista |
| Búsqueda | Google Trends, mensual desde 2017 | Pública | Acceso verificado |
| Video | YouTube Data API: resultados, estadísticas y comentarios | API oficial | Acceso verificado |
| TikTok | Panel de personas con consentimiento, con capturas de sus búsquedas | Propia | Protocolo listo |
| Asistentes | OpenAI y Gemini con búsqueda web; 22 prompts en cinco idiomas, 10 repeticiones | Propia | Acceso verificado |

## 6. Metodología

- Ingesta con validación contra los acumulados de la fuente y la procedencia de cada indicador (medido o derivado).
- Visibilidad en asistentes como porcentaje de corridas, con intervalo de Wilson, por destino, idioma y proveedor, más las fuentes citadas.
- Índices en percentil entre los 12 Pueblos Mágicos, brecha entre atención y desempeño, y cuadrantes con prueba de sensibilidad.
- Modelo con rezago contra una línea base estacional, con validación por origen móvil.
- Clasificador de comentarios validado contra etiquetas humanas (κ ≥ 0.6).

## 7. Tecnologías

Python con uv (pandas, pdfplumber); APIs de YouTube, OpenAI y Gemini; sitio estático con Astro, d3 y anime.js; AWS (S3, CloudFront y ACM) con Terraform. Todo el código y los datos curados están en el repositorio y son reproducibles.

---

## Preguntas al comité

1. ¿Qué día y a qué hora presenta el equipo dentro del 15 al 17 de octubre? ¿Cuánto dura el pitch?
2. ¿Hay formato o plataforma para entregar los documentos de la §9?
3. ¿La Secretaría puede confirmar el método de estimación de la afluencia (factor fijo sobre llegadas) y si existe alguna medición directa de excursionistas?
4. ¿Existe una versión descargable del Inventario Estatal de Experiencias de Turismo Comunitario?
5. ¿Podemos mostrar en el sitio los logos del evento y de Intelligentia?
