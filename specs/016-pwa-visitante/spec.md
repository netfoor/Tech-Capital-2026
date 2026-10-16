# Spec 016 · PWA del visitante

| | |
|---|---|
| Contexto | Experiencia del visitante (B2C) |
| Prioridad | P0 |
| Estado | MVP implementado: flujos P0 con modo de demostración y tipos alineados al contrato de la API; falta la prueba de punta a punta con el backend real |
| Depende de | 014 (API y modelo de datos); 015 (recomendador) para itinerarios reales |
| Habilita | 017 (recorridos), 018 (moderación), 020 (accesibilidad y privacidad), 022 (importar y compartir) |

## Bases que atiende

FIN-08 (funcionamiento demostrable de la solución), y los criterios de experiencia de usuario, inclusión y viabilidad técnica de la rúbrica. Contexto maestro §04.4 (L2, L3, L4), §05, §06.1, §06.3–6.5, §06.8, §14 y §17 (escenas 1 y 3).

## Objetivo

Que una persona sin cuenta descubra lugares de Puebla con información de accesibilidad honesta, los guarde en su mapa, arme un plan que respete sus necesidades y reporte lo que encontró. La lista es la vista principal; el mapa es su equivalente.

## Historias de usuario

**H1 (P0). Descubrir.** Como visitante, quiero ver lugares en lista y en mapa y filtrarlos por interés, destino, costo y accesibilidad.
- Dado el catálogo, cuando marco «sin escalones», entonces solo veo lugares cuyo dato de acceso sin escalones es «sí» y no fue reportado como barrera.
- Dado el filtro «solo atributos verificados», cuando lo activo junto con «sin escalones», entonces solo quedan los lugares con ese atributo en estado «verificado».
- Dado el mapa, cuando lo abro, entonces muestra los mismos lugares que la lista y la atribución «© OpenStreetMap contributors».

**H2 (P0). Ficha.** Como visitante, quiero saber qué tan accesible es un lugar y de dónde viene cada dato.
- Dado un atributo sin dato, cuando abro la ficha, entonces dice «Sin verificar», nunca «accesible».
- Dado un atributo, cuando se muestra su estado, entonces lleva ícono y texto (no solo color), su origen y su fecha.
- Dada una barrera reportada, cuando abro la ficha, entonces aparece con su tipo, estado y fecha.

**H3 (P0). Guardar en mi mapa.** Como visitante sin cuenta, quiero guardar lugares con mis etiquetas y una nota privada.
- Dado un lugar, cuando pulso «Guardar en mi mapa», entonces queda guardado en este dispositivo y el botón cambia a «Guardado».
- Dado «Mi mapa», cuando lo abro, entonces veo mis lugares agrupados por destino, en lista y en mapa, y puedo filtrar por etiqueta.
- Dado un navegador que bloquea el almacenamiento, cuando guardo, entonces la app no falla y avisa que no se podrá conservar.

**H4 (P0). Planear desde cero.** Como visitante, quiero un plan para las horas que tengo, con mis intereses, presupuesto y necesidades de acceso opcionales.
- Dado «4 horas, sin escalones, descansos cada 30 min, presupuesto bajo», cuando pido el plan, entonces ninguna parada viola esas restricciones, cada parada dice por qué se recomienda y qué datos no sabemos, y los lugares descartados dicen su motivo.

**H5 (P0). Planear desde mis guardados.** Como visitante, quiero convertir mis guardados en un plan por días.
- Dados 6 guardados, 2 días y 5 horas por día, cuando pido el plan, entonces recibo paradas por día, los que no caben con su motivo y hasta 2 alternativas marcadas «sugerencia».
- Dado un plan, cuando reordeno o quito paradas y lo guardo, entonces queda en «Mis planes» de este dispositivo.

**H6 (P0). Reportar y reseñar.** Como visitante, quiero reportar una barrera y calificar el lugar por dimensiones.
- Dado el formulario de barrera sin tipo, cuando lo envío, entonces veo un error que explica qué falta y el foco va al campo.
- Dada una reseña, cuando la envío, entonces cada dimensión va de 1 a 5 y el texto es opcional.

**H7 (P0). Lenguaje claro.** Como visitante, quiero una versión con frases más simples y menos información a la vez.

**H8 (P0). Sin conexión.** Como visitante con mala señal, quiero abrir la app y ver los últimos lugares consultados.

## Requisitos funcionales

- **FR-016-01** Rutas: `/` (Descubrir), `/lugar/:poiId` (ficha), `/lugar/:poiId/reportar`, `/lugar/:poiId/resena`, `/mi-mapa`, `/planear` y `/recorrido` (placeholder de la spec 017). `/admin` pertenece a otra spec.
- **FR-016-02** Cliente tipado en `frontend/src/api/` que respeta el contrato de la spec 014 (JSON snake_case, base `/api`).
- **FR-016-03** Modo de datos de demostración: si la API no responde (error de red, 404 o 5xx), la app usa un conjunto pequeño de POI sintéticos y muestra la banda «DATOS SINTÉTICOS DE DEMOSTRACIÓN» en todas las pantallas. Si un POI real trae `is_synthetic=true`, se muestra la misma etiqueta.
- **FR-016-04** Filtros reflejados en la URL para poder volver o compartir la búsqueda.
- **FR-016-05** La ficha muestra los 9 atributos de accesibilidad siempre, cada uno con valor, estado, origen y fecha; sin dato = «Sin verificar».
- **FR-016-06** Guardados, etiquetas, notas y planes en `localStorage`, con cada acceso en `try/catch`.
- **FR-016-07** Planear en dos modos, con edición (subir, bajar, quitar) y guardado del plan.
- **FR-016-08** Formularios de barrera y reseña con validación comprensible.
- **FR-016-09** PWA instalable: manifest en español, iconos locales, service worker con caché del shell y de la última respuesta de POI.
- **FR-016-10** Cadenas centralizadas en `frontend/src/i18n/es.ts`, con variante de lenguaje claro.

## Requisitos no funcionales

- WCAG 2.2 AA: landmarks, teclado completo, foco visible, objetivos de 24×24 px o más, contraste AA, estados con ícono y texto, `prefers-reduced-motion`, errores comprensibles.
- axe sin violaciones en los componentes P0 (pruebas automatizadas).
- Funciona a 390 px de ancho sin scroll horizontal.
- Sin fuentes ni recursos de CDN. Los únicos recursos externos son los mosaicos del mapa (OpenFreeMap) y la API propia.
- La interfaz no menciona las herramientas con que se construyó (constitución, X).
- No pide GPS para explorar, guardar ni planear (§05, §14).

## Fuera de alcance

- Sesión de recorrido, GPS, paradas y bitácora (spec 017). Solo se deja la pantalla «Mi recorrido» con un aviso honesto.
- Moderación de reportes (spec 018) y tablero (spec 019).
- Pegar enlace, compartir por enlace y Web Share Target (spec 022, P1).
- Sincronizar guardados con una cuenta: el cliente de `/auth` existe, pero el MVP guarda en local.
- Fotos en reportes de barrera (P1, requiere borrado de EXIF de la spec 020).

## Preguntas abiertas

- 2026-10-16: el contrato no fija los valores de `costo_rango` ni de `costo_max`. Se asume la misma escala que `presupuesto` (`gratis`, `bajo`, `medio`, `alto`) y `costo_max` recibe uno de esos valores. Confirmar con la spec 014.
- 2026-10-16: el contrato no lista las categorías. La interfaz traduce las conocidas (museo, templo, zona arqueológica, mirador, mercado, parque, plaza, artesanías, gastronomía) y muestra cualquier otra con su nombre tal cual.
- 2026-10-16: el horario llega como texto de OpenStreetMap (`horario_osm`) sin fecha. La ficha muestra el texto traducido de forma simple y la fuente «OpenStreetMap»; la fecha queda pendiente del contrato.
- 2026-10-16: en modo de demostración, las reseñas y los reportes no se envían; se avisa que quedaron solo en este dispositivo. El plan se calcula con un motor local sencillo que respeta las mismas restricciones indispensables; no sustituye al recomendador de la spec 015.
- 2026-10-16: con «sin escalones», un lugar sin dato se excluye del plan (opción conservadora, constitución XIII) y aparece en «no incluidos» con el motivo «no sabemos si tiene acceso sin escalones».
- 2026-10-16 (resuelto): el contrato real (`docs/api/contrato-p0.md`) fija `costo_rango` en `gratis|bajo|medio|alto|null`, valores `si|no|limitado` y números en texto. La interfaz trata «limitado» como que **no** cumple una necesidad indispensable.
- 2026-10-16: reseñas y reportes requieren cuenta. Se agregó `/cuenta` (registro e inicio de sesión opcionales). Sin sesión, el envío queda en el dispositivo y se dice por qué; falta reenviarlo automáticamente al iniciar sesión.
- 2026-10-16: en la reseña solo `global` es obligatoria, según el contrato. El reporte de barrera acepta una foto opcional en base64; el servidor le quita los metadatos.
