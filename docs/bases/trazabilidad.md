# Matriz de trazabilidad con la convocatoria

Fuente: [`convocatoria-hackathon-puebla-turistica-360.pdf`](convocatoria-hackathon-puebla-turistica-360.pdf) (8 páginas; archivo creado el 24 de septiembre de 2026; SHA-256 `d58b3cea…1d52`). El cartel de difusión ([`cartel-hackathon.png`](cartel-hackathon.png)) corresponde al mismo evento. Fechas: 15 al 17 de octubre de 2026, de 11:00 a 17:00, Centro Expositor.

Cada requisito tiene un identificador que las specs citan en su sección «Bases que atiende».

**Estados**
- **Planeado:** ya tiene spec y tareas.
- **En curso:** hay implementación parcial.
- **Hecho:** está implementado y verificado.
- **Riesgo:** la cobertura es débil y se indica cómo reforzarla.

## 1. Participación (§4)

| ID | Requisito | Cómo se atiende | Estado |
|---|---|---|---|
| PAR-01 | Tres estudiantes y un profesor tutor | Registro del equipo realizado; integración en `README.md` § Equipo | Hecho |
| PAR-02 | Solución, desarrollo y presentación hechos primordialmente por los estudiantes; el tutor orienta | Toda decisión de diseño queda registrada en `docs/decisiones/`; el tutor revisa la metodología (spec 011) | Planeado |
| PAR-03 | Equipo multidisciplinario | Perfiles de datos e IA, nube, y economía y derecho | Hecho |

## 2. Datos (§5)

| ID | Requisito | Cómo se atiende | Spec | Estado |
|---|---|---|---|---|
| DAT-01 | Proponer, localizar, seleccionar, obtener, documentar y justificar los datos | Registro `data/fuentes/fuentes.csv`, inventario `docs/entregables/04-inventario-fuentes.md` y justificación `05-justificacion-datos.md` | 001–007, 011 | En curso |
| DAT-02 | Explicar qué información se necesita, por qué es pertinente, de dónde proviene, cómo se obtuvo, qué calidad tiene, cómo se preparó y cómo genera evidencia | Cada fuente tiene una ficha con esos siete campos en el inventario | 011 | Planeado |
| DAT-03 | Fuentes legítimas y legales: datos abiertos, APIs, repositorios públicos, datos propios | Fuentes oficiales (Sectur Puebla, INEGI), APIs oficiales (YouTube Data, OpenAI, Gemini), Google Trends y datos propios del panel con consentimiento | 002–006 | En curso |
| DAT-04 | Integrar múltiples fuentes documentando procedencia, condiciones de uso y metodología de integración | Catálogo de destinos como llave común (claves INEGI); integración descrita en `docs/dominio/modelo-de-datos.md` y spec 008 | 001, 008 | Planeado |
| DAT-05 | Respetar licencias, términos de uso, privacidad y protección de datos | Constitución IV; datos del panel anonimizados; comentarios solo agregados; datos crudos de YouTube fuera del repositorio | 004, 005, 007 | Planeado |
| DAT-06 | Justificar la IA y explicar su valor; la incorporación superficial no basta | `docs/ia-responsable.md`: la IA es objeto de estudio (auditoría de asistentes) y herramienta validada (clasificación de comentarios, extracción de capturas) | 006, 007 | Planeado |

## 3. Mentoría (§7)

| ID | Requisito | Cómo se atiende | Estado |
|---|---|---|---|
| MEN-01 | Presentar problemática, usuario o beneficiario, hipótesis, solución, datos, metodología y tecnologías | `docs/entregables/mentoria.md`, con una sección para cada uno de los siete elementos | En curso: material listo |

## 4. Etapa final (§8)

| ID | Requisito | Cómo se atiende | Spec | Estado |
|---|---|---|---|---|
| FIN-01 | Versión funcional o demostrable | Plataforma con cuentas de usuario (Cognito) y página pública, desplegadas en un subdominio de foor.dev con datos reales (ADR-0009) | 009, 010 | En curso |
| FIN-02 | Pitch ejecutivo | `docs/entregables/10-pitch.md`: guion por tiempos | 011 | Planeado |
| FIN-03 | Demostración | Recorrido guiado del sitio, con una versión de respaldo sin conexión | 009, 011 | Planeado |
| FIN-04 | Ronda de preguntas | `docs/entregables/preguntas-del-jurado.md` | 011 | Planeado |
| FIN-05 | La presentación expone el problema | Sección «El problema» del sitio y del pitch | 009, 011 | Planeado |
| FIN-06 | La presentación expone la evidencia | `docs/producto/evidencia.md` y la misma sección del sitio | 009, 011 | Planeado |
| FIN-07 | La presentación expone los datos y la metodología | Sección «Cómo se hizo» del sitio | 008, 009 | Planeado |
| FIN-08 | La presentación muestra el funcionamiento de la solución | Radar, fichas y auditoría en vivo | 008, 009 | Planeado |
| FIN-09 | La presentación explica el papel de la IA o de la ciencia de datos | Sección del sitio y `docs/ia-responsable.md` | 006, 007, 009 | Planeado |
| FIN-10 | La presentación expone los beneficios para el visitante | Ver OBJ-03 | 011 | **Riesgo**, ver OBJ-03 |
| FIN-11 | La presentación expone el impacto para Puebla | Derrama potencial por destino (escenarios) y desconcentración hacia los Pueblos Mágicos | 008, 011 | Planeado |
| FIN-12 | La presentación expone la viabilidad de escalamiento | `docs/entregables/modelo-de-operacion.md`: costos, operación y extensión a otros estados | 010, 011 | Planeado |

## 5. Entregables (§9)

| ID | Entregable | Archivo | Spec | Estado |
|---|---|---|---|---|
| ENT-01 | Descripción ejecutiva del proyecto | `docs/entregables/01-descripcion-ejecutiva.md` | 011 | Planeado |
| ENT-02 | Definición del problema y de usuarios o beneficiarios | `docs/entregables/02-problema-y-usuarios.md` (parte de `docs/producto/`) | 011 | En curso |
| ENT-03 | Descripción de la solución | `docs/entregables/03-solucion.md` | 011 | Planeado |
| ENT-04 | Inventario y documentación de fuentes | `docs/entregables/04-inventario-fuentes.md`, generado desde `data/fuentes/fuentes.csv` | 011 | En curso |
| ENT-05 | Justificación de la selección de datos | `docs/entregables/05-justificacion-datos.md` | 011 | Planeado |
| ENT-06 | Procesos de obtención, limpieza, integración, transformación y análisis | `docs/entregables/06-procesos-de-datos.md` (resume `plan.md` de 002–008) | 011 | Planeado |
| ENT-07 | Arquitectura o metodología | `docs/arquitectura.md` y `docs/entregables/07-arquitectura.md` | 010, 011 | En curso |
| ENT-08 | Prototipo funcional o demostrable | URL del sitio y repositorio | 009, 010 | En curso |
| ENT-09 | Evidencia de análisis y resultados | `docs/entregables/09-resultados.md`, generado desde `data/curado/` | 008, 011 | Planeado |
| ENT-10 | Presentación ejecutiva y demostración final | `docs/entregables/10-pitch.md` y la presentación | 011 | Planeado |
| ENT-11 | Documentación del modelo de IA: configuración, variables, resultados y limitaciones | `docs/ia-responsable.md` | 006, 007 | Planeado |

## 6. Rúbrica (§11)

| ID | Criterio | Peso | Cómo se atiende | Evidencia esperada |
|---|---|---|---|---|
| RUB-01 | Relevancia y comprensión del problema | 15 % | Problema validado con datos del propio observatorio estatal: redes como canal principal, medición solo hotelera, brecha de los Pueblos Mágicos, Tianguis 2027 | `docs/producto/evidencia.md` |
| RUB-02 | Identificación, pertinencia, calidad y aprovechamiento de los datos | 20 % | Siete familias de fuentes, con procedencia y SHA-256; calidad evaluada (medido o derivado); integración con llave INEGI; metodología declarada | Inventario, `data/curado/`, manifiesto |
| RUB-03 | Innovación y creatividad | 15 % | Se crea una fuente de datos inexistente (panel de TikTok y auditoría multilingüe de asistentes) y se cruza con la serie oficial | Specs 005, 006 y 008 |
| RUB-04 | Solidez técnica y prototipo | 15 % | Pipelines reproducibles con uv, contratos JSON, sitio estático en AWS con Terraform y pruebas | `make verificar`, sitio desplegado |
| RUB-05 | Impacto turístico, económico y social | 15 % | Desconcentración hacia los Pueblos Mágicos; derrama potencial; insumo para el Tianguis 2027; beneficios para prestadores locales | Escenarios del spec 008 |
| RUB-06 | Viabilidad, implementación y escalabilidad | 10 % | Costos reales de operación; panel que se convierte en datos propios de la Secretaría; extensible a cualquier destino | `modelo-de-operacion.md` |
| RUB-07 | Experiencia de usuario y utilidad | 5 % | Sitio con mapa, fichas y selección compartida, diseñado para funcionarios y para citas de negocio, accesible y legible en teléfono | Spec 009, `docs/diseno.md` |
| RUB-08 | Pitch y demostración | 5 % | Guion ensayado, demostración de respaldo y preguntas preparadas | Spec 011 |

## 7. Criterios complementarios (§12)

| ID | Categoría | Criterios | Cómo se atiende |
|---|---|---|---|
| CAT-DAT | Mejor solución basada en datos | Calidad y diversidad de fuentes, metodología, profundidad del análisis, indicadores o predicciones, información accionable, reproducibilidad | Diversidad de siete familias; modelo con rezago contra línea base; reproducibilidad con `make datos` y SHA-256 |
| CAT-IA | Mejor uso de IA | Pertinencia, calidad técnica, integración, evidencia, valor adicional, explicabilidad, uso responsable; «el simple consumo de una API o un chatbot genérico no será suficiente» | La IA como objeto de medición (visibilidad en cinco idiomas, con fuentes citadas) y la clasificación validada contra etiquetas humanas; documentación de límites |
| CAT-SOS | Turismo sostenible | Desconcentración de flujos, desarrollo económico local, fortalecimiento comunitario, desarrollo regional | El radar prioriza destinos con capacidad disponible y la Sierra Norte y Nororiental; se vincula con las experiencias de turismo comunitario |

Regla de la convocatoria: un proyecto puede obtener el Gran Premio y además una sola categoría especial.

## 8. Objetivos (§3)

| ID | Objetivo | Cobertura | Cómo |
|---|---|---|---|
| OBJ-01 | Aprovechamiento estratégico de datos | Alta | Todo el radar |
| OBJ-02 | Uso responsable y pertinente de IA y ciencia de datos | Alta | `docs/ia-responsable.md` y constitución VII |
| OBJ-03 | Mejorar la experiencia del visitante antes, durante y después | **Media** | Antes del viaje: el visitante encuentra información correcta y completa de más destinos porque la Secretaría corrige y amplía lo que se ve en redes y asistentes. Durante: las fricciones que aparecen en los comentarios (acceso, precios, servicios) se convierten en acciones. Refuerzo P2: reporte de omisiones y errores de los asistentes por destino (spec 006, historia 4) |
| OBJ-04 | Herramientas para comprender y optimizar flujos | Alta | Atención frente a ocupación por destino y mes |
| OBJ-05 | Mayor distribución de los beneficios económicos | Alta | Prioriza destinos con capacidad disponible fuera de la capital |
| OBJ-06 | Turismo sostenible, accesible e incluyente | Media | Desconcentración de flujos; el sitio cumple criterios de accesibilidad |
| OBJ-07 | Decisiones basadas en evidencia | Alta | Mide el resultado de la promoción, no solo las impresiones |
| OBJ-08 | Vincular estudiantes y profesores con especialistas | Media | Validación con la Secretaría en la mentoría y la final |
| OBJ-09 | Potencial de continuidad, incubación o piloto | Alta | Piloto de noviembre de 2026 a marzo de 2027, con medición antes y después del Tianguis |

## 9. Otras disposiciones

| ID | Sección | Requisito | Cómo se atiende |
|---|---|---|---|
| PI-01 | §14 | La propiedad intelectual queda con los autores; licencia de difusión no exclusiva, gratuita y no comercial para los organizadores | `README.md` § Propiedad intelectual; la licencia del código queda como decisión del equipo |
| PI-02 | §15 | Acompañamiento institucional para protección y registro | Opcional; registrar como siguiente paso en `modelo-de-operacion.md` |
| USO-01 | §16 | Fuentes legítimas, derechos de autor, licencias, términos, privacidad y datos personales | Constitución IV; aviso de privacidad y consentimiento del panel (spec 005) |
| USO-02 | §16 | Explicar qué componentes usan IA, su función y sus límites | `docs/ia-responsable.md` |
| CON-01 | §17 | Continuidad: mentoría, incubación, pruebas piloto, validación con usuarios | `modelo-de-operacion.md` § Piloto |
| GEN-01 | §18 | Aceptación de las bases; el comité resuelve lo no previsto | Las dudas abiertas se registran en `docs/entregables/mentoria.md` § Preguntas al comité |

## 10. Dudas abiertas sobre las bases

- La convocatoria no publica premios, duración del pitch ni el día de presentación de cada equipo dentro del 15 al 17 de octubre.
- El §1 menciona mentorías en «las primeras semanas de octubre» y el §7 habla de «una única sesión». Se tratan como una sola sesión.
- El cartel dice «categoría libre» y el PDF fija el tema «Puebla Turística 360°». Se sigue el PDF.
