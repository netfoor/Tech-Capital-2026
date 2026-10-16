# Constitución del proyecto

Principios de Puebla Viva 360 que toda especificación, plan, tarea y línea de código debe respetar. Si una tarea choca con un principio, se detiene y se registra el conflicto en la sección «Preguntas abiertas» de su spec; no se resuelve en silencio.

## I. Las bases mandan

La convocatoria (`docs/bases/convocatoria-hackathon-puebla-turistica-360.pdf`) es el requisito de mayor jerarquía. Cada funcionalidad declara qué requisito de las bases atiende, y la matriz `docs/requirements.md` se mantiene al día.

- Verificación: toda spec tiene la sección «Bases que atiende» con referencias a `§` de la convocatoria.

## II. Especificación antes que código

Nada se implementa sin `spec.md` → `plan.md` → `tasks.md`. Un cambio de comportamiento se refleja primero en la spec y después en el código. Las tareas se marcan como hechas solo cuando su verificación pasa.

- Verificación: cada commit de código referencia una tarea (`T###`) de alguna spec.

## III. Cada cifra con procedencia

Todo dato publicado se puede rastrear hasta una fuente registrada en `data/fuentes/fuentes.csv`: URL, fecha de consulta y SHA-256 cuando hay archivo. Los indicadores distinguen entre **medido** (registro directo, por ejemplo DataTur) y **derivado** (calculado por la fuente con un factor o supuesto). Ninguna cifra se escribe a mano en el sitio ni en los documentos de entrega: se genera desde `data/curado/`.

- Verificación: cada indicador de `backend/metrics/definitions.yaml` declara su fuente y cada tabla curada tiene su fila en `data/catalog/data_catalog.csv`.

## IV. Recolección legítima y respeto a las personas

Solo se usan fuentes públicas, APIs oficiales dentro de sus términos y datos aportados con consentimiento. No se automatiza el acceso a plataformas en contra de sus términos. Los datos del panel se anonimizan en el origen; los comentarios de terceros se publican solo como conteos agregados, nunca con nombre de usuario ni texto literal identificable.

- Verificación: `data/privado/` y `data/crudo/` están en `.gitignore`; los contratos publicados no tienen campos de identidad personal.

## V. Reproducibilidad

Cualquier persona con el repositorio y las llaves puede regenerar todo con `make datos`. Las fuentes originales son inmutables. Los procesos son deterministas o registran semilla, modelo, versión y parámetros. Las corridas contra servicios externos guardan la respuesta cruda y la fecha.

- Verificación: `make datos` en un clon limpio produce los mismos archivos de `data/curado/` (misma SHA-256) salvo los que dependen de una corrida nueva fechada.

## VI. Honestidad estadística

Se reporta el tamaño de muestra, la incertidumbre y las limitaciones de cada resultado. Una correlación no se presenta como causa. Un resultado sin evidencia suficiente se dice así: «sin evidencia suficiente». Los modelos se comparan contra una línea base simple.

- Verificación: cada métrica del radar declara `n` y método; cada modelo reporta su comparación contra la línea base.

## VII. IA con propósito y explicable

La IA se usa donde aporta algo que no se lograría sin ella: como **objeto de estudio** (qué recomiendan los asistentes) y como **herramienta de clasificación o extracción** validada contra una muestra revisada por personas. Para cada componente con IA se documenta su función, modelo, parámetros, validación y límites en `docs/ia/`. Un chatbot genérico no es parte de la solución.

- Verificación: ningún componente con IA se integra sin su ficha en `docs/ia/` y su comparación contra una línea base.

## VIII. Lo mínimo demostrable primero

Se construye en orden de prioridad: P0 (indispensable para la demostración), luego P1 y al final P2. Una funcionalidad P0 terminada y desplegada vale más que tres P1 a medias.

- Verificación: no se abre una tarea P1 mientras exista una P0 desbloqueada sin dueño.

## IX. Seguridad de llaves y datos

Las llaves viven en `.env` (local) o en un gestor de secretos; nunca en el repositorio, en registros ni en el sitio. El sitio es estático y no expone llaves. Los datos personales viven en el esquema `private` y nunca salen en una respuesta pública.

- Verificación: `make verificar` busca patrones de llaves en los archivos versionados.

## X. Escritura clara

Todo en español de México, con voz activa y frases cortas. Los documentos y el sitio no hablan de las herramientas con que se construyó el proyecto; hablan del problema, los datos y la solución.

## XI. Nadie es objeto de vigilancia

La ubicación se registra solo con consentimiento específico y durante una sesión que la persona inicia, pausa y detiene. No hay rastreo oculto ni ubicación pública en vivo. La Secretaría ve agregados, nunca personas: cada indicador publicado suprime los grupos con menos de k observaciones.

- Verificación: una prueba comprueba que ninguna respuesta pública ni del tablero contiene coordenadas crudas, y otra que los agregados con n < k se suprimen.

## XII. Lo sintético se nota

Todo dato sintético vive en archivos o filas con `is_synthetic=true` y se muestra con la etiqueta «DATOS SINTÉTICOS DE DEMOSTRACIÓN». Se separan siempre cuatro estados: producto objetivo, MVP implementado, demo sintética y resultado medido.

- Verificación: las pruebas del tablero fallan si un agregado mezcla filas sintéticas y reales sin marcarlo.

## XIII. Accesibilidad de primera clase

La falta de un dato de accesibilidad se muestra como «sin verificar», nunca como «accesible». Una restricción indispensable del visitante nunca se viola. La interfaz busca WCAG 2.2 AA y la lista es la vista principal, no un extra del mapa.

- Verificación: pruebas unitarias del recomendador con 0 violaciones de restricciones indispensables, y axe sin errores en los flujos P0.
