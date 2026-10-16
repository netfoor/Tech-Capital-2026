# Decisiones de diseño: sitio del Radar de Atención Turística

Guía para hacer pantallas, secciones o piezas nuevas del sitio (`web/`) con un mismo estilo. El sitio está pensado para dos públicos:

- funcionarios de la Secretaría de Desarrollo Turístico que deciden promoción;
- las personas que asisten a una cita de negocio o a una demostración ante un jurado.

Las dos situaciones piden claridad, sobriedad y datos verificables.

---

## 1. Principios

1. **Las bases y la evidencia mandan.** Solo se muestra lo que piden las bases o lo que respalda un archivo de `data/curado/`. Ninguna cifra se escribe a mano.
2. **Nada debe parecer plantilla.**
   - No hay tarjetas redondeadas por todos lados, ni sombras suaves en cada caja, ni degradados decorativos.
   - No se ponen etiquetas en mayúsculas sobre los títulos ni frases de eslogan como títulos.
   - Las secciones se separan con espacio en blanco y líneas finas.
3. **Lo que se ve debe explicar algo.** Un adorno se queda solo si dice algo del tema. El motivo gráfico (§4) codifica las tres familias de fuentes.
4. **Una sola animación coreografiada al cargar:** la del mapa de la portada. Las demás responden a lo que hace la persona (scroll o clic) y se deshacen al regresar.
5. **Sobre la IA:**
   - Aparece solo como **objeto de estudio** (qué recomiendan los asistentes) o como **componente explicado** (qué hace, cómo se validó y qué límites tiene).
   - El sitio no habla de las herramientas con que se construyó.
6. **El teléfono es un diseño propio**, no la versión de escritorio encogida.
7. **Fondo claro y formal.** Títulos en tinta y en negritas; los acentos de color se reservan para datos y para el motivo.

---

## 2. Tipografía

| Uso | Fuente |
|---|---|
| Todo el texto | `"Amazon Ember", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` |
| Huellas SHA-256, comandos, CSV | `ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace` |

- **Ninguna fuente se descarga.** Si no está Amazon Ember, se usa la del sistema.
- **Referencia de organización:** títulos de sección centrados y en negritas, un acento debajo y el párrafo de entrada centrado.

| Elemento | Tamaño | Peso | Notas |
|---|---|---|---|
| H1 portada | `clamp(38px, 4.2vw, 58px)`, interlineado 1.05 | 800 | `letter-spacing: -0.02em`; máximo tres líneas |
| H2 sección | `clamp(30px, 3.3vw, 44px)`, interlineado 1.12 | 700 | Centrado, color tinta |
| H3 | 18–25 px según el contexto | 700 | Alineado a la izquierda |
| Entrada de sección | 19 px (17 en teléfono), interlineado 1.6 | 400 | Centrada, máximo unos 62 caracteres por línea |
| Cuerpo | 17 px (16 en teléfono), interlineado 1.65 | 400 | — |
| Notas y pies | 14–14.5 px | 400 | Color gris |
| Cifras grandes | 34–46 px | 800 | `font-variant-numeric: tabular-nums` |
| Texto dentro de SVG | 12.5–15 px en unidades del lienzo | 400 / 700 | Ver §8 |

- **Todos los encabezados (h1–h4) llevan peso 700 o más.** El reset de Tailwind los deja en 400; se fija en `global.css`.
- **Los números van con cifras tabulares** (clase `.num`).
- **Las etiquetas** se escriben en frase normal, nunca en mayúsculas.
- **Separadores:** no se juntan datos con puntos medios. Se escribe una frase o se usan dos líneas.

---

## 3. Color

Los colores de marca salen del material de la convocatoria de Tech Capital 2026: verde neón, aguamarina y azul. Se muestrearon del PDF. Sobre fondo blanco, el verde y el aguamarina no tienen contraste suficiente para texto, por eso solo se usan en formas del motivo; para texto existen variantes oscuras.

Los tokens están en `web/src/styles/global.css` dentro de `@theme`.

| Token | Hex | Uso | Contraste sobre blanco |
|---|---|---|---|
| `tinta` | `#111827` | Texto principal y títulos | 17.7 : 1 |
| `tinta-2` | `#374151` | Texto secundario | 10.3 : 1 |
| `gris` | `#6B7280` | Notas, ejes | 4.8 : 1 |
| `linea` | `#E2E5EA` | Bordes y divisores | — |
| `banda` | `#F4F6F8` | Fondo de secciones alternas | — |
| `noche` | `#0E1A2E` | Fondo del pie de página (único bloque oscuro) | — |
| `tc-verde` | `#33F814` | Motivo: datos oficiales (solo formas) | 1.4 : 1 |
| `tc-agua` | `#00E0C8` | Motivo: señales digitales (solo formas) | 1.7 : 1 |
| `tc-azul` | `#0058F8` | Motivo: asistentes; enlaces; botón primario | 5.6 : 1 |
| `verde-texto` | `#1E7D12` | Verde para texto sobre blanco | 5.3 : 1 |
| `agua-texto` | `#00796B` | Aguamarina para texto sobre blanco | 5.3 : 1 |
| `sel` | `#0058F8` | Selección: anillo en el mapa, fila elegida, foco | 5.6 : 1 |

### Escalas de datos

| Escala | Cortes o clases | Colores | Uso |
|---|---|---|---|
| Desempeño (ocupación %) | 6 clases, cortes fijos `30, 38, 46, 54, 62` | `#FDECD3 #F8CF98 #EBA75A #D07F2C #A85A12 #7A3E0B` | Mapa y tablas de ocupación |
| Atención (percentil) | 6 clases, cortes fijos `17, 33, 50, 67, 83` | `#DCE8FE #AFC9FB #7EA6F7 #4C7FF0 #1E5BE3 #0B3FAE` | Componentes de atención |
| Brecha (atención − desempeño) | 7 clases divergentes, centro en 0, cortes `-45, -25, -8, 8, 25, 45` | `#7A3E0B #B45309 #E7B46E #EEF0F3 #8FB3F7 #2F6EEA #0B3FAE` | Mapa principal |

- **Medido** = relleno sólido. **Derivado** = trama de líneas a 45° del mismo color. Así la procedencia no depende solo del color.
- **Cuadrantes**: se rotulan directamente sobre la gráfica, sin leyenda aparte.
  - `consolidado`: `#374151`
  - `atencion_sin_estancia`: `#0058F8`
  - `demanda_poco_visible`: `#B45309`
  - `por_posicionar`: `#00796B`
- **Idiomas** (siempre rotulados):
  - es `#0058F8`
  - en `#00796B`
  - fr `#6D28D9`
  - ko `#B45309`
  - zh `#9F1239`
- **Proveedores de asistentes**: OpenAI `#374151`, Google `#0058F8`. Se rotulan con el nombre del modelo.
- Antes de publicar se verifica el contraste:
  - texto ≥ 4.5 : 1;
  - puntos y líneas de datos ≥ 3 : 1 contra su fondo;
  - los rellenos de área de las clases claras (las dos primeras de cada escala) llevan un borde de 0.5 px en `#9CA3AF`.

**Qué evitar:**
- Negro puro como fondo de página.
- Degradados neón.
- Rojo y verde juntos para codificar.
- Arcoíris.
- Más de siete clases en una escala.

---

## 4. Motivo gráfico propio: cuadrado, paralelogramo, círculo

Al pie de cada página de la convocatoria hay una banda que repite un rectángulo verde, un paralelogramo aguamarina y un círculo azul. En este sitio esas tres formas **representan las tres familias de fuentes del radar**:

| Forma | Color | Familia |
|---|---|---|
| ■ cuadrado | `tc-verde` con borde `verde-texto` | Datos oficiales (Observatorio Turístico, INEGI) |
| ▰ paralelogramo | `tc-agua` con borde `agua-texto` | Señales digitales (búsqueda, YouTube, panel de TikTok) |
| ● círculo | `tc-azul` | Respuestas de asistentes |

Se usa en tres lugares y no en más:
1. **Acento bajo cada H2:** las tres formas pequeñas (8 px) unidas por una línea de 1.5 px en `linea`, centradas.
2. **Marca de origen de cada dato:** la forma de 10 px antes del nombre de la fuente en fichas, tablas y notas. Así se sabe de un vistazo si una cifra es oficial, de señales o de asistentes.
3. **Pie de página:** la banda completa, como en la convocatoria, sobre fondo `noche`.

---

## 5. Estructura: página pública y plataforma

El sitio tiene dos superficies ([ADR-0009](decisiones/0009-landing-publica-y-plataforma-con-cognito.md)). La página pública cuenta la historia y la plataforma es el producto.

### 5.1 Página pública (`/`)

Orden fijo, definido en `web/src/secciones.ts`:

1. Inicio
2. El problema
3. La plataforma
4. Para el Tianguis 2027
5. Cómo se hizo
6. Datos y código

**Encabezado** (sticky, blanco, 64 px; 56 px en teléfono)
- Izquierda: nombre del proyecto en texto. No se usan logos de dependencias de gobierno ni del evento, para no sugerir un respaldo oficial; el evento se nombra en texto.
- Derecha: botón con la sección actual («3 de 6 La plataforma ▾») que abre la lista, y el botón primario «Entrar a la plataforma».
- Abajo: un riel de avance de 2 px. El tramo recorrido va en `tc-azul` y termina en un círculo (la posición actual).

La sección «La plataforma» muestra las cuatro vistas con una imagen real de cada una (capturas de la plataforma con datos) y una frase de para qué sirve. No repite las gráficas completas: invita a entrar.

### 5.2 Plataforma (`/plataforma/`)

Navegación de aplicación, no de documento:

```
┌──────────────────────────────────────────────────────────────────────┐
│ Radar de Atención Turística   Radar  Fichas  Asistentes  Redes   correo  Salir │
├──────────────────────────────────────────────────────────────────────┤
│ Filtros: periodo · componentes · idioma (según la vista)                     │
├───────────────────────────────────────────────┬──────────────────────┤
│ Vista: mapa, tabla o gráficas                 │ Ficha del destino     │
│                                               │ (panel de 420 px)     │
└───────────────────────────────────────────────┴──────────────────────┘
```

| Vista | Contenido | Datos |
|---|---|---|
| Radar (inicio) | Mapa por brecha, tabla de los 12 y gráfica de cuadrantes. Al elegir un destino se abre su ficha en el panel lateral | `radar.json`, `geo/*.json` |
| Fichas | Las 12 fichas en rejilla, cada una con «Descargar para la cita» | `fichas/<destino_id>.json` |
| Asistentes | Visibilidad por destino con alternas de idioma y proveedor, dominios citados y un ejemplo de respuesta | `asistentes.json` |
| Redes | Presencia en el panel de TikTok y en YouTube; opinión agregada (P1) | `redes.json` |

- **Barra superior** (blanca, 56 px, línea inferior en `linea`): nombre del proyecto, las cuatro vistas como enlaces de texto (la activa en tinta, peso 700, con un subrayado de 2 px en `tc-azul`), y a la derecha el correo de la sesión y «Salir». Sin pestañas en forma de píldora.
- **Rutas** por fragmento: `#radar`, `#fichas`, `#asistentes`, `#redes`, y `#radar/<destino_id>` para abrir una ficha. Así cada estado tiene un enlace que se puede compartir.
- **Panel de ficha:** 420 px a la derecha en escritorio; en teléfono ocupa toda la pantalla con un botón «Cerrar». Se cierra con Escape.
- **Estados vacíos:** si un archivo de datos todavía no existe, la vista dice qué falta en una frase («Todavía no hay corridas de asistentes») y no muestra gráficas falsas.
- **Acceso:** mientras se valida la sesión se ve «Verificando acceso…». Sin sesión, la plataforma lleva al inicio de sesión de Cognito. En modo local (sin configuración de Cognito) aparece una banda gris arriba: «Modo local: acceso sin cuenta».
- «Cómo se hizo» y las descargas viven en la página pública; la plataforma los enlaza desde el pie de la barra.

**Sección tipo**
```
          Título centrado (H2, 700)
             ■─────▰─────●            ← acento (§4)
   Entrada centrada, máx. ~62 caracteres
   Nota pequeña con lo que piden las bases (gris)

   [contenido alineado a la izquierda, en rejilla]
```
- Espacio vertical: 104 px por sección en escritorio, 72 px en teléfono.
- Ancho de contenido: 1200 px; la portada usa 1320 px.
- Las secciones alternan blanco y `banda`. El único bloque oscuro es el pie (`noche`), donde el motivo se ve como en la convocatoria.

**Portada** (fondo blanco)
- Columna de texto (≤ 540 px, para que el H1 quepa en dos o tres líneas): H1 «Radar de Atención Turística de Puebla», el acento, la entrada, dos botones («Entrar a la plataforma» y «Cómo funciona») y una nota con el evento.
- Columna del mapa:
  - el contorno del estado con los municipios en `linea`;
  - los 12 Pueblos Mágicos y la capital como puntos en su posición real;
  - cada punto tiene dos capas: un relleno con su ocupación (escala de desempeño) y un anillo con su atención (escala de atención).

**Paneles**
- Bordes rectos o con radio de 0 a 2 px y un borde de 1 px en `linea`.
- Las tarjetas no llevan sombra. La única sombra está en la lista desplegable del encabezado.

---

## 6. Componentes

| Componente | Especificación |
|---|---|
| Botón primario | Fondo `tc-azul`, texto blanco, peso 700, alto mínimo 44 px, radio 3 px |
| Botón secundario | Transparente, con borde de 1.5 px en `tinta` |
| Alterna (filtros: idioma, proveedor, periodo) | Grupo de botones unidos con borde de 1 px. El activo va en `tinta` con texto blanco. Sin forma de píldora |
| Tabla | Encabezado sticky con línea inferior de 1.5 px en tinta. Filas de 8 px de relleno con línea `linea`. La fila elegida lleva fondo `#EAF1FE` y una barra de 3 px en `sel` a la izquierda |
| Ficha de destino | Panel blanco con borde fino. Contiene: nombre, zona, cuadrante rotulado, cifras grandes (ocupación de 12 meses y visibilidad en asistentes), componentes de atención como barras con su marca de origen (§4), fricciones principales, fuentes que citan los asistentes, minimapa y acciones («Descargar ficha», «Ver en el mapa») |
| Barra de visibilidad | Barra horizontal con el porcentaje y una línea con el intervalo de 95 %. Muestra n y k al pasar el ratón o al tocar |
| Gráfica de cuadrantes | Dispersión: atención (x) frente a desempeño (y), con líneas en las medianas y cada destino rotulado |
| Tooltip | Fondo `tinta`, texto blanco de 13.5 px, sin radio. Solo aparece con ratón; en pantallas táctiles el toque selecciona |
| Aviso de error | Fondo blanco con borde izquierdo de 4 px en `#B91C1C`. Dice qué falló y qué hacer |
| Verificación de datos | En el pie: «Datos verificados: n de n archivos coinciden con su huella». Al desplegarlo se ve cada archivo con su SHA-256 abreviada |

---

## 7. Movimiento (anime.js 4)

| Animación | Cómo |
|---|---|
| Mapa de la portada | Al cargar, los puntos aparecen de oeste a este. El relleno sube hasta su ocupación y el anillo se traza hasta su atención (`svg.createDrawable`). Es la única coreografía |
| Cuadrantes | Ligada al scroll: los destinos se desplazan de su posición por atención a su posición por desempeño, para mostrar la brecha. Es reversible |
| Visibilidad por idioma | Al cambiar de idioma, las barras se reacomodan en 0.45 s |
| Cambio de figura en «Cómo se hizo» | Fundido de 0.45 s por CSS |

**Reglas**
- Toda animación ligada al scroll debe ser reversible: al subir, se deshace.
- Los observadores de scroll se vuelven a medir si cambia el alto de la página.
- Con `prefers-reduced-motion` no hay animaciones: las figuras se muestran en su estado final.

---

## 8. Gráficas y mapas (d3 7)

**Unidades**
- Las figuras de «Cómo se hizo» se dibujan en 800 × 600 en escritorio y con 400 de ancho en teléfono, con un alto propio por escena. Nunca se encoge una figura de escritorio para el teléfono.
- Las gráficas pequeñas se dibujan con el ancho real del contenedor (`ResizeObserver`).

**Mapas**
- Proyección cónica conforme de Lambert con los parámetros de INEGI: `d3.geoConicConformal().parallels([17.5, 29.5]).rotate([102, 0])`, ajustada con `fitExtent` al estado.
- Geometrías de `data/referencia/geo/` (Marco Geoestadístico de INEGI de diciembre de 2025, simplificado al 4 %).
- La escala gráfica va en kilómetros.
- El zoom de los botones se centra en el destino elegido.
- Cada mapa cita su fuente: «Límites: INEGI, Marco Geoestadístico 2025».

**Etiquetas**
- Llevan halo blanco (`paint-order: stroke`) cuando cruzan líneas o puntos.
- Los textos centrados se recorren para no salirse del lienzo.

**Ejes**
- Sin línea de dominio, rejilla `#E8EBEF`, texto gris de 12.5 px.
- Los rótulos dicen la unidad y la dirección: «más a la derecha, más atención».

**Leyendas**
- Siempre presentes, salvo en la gráfica de cuadrantes, que rotula directamente.
- Medido y derivado se distinguen por relleno o trama.

**Selección compartida.** En la plataforma, elegir un destino en cualquier lugar actualiza el mapa, la tabla, la gráfica de cuadrantes, el panel de ficha y la vista de asistentes, y cambia la ruta a `#radar/<destino_id>`. Se hace con `seleccionar(destinoId, origen)` en `web/src/scripts/comun.js`.

---

## 9. Teléfono (≤ 760 px; una columna desde 1080 px)

- **Encabezado de la página pública:** el texto «3 de 6» se oculta por debajo de 420 px.
- **Barra de la plataforma:** las vistas se vuelven desplazables en horizontal; el correo se oculta y queda «Salir».
- **Panel de ficha:** ocupa toda la pantalla, con «Cerrar» arriba.
- **Portada:** el mapa pasa debajo del texto con todo el ancho; los botones ocupan todo el ancho.
- **Tabla del radar:** se ocultan las columnas de componentes y queda el índice; al tocar una fila se abre la ficha.
- **Asistentes:** las alternas de idioma se vuelven desplazables en horizontal, sin salto de línea.
- **Cuadrantes:** las etiquetas solo se muestran para el destino elegido y los extremos.

---

## 10. Escritura

- Español de México, voz activa, frases cortas. Se usa coma de miles y punto decimal, por ejemplo «41.3 %».
- **Botones:** dicen lo que hacen. Por ejemplo: «Ver la ficha de Cuetzalan», «Descargar CSV», «Comparar idiomas».
- **Las bases se citan aparte**, en una nota pequeña bajo la entrada: «La convocatoria pide…».
- **Solo se afirma lo que sostiene la evidencia.** Si algo no está probado, se dice: «sin evidencia suficiente», «correlación, no causa», «muestra pequeña y no aleatoria».
- **Errores:** explican qué pasó y qué hacer, sin disculparse.
- **No se usan:** flechas «→» al final de los enlaces, emojis, ni etiquetas del tipo «PALABRA — fragmento».

---

## 11. Datos en la página

- Todo dato visible sale de `web/public/datos/*.json`, que genera `uv run radar exportar` y que se valida contra `contracts/`.
- El navegador comprueba la SHA-256 de cada archivo contra `manifiesto.json` antes de usarlo. El pie muestra el resultado por archivo.
- Las descargas son copias exactas de `data/curado/`.

---

## 12. Lista de revisión antes de publicar

- [ ] Los encabezados están en negritas: el reset de Tailwind no los dejó en 400.
- [ ] No hay desborde horizontal a 390 px y las etiquetas de los SVG no se salen.
- [ ] El texto de los SVG mide al menos 12 px reales en teléfono.
- [ ] Las animaciones de scroll se deshacen al subir; con movimiento reducido todo queda en su estado final.
- [ ] Medido y derivado se distinguen sin color.
- [ ] El sitio no menciona herramientas de construcción. Comprobar con `grep -riE "hecho con|generado (por|con)|copilot|claude|opus" web/src`; los nombres de los asistentes estudiados aparecen solo en la sección de asistentes.
- [ ] El manifiesto coincide: 100 % de los archivos verificados.
- [ ] La plataforma no muestra contenido sin sesión, salvo en modo local, y el despliegue no se hizo en modo local.
- [ ] Contraste revisado: texto ≥ 4.5 : 1; puntos y líneas ≥ 3 : 1; rellenos claros con borde.
- [ ] Capturas a 1440×900, 1280×720 y 390×844 revisadas a ojo.

---

## 13. Archivos de referencia

| Qué | Dónde |
|---|---|
| Tokens y estilos | `web/src/styles/global.css` |
| Secciones de la página pública | `web/src/components/*.astro` y `web/src/secciones.ts` |
| Plataforma | `web/src/pages/plataforma/index.astro`, `web/src/components/plataforma/` y `web/src/scripts/plataforma.js` |
| Acceso | `web/src/scripts/acceso.js` |
| Selección compartida, formato y colores en JS | `web/src/scripts/comun.js` |
| Mapa | `web/src/scripts/mapa.js` |
| Figuras de «Cómo se hizo» | `web/src/scripts/escenas.js` |
| Referencias visuales | Banda de formas al pie de la convocatoria, colores del logotipo de Tech Capital y organización tipográfica del sitio de AWS UG Puebla |
