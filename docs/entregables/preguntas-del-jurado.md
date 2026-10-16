# Preguntas del jurado y respuestas preparadas

Cada respuesta cita el archivo del repositorio donde se comprueba. Las cifras no se repiten aquí: se leen en el sitio y en [`09-resultados.md`](09-resultados.md).

## Datos y método

**1. ¿De dónde salen los datos oficiales y cómo sabemos que son los publicados?**
De los informes mensuales del Observatorio Turístico de la Secretaría. Cada original se guarda sin editar con su URL, fecha de consulta y SHA-256, y `uv run radar fuentes` comprueba que sigan coincidiendo. Evidencia: [`data/fuentes/fuentes.csv`](../../data/fuentes/fuentes.csv).

**2. ¿Por qué el índice de desempeño usa solo la ocupación?**
Porque es la única medida directa y completa de los 12 destinos en el periodo. La afluencia y la derrama se derivan de las llegadas con un factor fijo, así que añadirlas repetiría la misma señal. Se muestran en la ficha como contexto. Evidencia: [`07-arquitectura.md`](07-arquitectura.md) y [`data/curado/factor_afluencia_por_centro.csv`](../../data/curado/factor_afluencia_por_centro.csv).

**3. Con solo dos componentes de atención, ¿no es frágil el radar?**
Sí, y se dice. Con dos componentes no se mide la sensibilidad del cuadrante y el sitio lo anota en cada destino. El diseño agrega YouTube y el panel cuando existan; con tres o más se marca qué destinos cambian de cuadrante al quitar un componente. Evidencia: [`pipelines/src/radar/radar/indices.py`](../../pipelines/src/radar/radar/indices.py) y la nota de cada destino en `radar_destinos.csv`.

**4. ¿Percentiles entre 12 destinos no exageran diferencias pequeñas?**
Pueden hacerlo: el percentil ordena, no mide distancias. Por eso cada ficha muestra también el valor bruto (por ejemplo la ocupación y el porcentaje de visibilidad con su intervalo) y la tabla del radar enseña ambos. Evidencia: [`data/curado/radar_destinos.csv`](../../data/curado/radar_destinos.csv).

**5. ¿Cómo se unen las consultas de Google Trends si cada tanda tiene su propia escala?**
Con un destino ancla común a todas las tandas; para destinos de poco volumen se usa un segundo ancla. El interés ajustado es el interés por el cociente de las medias del ancla. Evidencia: [`pipelines/src/radar/senales/trends.py`](../../pipelines/src/radar/senales/trends.py) y [`specs/003-tendencias-busqueda/plan.md`](../../specs/003-tendencias-busqueda/plan.md).

## Asistentes conversacionales

**6. Los asistentes responden distinto cada vez. ¿Qué valor tiene medirlos?**
Justo por eso se mide un porcentaje sobre muchas corridas repetidas, con semilla fija, y se reporta con intervalo de Wilson al 95 %. Una sola respuesta no dice nada; cientos sí dicen con qué frecuencia aparece cada destino. Evidencia: [`docs/ia-responsable.md`](../ia-responsable.md) y [`data/curado/asistentes_visibilidad.csv`](../../data/curado/asistentes_visibilidad.csv).

**7. ¿Cómo sabe que el destino «aparece» y no es una coincidencia de texto?**
Con términos verificados por idioma, límites de palabra y la regla de que gana el término más largo. Para coreano y chino se usa además un extractor con lista cerrada de destinos. La validación manual de 60 respuestas con precisión y exhaustividad sigue pendiente (T006-11) y los resultados se presentan como provisionales hasta tenerla. Evidencia: [`pipelines/tests/test_detectar.py`](../../pipelines/tests/test_detectar.py) y [`specs/006-auditoria-asistentes/tasks.md`](../../specs/006-auditoria-asistentes/tasks.md).

**8. ¿Qué pasa con «Puebla» que es ciudad y estado?**
El nombre suelto es ambiguo en francés, coreano y chino, así que no cuenta como la capital salvo que aparezca una expresión de ciudad. Está marcado como no verificado en el catálogo. Evidencia: [`data/referencia/terminos_idiomas.csv`](../../data/referencia/terminos_idiomas.csv).

**9. ¿Usan la misma versión del modelo que usaría un turista?**
No necesariamente. La API no tiene memoria ni ubicación de una cuenta personal, y cada corrida registra el modelo real que respondió y su fecha. El diseño incluye un brazo «real» con conversaciones de personas (P1) para compararlo. Evidencia: [`docs/ia-responsable.md`](../ia-responsable.md).

**10. ¿Por qué Gemini casi no busca en la web?**
Con la herramienta de búsqueda activada, el modelo decide si busca; en esta primera corrida lo hizo en muy pocas respuestas. Se reporta tal cual y está planeado un brazo sin búsqueda para separar el efecto. Evidencia: [`docs/entregables/09-resultados.md`](09-resultados.md) y la tarea T006-14.

## Panel, TikTok y privacidad

**11. ¿Es legal medir TikTok?**
No se extrae nada con automatización ni cuentas ajenas. La API de investigación de TikTok no está disponible para México, así que el dato viene de un panel de personas que aceptan participar con consentimiento informado y capturan lo que ven. Evidencia: [`docs/decisiones/0004-panel-con-consentimiento.md`](../decisiones/0004-panel-con-consentimiento.md).

**12. ¿Qué tan representativo es un panel pequeño?**
No lo es de todos los visitantes, y así se presenta: los resultados describen al panel, con su n y su intervalo. Sirve para detectar qué contenido aparece al buscar cada destino, no para estimar el total de visitantes. Evidencia: [`specs/005-panel-tiktok/spec.md`](../../specs/005-panel-tiktok/spec.md).

**13. ¿Qué datos personales se guardan y se publican?**
Del panel y de los comentarios solo se publican agregados con un n mínimo; los datos personales viven en `data/privado/`, fuera del repositorio. El sitio no tiene campos de identidad. Evidencia: [`AGENTS.md`](../../AGENTS.md) §6 y [`contracts/`](../../contracts/).

## Interpretación y uso

**14. ¿El radar prueba que más atención causa más visitas?**
No. Muestra una posición relativa entre destinos, no una causa. La medición del efecto de una campaña se plantea como comparación antes y después entre destinos promovidos y no promovidos, y se reporta como evidencia indicativa. Evidencia: [`modelo-de-operacion.md`](modelo-de-operacion.md).

**15. ¿Por qué no es solo un tablero?**
Porque produce una fuente de datos que no existe (qué responden los asistentes y qué se ve en redes, por idioma), la cruza con lo oficial y entrega una recomendación por cuadrante y una ficha imprimible por destino para la cita. Evidencia: [`01-descripcion-ejecutiva.md`](01-descripcion-ejecutiva.md).

**16. ¿Qué gana el visitante?**
Información más completa y correcta de destinos poco visibles: la Secretaría puede corregir y ampliar lo que los asistentes y las redes muestran. Evidencia: [`02-problema-y-usuarios.md`](02-problema-y-usuarios.md).

**17. ¿Y si la medición oficial está sesgada por el hotel?**
Es una limitación reconocida: la afluencia y la derrama se derivan de las llegadas a hotel con un factor fijo y el visitante de un día no se mide directo. El radar usa la ocupación y aporta señales digitales que sí capturan ese interés. Evidencia: [`docs/producto/evidencia.md`](../producto/evidencia.md) §2.

## Operación y escalamiento

**18. ¿Cuánto cuesta operarlo?**
El costo variable son las corridas de los asistentes; la primera auditoría costó unos 2 USD en tokens de OpenAI, y las demás tarifas se registran con fuente y fecha cuando se verifican. El sitio es estático. Evidencia: [`modelo-de-operacion.md`](modelo-de-operacion.md).

**19. ¿Cómo se extiende a más destinos o estados?**
Agregando filas al catálogo y a los términos, y repitiendo las etapas; el modelo de datos no depende de Puebla. Evidencia: [`docs/dominio/modelo-de-datos.md`](../dominio/modelo-de-datos.md).

**20. ¿Cómo sé que las cifras del sitio son las del repositorio?**
El navegador compara la SHA-256 de cada archivo con el manifiesto y avisa si algo no coincide; además cada cifra sale de una tabla de `data/curado/` generada por código. Evidencia: [`web/src/scripts/datos.js`](../../web/src/scripts/datos.js) y [`web/public/datos/manifiesto.json`](../../web/public/datos/manifiesto.json).

## IA responsable

**21. ¿Dónde se usa IA y con qué límites?**
En la auditoría de asistentes (objeto de estudio) y en un extractor de menciones para coreano y chino (herramienta). Cada componente tiene función, modelo, validación y limitaciones documentadas. Evidencia: [`docs/ia-responsable.md`](../ia-responsable.md).
