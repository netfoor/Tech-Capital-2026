# Lenguaje ubicuo

Estos términos significan lo mismo en las conversaciones, en los documentos, en el sitio y en el código. El nombre en código es el identificador que se usa en tablas, columnas y funciones. Si un término nuevo hace falta, se agrega aquí antes de usarlo.

## Territorio

| Término | Definición | Nombre en código |
|---|---|---|
| Destino | Lugar turístico que el radar analiza. Puede abarcar uno o varios municipios (Cholula abarca San Pedro y San Andrés) | `destino`, `destino_id` |
| Pueblo Mágico | Destino con el distintivo federal. Puebla tiene 12 | `pueblo_magico` |
| Zona | Agrupación de trabajo de destinos cercanos (Sierra Norte, Sierra Nororiental, Centro…). No es una regionalización oficial | `zona` |
| Clave INEGI | Clave geoestadística del municipio (5 dígitos, por ejemplo `21043`) o de la localidad (9 dígitos) | `cvegeo` |
| Cabecera | Localidad sede del municipio; sus coordenadas ubican al destino en el mapa | `cabecera` |
| Centro turístico | Unidad con la que el Observatorio Turístico publica sus datos. Normalmente coincide con un destino; también hay agregados («Estado», «Resto del Estado») y subcentros (San Pedro Cholula, San Andrés Cholula) | `centro_ot`, `nivel` |

## Desempeño turístico (datos oficiales)

| Término | Definición | Nombre en código |
|---|---|---|
| Periodo | Mes calendario, escrito `AAAA-MM` | `periodo` |
| Indicador oficial | Variable publicada por el Observatorio Turístico | `indicador` |
| Procedencia | Indica si el valor es **medido** (registro directo de DataTur) o **derivado** (estimado por la Secretaría con un factor o supuesto) | `procedencia` ∈ {`medido`, `derivado`} |
| Llegadas de turistas | Personas que se registran en un hospedaje y pernoctan al menos una noche. Medido | `llegadas_turistas` |
| Turistas noche | Suma de noches pernoctadas. Medido | `turistas_noche` |
| Ocupación | Cuartos ocupados entre cuartos disponibles, en porcentaje. Medido | `ocupacion_pct` |
| Cuartos libres por día | Cuartos disponibles no ocupados, en promedio diario. Representa la capacidad disponible | `cuartos_libres_por_dia` |
| Estadía promedio | Noches entre llegadas. Medido | `estadia_promedio_dias` |
| Afluencia de visitantes | Turistas más excursionistas. **Derivado**: en la serie oficial se calcula como llegadas por un factor fijo | `afluencia_visitantes` |
| Excursionista | Visitante que no pernocta. No se mide de forma directa en la serie oficial | — |
| Derrama | Gasto estimado de los visitantes. **Derivado** | `derrama_mxn` |
| Derrama por visitante | Derrama entre afluencia. Hereda la procedencia derivada | `derrama_por_visitante_mxn` |

## Atención digital

| Término | Definición | Nombre en código |
|---|---|---|
| Señal de atención | Medición de cuánto aparece o se busca un destino en un canal digital | `senal` |
| Interés de búsqueda | Valor relativo de 0 a 100 de Google Trends para un término o tema, en una región y un periodo | `interes` |
| Término ancla | Término fijo que se incluye en cada consulta de Trends para que los lotes sean comparables entre sí | `ancla` |
| Interés ajustado | Interés reescalado contra el término ancla; permite comparar destinos consultados en lotes distintos | `interes_ajustado` |
| Consulta de video | Búsqueda en YouTube con un texto fijo; se registran los primeros resultados y sus métricas en la fecha de consulta | `consulta_video` |

## Panel ciudadano

| Término | Definición | Nombre en código |
|---|---|---|
| Panel | Grupo de personas reales que, con su consentimiento, registran lo que les muestra una plataforma al buscar con textos fijos | `panel` |
| Participante | Persona del panel, identificada solo con un código (`P01`…) más su rango de edad y región de residencia | `participante_id` |
| Consentimiento | Aceptación registrada, con versión del aviso y fecha. Sin consentimiento no hay observación | `consentimiento` |
| Sesión | Una vez que un participante hace las búsquedas del protocolo en una plataforma | `sesion_id` |
| Observación | Un resultado visto en una sesión: posición, destino detectado, vistas visibles y tipo de contenido | `observacion` |
| Presencia en el panel | Proporción de sesiones en las que un destino aparece entre los primeros resultados | `presencia_panel` |

## Visibilidad en asistentes

| Término | Definición | Nombre en código |
|---|---|---|
| Asistente | Servicio conversacional de un proveedor (OpenAI, Google) con un modelo concreto | `proveedor`, `modelo` |
| Prompt | Pregunta fija del corpus, con idioma, mercado y tono | `prompt_id` |
| Mercado | País o región cuyo viajero se simula con el idioma y el contexto del prompt (MX, US, FR, KR, CN) | `mercado` |
| Tono | Forma de preguntar: `casual` (turista), `concreto` (pregunta acotada) o `comprador` (operador que arma un paquete) | `tono` |
| Corrida | Una respuesta de un asistente a un prompt, en una fecha, con parámetros registrados | `corrida_id` |
| Repetición | Número de corrida del mismo prompt con el mismo asistente; se repite para medir la variabilidad | `repeticion` |
| Con búsqueda | Se le permitió al asistente buscar en internet (solicitado) | `con_busqueda` |
| Buscó | El asistente efectivamente consultó la web en esa corrida (observado) | `busco` |
| Mención | Aparición de un destino en una respuesta, con su orden de aparición | `mencion` |
| Cita | Fuente web que el asistente adjunta a su respuesta | `cita`, `dominio` |
| Visibilidad | Porcentaje de corridas de un segmento en que se menciona el destino, con su intervalo de confianza | `visibilidad_pct` |
| Brazo controlado | Corridas por API con prompts del corpus | `brazo = "controlado"` |
| Brazo real | Conversaciones de personas reales en sus cuentas, compartidas por enlace | `brazo = "real"` |

## Opinión del visitante

| Término | Definición | Nombre en código |
|---|---|---|
| Comentario | Texto público escrito por un usuario bajo un video. Es dato personal: no sale del contexto | `comentario` (privado) |
| Categoría | Clase asignada a un comentario: `intencion`, `experiencia_positiva`, `experiencia_negativa`, `friccion`, `pregunta`, `otro` | `categoria` |
| Fricción | Obstáculo que menciona el visitante, como precio, acceso, seguridad, saturación o servicios | `subcategoria` |
| Agregado de opinión | Conteo y proporción de categorías por destino y fuente; es lo único que se publica | `opinion_agregada` |
| Etiqueta humana | Categoría asignada por una persona a una muestra, para validar al clasificador | `etiqueta_humana` |

## Análisis (radar)

| Término | Definición | Nombre en código |
|---|---|---|
| Componente de atención | Cada canal medido para un destino: búsqueda, YouTube, panel o asistentes, expresado en percentil entre los destinos comparados | `componente` |
| Índice de atención | Promedio de los percentiles de los componentes disponibles; se publica junto con sus componentes | `indice_atencion` |
| Índice de desempeño | Percentil de la ocupación de los últimos 12 meses medidos | `indice_desempeno` |
| Brecha | Índice de atención menos índice de desempeño. Negativo indica menos atención de la que su desempeño sugeriría | `brecha` |
| Cuadrante | Clasificación por atención y desempeño: `consolidado`, `atencion_sin_estancia`, `demanda_poco_visible`, `por_posicionar` | `cuadrante` |
| Ficha de destino | Resumen de un destino para decisión y citas de negocio | `ficha` |
| Escenario de derrama | Estimación de la derrama adicional si la ocupación sube cierto número de puntos. Usa la metodología de la propia Secretaría | `escenario` |
| Modelo con rezago | Modelo que estima las llegadas de turistas con el interés de búsqueda de meses previos; se compara con una línea base estacional | `modelo_rezago` |

## Publicación

| Término | Definición | Nombre en código |
|---|---|---|
| Paquete de datos | Conjunto de archivos JSON que consume el sitio | `web/public/datos/*.json` |
| Manifiesto | Lista de archivos del paquete con su SHA-256, fecha y fuentes | `manifiesto.json` |
| Huella | SHA-256 de un archivo | `sha256` |
