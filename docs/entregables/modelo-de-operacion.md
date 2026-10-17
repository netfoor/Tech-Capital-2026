# Modelo de operación, costos y continuidad

Cómo operaría la Secretaría de Desarrollo Turístico el Radar de Atención Turística después del hackathon, qué cuesta y cómo se mide si sirve.

## Ciclo mensual

| Paso | Qué ocurre | Cómo | Resultado |
|---|---|---|---|
| 1. Datos oficiales | Se incorpora el nuevo mes del Observatorio Turístico | `radar indicadores` con el PDF del mes | Serie mensual actualizada |
| 2. Búsqueda | Se actualiza el interés de búsqueda de los destinos | `radar senales trends` desde una red residencial | `interes_busqueda_mensual.csv` |
| 3. Asistentes | Se repite la auditoría con los mismos prompts | `radar asistentes correr`, `extraer`, `procesar` | Visibilidad con intervalo por destino, idioma y proveedor |
| 4. Panel y video | Se recibe la nueva ronda del panel y de YouTube | Según los protocolos de las specs 004 y 005 | Agregados por destino |
| 5. Radar | Se recalculan índices, brecha y cuadrantes | `radar radar calcular` | `radar_destinos.csv` |
| 6. Publicación | Se valida, se firma y se despliega | `make verificar`, `make exportar`, `make web`, `make desplegar` | Sitio con manifiesto verificado |
| 7. Decisión | El área de promoción revisa fichas y cuadrantes | Reunión mensual con las fichas impresas | Prioridades de campaña del mes |

## Roles

| Rol | Responsabilidad |
|---|---|
| Responsable de datos | Corre las etapas con llaves, revisa los avisos de calidad y valida los resultados antes de publicar |
| Operador de infraestructura | Mantiene el sitio, las cuentas de acceso y los costos de nube |
| Enlace de la Secretaría | Define qué campañas y creadores se miden y recibe las fichas |
| Coordinador del panel | Convoca a los participantes, mantiene el consentimiento y el protocolo |

Las personas que cubren cada rol las define la Secretaría junto con el equipo en el piloto.

## Piloto: noviembre de 2026 a marzo de 2027

1. **Noviembre:** primera medición mensual completa con el panel ampliado y los cinco idiomas.
2. **Diciembre a febrero:** una medición por mes; ajustes del corpus de prompts con la Secretaría; fichas actualizadas.
3. **Marzo de 2027:** fichas por destino para las citas del Tianguis Turístico (9 al 12 de marzo) y medición inmediata posterior.

## Medir si la promoción funcionó

El radar no prueba causalidad por sí solo; ofrece una comparación estructurada:

1. **Qué se mide:** visibilidad en asistentes, interés de búsqueda, presencia en el panel y, del lado oficial, ocupación y llegadas.
2. **Grupos:** destinos con campaña o creador contratado frente a destinos sin ella, con la lista de campañas que entrega la Secretaría.
3. **Antes y después:** la misma medición con los mismos prompts y las mismas fuentes en una fecha previa y una posterior a la campaña.
4. **Diferencia de diferencias:** el cambio de los destinos promovidos menos el cambio de los no promovidos, con intervalos de incertidumbre.
5. **Cautelas:** el volumen es pequeño (pocos destinos), por lo que se reporta como evidencia indicativa y se acumula mes a mes. El modelo con rezago (spec 008, P1) prueba si el interés de búsqueda anticipa las llegadas.

### Primera línea de acción propuesta: que los asistentes recomienden más destinos

Los asistentes recomiendan sobre todo Cholula (82 % de las respuestas) y la capital (76 %). En cambio, Teziutlán, Xicotepec y Tetela de Ocampo, que casi no aparecen (8 a 18 %), reciben la mayor proporción de comentarios que valoran el lugar cuando alguien ve un video sobre ellos (34 a 35 %, `09-resultados.md`). La propuesta para el piloto es la siguiente:

1. Producir contenido de esos destinos con creadores y con el equipo de la Secretaría: videos, guías de cómo llegar y de cuándo ir. Las preguntas de los comentarios dicen qué falta.
2. Publicarlo también en las páginas que los asistentes ya citan (visitpuebla.mx y sectur.gob.mx concentran buena parte de las citas de gobierno).
3. Medir con la auditoría de asistentes antes y después, en el esquema de esta sección. Es una hipótesis por comprobar, no un efecto demostrado.

## Costos

Cada cifra lleva su fuente y fecha. Lo que no está verificado se marca como pendiente y no se estima.

| Concepto | Costo | Fuente y fecha | Estado |
|---|---|---|---|
| Tokens de OpenAI en la auditoría (modelo `gpt-5-mini`) | Unos 2.0 USD por la primera auditoría | Tarifa de la [documentación del modelo](https://developers.openai.com/api/docs/models/gpt-5-mini), 16 oct 2026, por los tokens de `asistentes_corridas.csv` | Verificado |
| Herramienta de búsqueda de OpenAI | Por llamada | Página de precios de OpenAI | Pendiente de verificar |
| Gemini con búsqueda de Google | Por tokens y por consulta | Página de precios de Gemini | Pendiente de verificar |
| YouTube Data API | Cuota gratuita diaria | Documentación de Google | Pendiente de verificar |
| Hospedaje del sitio (S3, CloudFront, ACM, Cognito) | Se estima con la calculadora de AWS al aplicar la infraestructura | Calculadora de precios de AWS | Pendiente (T010-02 a T010-04) |
| Dominio y DNS | Subdominio de un dominio existente | Cloudflare | Sin costo adicional |
| Panel | Incentivos y logística a definir con la Secretaría | — | Por definir |

Las corridas de OpenAI y Gemini son la parte variable del costo: crece con el número de prompts, idiomas y repeticiones, y se controla con `--max-segundos` y con el tamaño del corpus.

## Continuidad y extensión

- **Todo en el repositorio:** código, fuentes con huella, decisiones y métodos; cualquier persona del equipo de la Secretaría puede reproducir el cálculo.
- **Recolección programada (P2):** una función programada en la nube puede repetir YouTube y los asistentes cada mes; está especificada en la spec 010.
- **Más destinos:** el catálogo y los términos son tablas; agregar un destino es agregar filas y volver a correr las etapas.
- **Más estados:** el modelo de datos no depende de Puebla; cambia el catálogo, el corpus de prompts y la fuente oficial.
- **Gobernanza de datos:** del panel y de los comentarios solo se publican agregados; los datos personales viven fuera del repositorio y del sitio.
