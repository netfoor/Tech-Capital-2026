# Spec 009 · Sitio: página pública y plataforma

| | |
|---|---|
| Contexto | Publicación |
| Prioridad | P0 |
| Estado | En curso: andamiaje de la página pública y de la plataforma con acceso en `web/` |
| Depende de | 001 y 002 (primera versión), 006 y 008 (versión completa), 010 (despliegue y Cognito) |
| Habilita | 011 (demostración) |

## Bases que atiende

FIN-01 a FIN-09 (versión funcional y demostración), ENT-08 (prototipo), RUB-04 (solidez técnica), RUB-06 (viabilidad: se ve y se usa como producto), RUB-07 (experiencia de usuario y utilidad) y RUB-08 (demostración).

## Objetivo

Dos superficies sobre los mismos datos ([ADR-0009](../../docs/decisiones/0009-landing-publica-y-plataforma-con-cognito.md)):

1. **Página pública (`/`)**: en dos minutos, un funcionario o un jurado entiende el problema, qué hace la plataforma, cómo se usa rumbo al Tianguis y cómo se hizo.
2. **Plataforma (`/plataforma/`)**: la herramienta que usaría la Secretaría. Con sesión, permite ver qué destinos están subexpuestos y por qué, abrir y descargar la ficha de cada uno, y comparar qué responden los asistentes y qué se ve en redes.

## Historias de usuario

**H1 (P0).** Como funcionario con cuenta, quiero entrar a la plataforma con mi correo.
- Dado que no tengo sesión, cuando abro `/plataforma/`, entonces me lleva al inicio de sesión de Cognito y al volver veo la vista Radar con mi correo y «Salir» en la barra. Al salir, la sesión se borra y vuelvo a la página pública.

**H2 (P0).** Como funcionario, quiero ver en un mapa los 12 Pueblos Mágicos coloreados por su brecha y elegir uno para ver su ficha.
- Dada la vista Radar, cuando hago clic en un destino del mapa, de la tabla o de la gráfica de cuadrantes, entonces se selecciona en todas las vistas, se abre su ficha en el panel lateral y la dirección cambia a `#radar/<destino_id>`.

**H3 (P0).** Como asistente a una cita de negocio en el Tianguis, quiero descargar la ficha de un destino.
- Dada una ficha, cuando pulso «Descargar para la cita», entonces obtengo una versión imprimible (PDF desde el navegador, una hoja carta) con cifras, cuadrante, visibilidad por idioma y fuentes.

**H4 (P0).** Como jurado, quiero comprobar que los datos son los que dice el equipo.
- Dado el sitio, cuando carga datos, entonces verifica la SHA-256 de cada JSON contra el manifiesto y muestra «Datos verificados: n de n». Si una huella no coincide, ese bloque no se dibuja y aparece un aviso.

**H5 (P0).** Como jurado, quiero ver qué responden los asistentes según el idioma.
- Dada la vista Asistentes, cuando elijo un idioma o un proveedor, entonces veo la visibilidad de cada destino con su intervalo y los dominios más citados.

**H6 (P0).** Como persona sin cuenta, quiero entender el proyecto y revisar el método.
- Dada la página pública, cuando la recorro, entonces veo el problema con su evidencia, las cuatro vistas de la plataforma con capturas reales, el uso para el Tianguis, el método y las descargas, sin iniciar sesión.

**H7 (P0).** Como persona con teléfono, quiero usar el sitio sin zoom ni desbordes.
- Dado un ancho de 390 px, cuando recorro la página pública y la plataforma, entonces no hay desborde horizontal, los textos de las gráficas miden al menos 12 px y el panel de ficha ocupa la pantalla completa.

**H8 (P1).** Como presentador, quiero la demostración sin internet.
- Dado `web/dist/` compilado en modo local, cuando lo sirvo sin conexión, entonces la página pública y la plataforma funcionan igual. No hay recursos externos.

## Superficies

**Página pública** (orden fijo, `docs/diseno.md` §5.1)

| # | Sección | Contenido | Datos |
|---|---|---|---|
| 1 | Inicio | H1, entrada, «Entrar a la plataforma» y mapa animado: ocupación (relleno) y atención (anillo) | `destinos.json`, `radar.json` |
| 2 | El problema | Cuatro hallazgos con su fuente: redes como canal principal, medición hotelera, concentración y Tianguis | `evidencia.json` |
| 3 | La plataforma | Las cuatro vistas con capturas reales y para qué sirve cada una | capturas de la plataforma |
| 4 | Para el Tianguis 2027 | Fichas para citas, comparación por idioma de mercado, medición antes y después y piloto propuesto | texto, `radar.json` |
| 5 | Cómo se hizo | Fuentes, procesos, fórmulas del radar, componentes con IA y limitaciones | `metodo.json` |
| 6 | Datos y código | Descargas (CSV de `data/curado/`), manifiesto y enlace al repositorio | `manifiesto.json` |

**Plataforma** (`docs/diseno.md` §5.2)

| Vista | Ruta | Contenido | Datos |
|---|---|---|---|
| Radar | `#radar`, `#radar/<destino_id>` | Mapa por brecha, tabla de los 12, gráfica de cuadrantes y panel de ficha | `radar.json`, `geo/*.json`, `fichas/*.json` |
| Fichas | `#fichas` | Las 12 fichas con descarga | `fichas/*.json` |
| Asistentes | `#asistentes` | Visibilidad con alternas de idioma y proveedor, dominios citados y un ejemplo | `asistentes.json` |
| Redes | `#redes` | Panel de TikTok, YouTube y opinión agregada (P1) | `redes.json` |

## Requisitos funcionales

- **FR-009-01** Astro con salida estática, Tailwind CSS 4 con los tokens de `docs/diseno.md`, d3 7 y anime.js 4. Sin dependencias en tiempo de ejecución fuera del propio sitio y de Cognito.
- **FR-009-02** `radar exportar` genera `web/public/datos/*.json`, los valida contra `contracts/` y escribe `manifiesto.json`.
- **FR-009-03** Verificación de huellas en el navegador con `crypto.subtle.digest('SHA-256')` antes de usar cada archivo.
- **FR-009-04** Selección compartida `seleccionar(destinoId, origen)` entre el mapa, la tabla, la gráfica de cuadrantes, el panel de ficha y la vista de asistentes, sincronizada con la ruta.
- **FR-009-05** Estilos de impresión para la ficha: una hoja carta con las cifras y las fuentes.
- **FR-009-06** `prefers-reduced-motion` respetado; las animaciones de scroll de la página pública son reversibles.
- **FR-009-07** Accesibilidad: navegación por teclado, `aria-label` en las gráficas con un resumen textual y contraste según `docs/diseno.md`.
- **FR-009-08** Primera versión desplegable solo con datos de 001 y 002: mapa y desempeño en la página pública y en la vista Radar. Así la infraestructura se prueba pronto.
- **FR-009-09** Acceso con Cognito Hosted UI (`src/scripts/acceso.js`): código de autorización con PKCE (S256) y `state`, intercambio en `/oauth2/token`, token en `sessionStorage`, caducidad respetada y cierre con `/logout`. La configuración pública llega por `PUBLIC_COGNITO_DOMINIO` y `PUBLIC_COGNITO_CLIENTE_ID` en `web/.env` (lo escribe `make web-config`).
- **FR-009-10** Modo local: sin `PUBLIC_COGNITO_DOMINIO`, la plataforma entra sin cuenta y muestra la banda «Modo local». `infra/desplegar.sh` rechaza una compilación en modo local.

## Requisitos no funcionales

- Peso total del sitio menor a 1.5 MB, sin contar descargas.
- Primer render significativo en menos de 2 s en 4G.
- Compilación (`npm run build`) en menos de 60 s.

## Fuera de alcance

- Edición de datos o API en vivo (ADR-0002).
- Roles y permisos distintos por usuario: todas las cuentas ven lo mismo.
- Protección de los archivos de datos en CloudFront: son públicos por diseño (ADR-0009).
- Versión en inglés del sitio (se puede agregar después para el Tianguis).

## Preguntas abiertas

- Logos: ¿se piden los logos de Tech Capital e Intelligentia para el pie de la página pública, con permiso? Mientras tanto se nombra el evento en texto.
- ¿Qué cuentas se dan de alta para la demostración? Por defecto: una por integrante y una de demostración para el jurado, creada el día de la presentación.
