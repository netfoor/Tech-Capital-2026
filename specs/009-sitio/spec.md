# Spec 009 · Sitio

| | |
|---|---|
| Contexto | Publicación |
| Prioridad | P0 |
| Estado | En curso: andamiaje en `web/` |
| Depende de | 001 y 002 (primera versión), 006 y 008 (versión completa), 010 (despliegue) |
| Habilita | 011 (demostración) |

## Bases que atiende

FIN-01 a FIN-09 (versión funcional y demostración), ENT-08 (prototipo), RUB-04 (solidez técnica), RUB-07 (experiencia de usuario y utilidad) y RUB-08 (demostración).

## Objetivo

Un sitio estático, rápido y verificable donde un funcionario o un jurado entiende en dos minutos:
1. el problema;
2. qué destinos están subexpuestos;
3. por qué;
4. qué hacer con eso rumbo al Tianguis.

## Historias de usuario

**H1 (P0).** Como funcionario, quiero ver en un mapa los 12 Pueblos Mágicos coloreados por su brecha y elegir uno para ver su ficha.
- Dado el sitio, cuando hago clic en un destino del mapa, de la tabla o de la gráfica de cuadrantes, entonces se selecciona en todas las vistas y se abre su ficha.

**H2 (P0).** Como asistente a una cita de negocio en el Tianguis, quiero descargar la ficha de un destino.
- Dada una ficha, cuando pulso «Descargar ficha», entonces obtengo una versión imprimible (PDF desde el navegador con estilos de impresión) con cifras, cuadrante, visibilidad por idioma y fuentes.

**H3 (P0).** Como jurado, quiero comprobar que los datos son los que dice el equipo.
- Dado el sitio, cuando carga, entonces verifica la SHA-256 de cada JSON contra el manifiesto y el pie dice «Datos verificados: n de n». Si una huella no coincide, ese bloque no se dibuja y aparece un aviso.

**H4 (P0).** Como jurado, quiero ver qué responden los asistentes según el idioma.
- Dada la sección de asistentes, cuando elijo un idioma o un proveedor, entonces veo la visibilidad de cada destino con su intervalo y los dominios más citados.

**H5 (P0).** Como persona con teléfono, quiero usar el sitio sin zoom ni desbordes.
- Dado un ancho de 390 px, cuando recorro el sitio, entonces no hay desborde horizontal y los textos de las gráficas miden al menos 12 px.

**H6 (P1).** Como presentador, quiero la demostración sin internet.
- Dado `web/dist/`, cuando lo sirvo localmente sin conexión, entonces el sitio funciona igual. No hay recursos externos.

## Secciones (orden fijo, `docs/diseno.md` §5)

| # | Sección | Contenido | Datos |
|---|---|---|---|
| 1 | Inicio | H1, entrada y mapa animado: ocupación (relleno) y atención (anillo) | `destinos.json`, `radar.json` |
| 2 | El problema | Cuatro hallazgos con su fuente: redes como canal principal, medición hotelera, concentración y Tianguis | `evidencia.json` |
| 3 | Radar | Mapa por brecha, tabla de los 12 y gráfica de cuadrantes | `radar.json`, `geo/*.json` |
| 4 | Fichas de destino | Ficha del destino elegido | `fichas/<destino_id>.json` |
| 5 | Lo que responden los asistentes | Visibilidad por destino con alternas de idioma y proveedor; dominios citados; ejemplo de respuesta | `asistentes.json` |
| 6 | Lo que se ve en redes | Presencia en el panel de TikTok y en YouTube; opinión agregada (P1) | `redes.json` |
| 7 | Para el Tianguis 2027 | Cómo se usa: fichas para citas, comparación por idioma de mercado y medición antes y después; piloto propuesto | texto, `radar.json` |
| 8 | Cómo se hizo | Fuentes, procesos, fórmulas del radar, componentes con IA y limitaciones | `metodo.json` |
| 9 | Datos y código | Descargas (CSV de `data/curado/`), manifiesto, enlace al repositorio | `manifiesto.json` |

## Requisitos funcionales

- **FR-009-01** Astro con salida estática, Tailwind CSS 4 con los tokens de `docs/diseno.md`, d3 7 y anime.js 4. Sin dependencias en tiempo de ejecución fuera del propio sitio.
- **FR-009-02** `radar exportar` genera `web/public/datos/*.json`, los valida contra `contracts/` y escribe `manifiesto.json`.
- **FR-009-03** Verificación de huellas en el navegador con `crypto.subtle.digest('SHA-256')` antes de usar cada archivo.
- **FR-009-04** Selección compartida `seleccionar(destinoId, origen)` entre el mapa, la tabla, la gráfica de cuadrantes, la ficha y la sección de asistentes.
- **FR-009-05** Estilos de impresión para la ficha: una página carta con las cifras y las fuentes.
- **FR-009-06** `prefers-reduced-motion` respetado; todas las animaciones de scroll son reversibles.
- **FR-009-07** Accesibilidad: navegación por teclado, `aria-label` en las gráficas con un resumen textual y contraste según `docs/diseno.md`.
- **FR-009-08** Primera versión desplegable solo con datos de 001 y 002: mapa y desempeño. Así la infraestructura se prueba pronto.

## Requisitos no funcionales

- Peso total del sitio menor a 1.5 MB, sin contar descargas.
- Primer render significativo en menos de 2 s en 4G.
- Compilación (`npm run build`) en menos de 60 s.

## Fuera de alcance

- Inicio de sesión, edición de datos o API en vivo (ADR-0002).
- Versión en inglés del sitio (se puede agregar después para el Tianguis).

## Preguntas abiertas

- Logos: el encabezado usa los de las instituciones del equipo. ¿Se piden los logos de Tech Capital e Intelligentia para el pie, con permiso? Mientras tanto se nombra el evento en texto.
