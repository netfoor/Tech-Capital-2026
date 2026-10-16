# Contextos delimitados

Cada contexto tiene un módulo en `pipelines/src/radar/` y una spec que lo implementa. Para cada uno se describe:

- su responsabilidad;
- sus agregados, entidades y objetos de valor;
- las invariantes que nunca se rompen;
- los eventos que produce;
- lo que publica para los demás contextos.

Los eventos se materializan como archivos fechados y entradas en el manifiesto, no como un bus de mensajes ([ADR-0003](../decisiones/0003-eventos-como-archivos.md)).

---

## 1. Catálogo territorial · `radar.catalogo` · spec 001

**Responsabilidad:** dar identidad estable a cada destino y traducir cualquier nombre o clave a un `destino_id`.

| Elemento | Tipo | Contenido |
|---|---|---|
| `Destino` | Agregado (raíz) | `destino_id`, nombre, tipo, si es Pueblo Mágico, municipios, cabecera, ubicación, zona, centro del observatorio, términos por idioma, hashtags |
| `ClaveINEGI` | Objeto de valor | Clave municipal de 5 dígitos o de localidad de 9 dígitos, con prefijo `21` |
| `Ubicacion` | Objeto de valor | Latitud, longitud y altitud de la cabecera (WGS84) |
| `Terminos` | Objeto de valor | Nombres y variantes por idioma para búsquedas y para reconocer menciones |

**Invariantes**
- Hay exactamente 12 Pueblos Mágicos.
- `destino_id` y `centro_ot` son únicos.
- Las claves INEGI son válidas para Puebla.
- La cabecera pertenece al primer municipio del destino.
- Las coordenadas están dentro del estado.

**Publica:** `data/referencia/destinos.csv` y las geometrías en `data/referencia/geo/`.

---

## 2. Desempeño turístico · `radar.indicadores` · spec 002

**Responsabilidad:** traducir la estadística oficial a series mensuales limpias, con procedencia.

| Elemento | Tipo | Contenido |
|---|---|---|
| `SerieIndicador` | Agregado (raíz) | Centro, indicador, unidad, procedencia y observaciones mensuales |
| `Observacion` | Objeto de valor | Periodo y valor |
| `Procedencia` | Objeto de valor | `medido` o `derivado`, según el glosario de la fuente |

**Invariantes**
- Un valor por centro, indicador y periodo.
- La ocupación coincide con cuartos ocupados entre disponibles (tolerancia de 0.6 puntos).
- La suma de los meses coincide con el acumulado del PDF; los faltantes se reportan, no se imputan.
- No hay periodos posteriores al último mes publicado.

**Eventos:** `SeriePublicada(fuente_id, ultimo_periodo)`.

**Publica:** `indicadores_oficiales_mensual.csv`, `indicadores_oficiales_anual.csv` y `factor_afluencia_por_centro.csv`.

---

## 3. Atención digital · `radar.senales` · specs 003 y 004

**Responsabilidad:** medir el interés de búsqueda y la presencia en video de cada destino.

| Elemento | Tipo | Contenido |
|---|---|---|
| `ConsultaTendencias` | Agregado | Términos o temas, región, rango de fechas, ancla, fecha de consulta y respuesta cruda |
| `SerieInteres` | Entidad | Destino, región, periodo, interés relativo e interés ajustado contra el ancla |
| `ConsultaVideo` | Agregado | Texto de búsqueda, región, idioma, fecha y resultados ordenados |
| `Video` | Entidad | `video_id`, destino, posición, fecha de publicación, vistas, me gusta y número de comentarios a la fecha de consulta |

**Invariantes**
- Cada lote de Trends contiene el término ancla.
- No se mezclan series obtenidas con anclas distintas sin reescalar.
- Las métricas de video siempre llevan su fecha de consulta.
- Los datos crudos de YouTube no se versionan.

**Eventos:** `TendenciasActualizadas`, `VideosActualizados`.

**Publica:** `interes_busqueda_mensual.csv`, `videos_por_destino.csv` y `presencia_youtube.csv` (métricas agregadas por destino).

---

## 4. Panel ciudadano · `radar.panel` · spec 005

**Responsabilidad:** registrar, con consentimiento, qué muestra TikTok a personas reales al buscar destinos de Puebla.

| Elemento | Tipo | Contenido |
|---|---|---|
| `Participante` | Agregado (raíz) | Código `Pnn`, rango de edad, región de residencia, si ya visitó Puebla y consentimiento |
| `Consentimiento` | Objeto de valor | Versión del aviso, fecha y medio |
| `Sesion` | Agregado (raíz) | Participante, plataforma, fecha, consultas del protocolo y evidencia (capturas, en privado) |
| `ObservacionResultado` | Entidad | Consulta, posición, destino detectado, vistas visibles, tipo de contenido y si el participante abrió comentarios |

**Invariantes**
- Sin consentimiento vigente no se registra una sesión.
- No se guardan nombres, usuarios ni rostros fuera de `data/privado/`.
- Cada sesión usa las consultas de la versión vigente del protocolo.

**Eventos:** `SesionRegistrada`, `PanelCerrado(version_protocolo, n_participantes)`.

**Publica:** `panel_observaciones.csv` y `presencia_panel.csv`, anonimizados y sin texto libre.

---

## 5. Visibilidad en asistentes · `radar.asistentes` · spec 006

**Responsabilidad:** medir qué destinos recomiendan los asistentes, en qué idioma y con qué fuentes.

| Elemento | Tipo | Contenido |
|---|---|---|
| `Prompt` | Agregado | `prompt_id`, idioma, mercado, tono, texto y origen (equipo o panel) |
| `Corrida` | Agregado (raíz) | Prompt, brazo, proveedor, modelo, parámetros, si se pidió búsqueda, si buscó, repetición, fecha, respuesta cruda y huella |
| `Mencion` | Entidad | Corrida, destino y orden de aparición |
| `Cita` | Entidad | Corrida, URL, dominio y tipo de dominio |
| `Visibilidad` | Objeto de valor | Segmento, destino, n, k, porcentaje e intervalo de Wilson al 95 % |

**Invariantes**
- Toda corrida guarda su respuesta cruda y sus parámetros.
- Las menciones se detectan con los términos del catálogo y la detección se valida con una muestra revisada por personas.
- Un mismo prompt se repite al menos 10 veces por asistente antes de reportar su visibilidad.

**Eventos:** `CorridaCompletada`, `AuditoriaCerrada(fecha, n_corridas)`.

**Publica:** `asistentes_corridas.csv`, `asistentes_menciones.csv`, `asistentes_citas.csv`, `asistentes_visibilidad.csv` y `asistentes_ejemplos.csv`.

---

## 6. Opinión del visitante · `radar.comentarios` · spec 007

**Responsabilidad:** convertir comentarios públicos en categorías agregadas por destino, sin exponer a las personas.

| Elemento | Tipo | Contenido |
|---|---|---|
| `Comentario` | Entidad (privada) | Fuente, video, fecha y texto. Vive solo en `data/privado/` |
| `Clasificacion` | Objeto de valor | Categoría, subcategoría, confianza, modelo y versión del prompt de clasificación |
| `MuestraValidacion` | Agregado | Comentarios etiquetados por personas, acuerdo entre personas y acuerdo con el clasificador |
| `OpinionAgregada` | Objeto de valor | Destino, fuente, categoría, n y proporción |

**Invariantes**
- Solo se publican agregados con n ≥ 5 por celda.
- El clasificador no se usa si su acuerdo con las etiquetas humanas es menor a κ = 0.6.

**Eventos:** `ClasificacionValidada(kappa)`.

**Publica:** `opinion_agregada.csv` y `validacion_clasificador.json`.

---

## 7. Análisis · `radar.radar` · spec 008 (núcleo)

**Responsabilidad:** combinar atención y desempeño por destino, clasificar y priorizar, y estimar efectos.

| Elemento | Tipo | Contenido |
|---|---|---|
| `PerfilDestino` | Agregado (raíz) | Destino, periodo de referencia, componentes de atención, desempeño, índices, brecha, cuadrante y notas |
| `ComponenteAtencion` | Objeto de valor | Canal, valor bruto, percentil, n y fecha |
| `Desempeno` | Objeto de valor | Ocupación en los últimos 12 meses, cuartos libres por día, llegadas y crecimiento |
| `Cuadrante` | Objeto de valor | Una de cuatro clases, con su regla de corte |
| `ResultadoModelo` | Objeto de valor | Destino, especificación, error contra la línea base y periodo de prueba |
| `EscenarioDerrama` | Objeto de valor | Supuesto en puntos de ocupación, cuartos, turistas, visitantes y derrama adicional |

**Invariantes**
- Un componente sin datos no se imputa: el índice usa los disponibles y lo declara.
- Los cortes de cuadrante son la mediana de los 12 Pueblos Mágicos.
- Todo escenario declara sus supuestos.

**Eventos:** `RadarCalculado(periodo_ref)`.

**Publica:** `radar_destinos.csv`, `modelo_rezago.csv` y `escenarios_derrama.csv`.

---

## 8. Publicación · `radar.exportar` y `web/` · spec 009

**Responsabilidad:** presentar los resultados de forma clara y verificable.

| Elemento | Tipo | Contenido |
|---|---|---|
| `PaqueteDatos` | Agregado | Archivos JSON validados contra `contracts/` |
| `Manifiesto` | Objeto de valor | Archivo, SHA-256, fecha de generación y fuentes |

**Invariantes**
- Ningún archivo se publica sin pasar su esquema.
- El navegador verifica la SHA-256 antes de usar un archivo.
- No hay cifras escritas a mano en el sitio.

**Eventos:** `SitioPublicado(commit, url)`.
