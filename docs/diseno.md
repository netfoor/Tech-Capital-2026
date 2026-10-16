# Sistema visual de Puebla Viva 360

Este documento fija cómo se ve y cómo se comporta la PWA del visitante. Toda pantalla nueva usa estos tokens y componentes. Los tokens viven en `frontend/src/estilos/tokens.css`; la prueba `frontend/src/estilos/tokens.test.ts` comprueba el contraste de los pares de color de esta página.

## 1. Principios

1. **Cálida y clara.** Inspirada en Puebla: el azul de la talavera, el barro de los ladrillos y el papel crema. Superficies limpias, sin ruido.
2. **La lista manda.** Cada vista con lugares se puede usar completa sin el mapa.
3. **Honestidad visible.** Lo que no sabemos se dice («Sin verificar»). Lo sintético se rotula. Un estado nunca depende solo del color.
4. **Pocas cosas a la vez.** Un objetivo principal por pantalla. El modo de lenguaje claro reduce aún más la densidad.
5. **Sin dependencias externas.** Tipografía del sistema, íconos dibujados en SVG dentro del código. Lo único externo son los mosaicos del mapa.

## 2. Color

Todos los pares de texto cumplen AA (4.5:1 o más); los bordes de controles cumplen 3:1 contra su fondo.

| Token | Valor | Uso |
|---|---|---|
| `--color-fondo` | `#FAF6EF` | Fondo de la página (papel crema) |
| `--color-superficie` | `#FFFFFF` | Tarjetas, formularios, paneles |
| `--color-superficie-alta` | `#F3ECE1` | Bloques destacados, filtros |
| `--color-texto` | `#1C2230` | Texto principal |
| `--color-texto-suave` | `#4B5263` | Metadatos, ayudas |
| `--color-borde` | `#E4D9C8` | Separadores decorativos (no delimitan controles) |
| `--color-borde-control` | `#7D7262` | Borde de campos, casillas y botones secundarios |
| `--color-primario` | `#1F4E8C` | Azul talavera: acciones principales, enlaces, foco |
| `--color-primario-fuerte` | `#173D6E` | Hover y estado presionado |
| `--color-primario-suave` | `#E6EEF8` | Fondo de elementos activos |
| `--color-acento` | `#A8431E` | Barro: acentos, «Guardar en mi mapa» |
| `--color-acento-suave` | `#FBEADF` | Fondo de etiquetas propias |
| `--color-verificado` / `-fondo` | `#1F6E43` / `#E3F2E8` | Estado verificado |
| `--color-sin-verificar` / `-fondo` | `#7A4F00` / `#FFF3D4` | Estado sin verificar |
| `--color-reportado` / `-fondo` | `#A52A1E` / `#FCE8E5` | Estado reportado y errores |
| `--color-moderacion` / `-fondo` | `#5A3D8F` / `#EEE8F8` | Estado en moderación |
| `--color-sintetico` | `#FFD25E` | Banda «DATOS SINTÉTICOS DE DEMOSTRACIÓN» (texto `--color-texto`) |

Pares comprobados: texto y texto suave sobre fondo, superficie y superficie alta; primario sobre superficie y fondo; blanco sobre primario y sobre acento; cada estado sobre su fondo; texto sobre la banda sintética; borde de control sobre superficie y fondo (3:1).

## 3. Tipografía

- Texto: `system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`.
- Títulos: `"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif`, que da calidez sin descargar fuentes.
- Tamaño base 1 rem (16 px), interlineado 1.55. Nunca menos de 0.875 rem.
- Escala: `--texto-xs` 0.875 · `--texto-s` 0.9375 · `--texto-m` 1 · `--texto-l` 1.25 · `--texto-xl` 1.5 · `--texto-2xl` 2 rem.
- Todo en rem: el texto escala con la configuración del navegador hasta 200 % sin perder contenido.
- Lenguaje claro: base 1.125 rem e interlineado 1.7.

## 4. Espaciado, forma y elevación

- Escala de 4 px: `--esp-1` 0.25 · `--esp-2` 0.5 · `--esp-3` 0.75 · `--esp-4` 1 · `--esp-5` 1.5 · `--esp-6` 2 · `--esp-7` 3 rem.
- Radios: `--radio-s` 8 px (controles), `--radio-m` 14 px (tarjetas), `--radio-pastilla` 999 px (etiquetas y chips).
- Sombras: `--sombra-1` para tarjetas y `--sombra-2` para paneles flotantes. Suaves y cálidas (tinte café).
- Ancho máximo de contenido: 72 rem. Margen lateral: 1 rem en móvil.

## 5. Movimiento

- Transiciones de 150 ms en color y sombra. Nada se mueve solo.
- Con `prefers-reduced-motion: reduce` se eliminan transiciones, animaciones y el vuelo del mapa.

## 6. Componentes

| Componente | Reglas |
|---|---|
| **Botón** | Altura mínima 44 px (mínimo absoluto 24 px). Variantes: principal (azul, texto blanco), secundario (borde de control, fondo superficie), acento (barro) y discreto (solo texto subrayado al pasar). Siempre con texto; un ícono solo lleva `aria-label`. |
| **Campo** | Etiqueta visible arriba; ayuda debajo con `aria-describedby`; error en rojo con ícono «!», texto que explica qué hacer y `aria-invalid`. Al enviar con errores, el foco va al primer campo con error y se muestra un resumen. |
| **Casilla y chip de filtro** | Casilla nativa de 24 px con etiqueta clicable completa. Los chips de interés son botones con `aria-pressed`. |
| **Tarjeta de lugar** | Nombre (enlace a la ficha), categoría y destino, costo, cobertura de accesibilidad con ícono y texto, etiqueta sintética si aplica y botón «Guardar». Toda la información también está en la ficha. |
| **Estado de atributo** | Pastilla con ícono + texto: ✓ Verificado · ? Sin verificar · ! Reportado · reloj En moderación. El color refuerza, no informa por sí solo. |
| **Banda sintética** | Franja fija arriba, fondo `--color-sintetico` con rayas diagonales, texto en mayúsculas «DATOS SINTÉTICOS DE DEMOSTRACIÓN» y explicación breve. `role="note"`. |
| **Aviso** | Caja con borde izquierdo de color de estado, ícono y texto. Los avisos dinámicos usan `role="status"`. |
| **Mapa** | Siempre acompañado de su lista. Atribución «© OpenStreetMap contributors» visible bajo el mapa. Marcadores como botones con nombre accesible. Si no carga, aviso y enlace a la lista. |
| **Calificación 1–5** | Grupo de radios nativos con `fieldset` y `legend`; cada opción dice su número y significado («1, muy malo» … «5, excelente»). |
| **Navegación** | Barra superior con marca y, en móvil, barra inferior fija con 5 destinos: Descubrir, Mi mapa, Planear, Mi recorrido y Ajustes de lectura. La página actual lleva `aria-current="page"`. |

## 7. Íconos

Dibujados en SVG dentro de `frontend/src/componentes/Icono.tsx`, trazo de 2 px, 24 px de caja. Decorativos con `aria-hidden="true"` cuando hay texto al lado.

## 8. Voz y tono

Español de México, segunda persona («tú»), frases cortas y voz activa. Decimos lo que sabemos y lo que no: «No sabemos si tiene rampa» en lugar de omitirlo. Nunca «accesible» sin verificación. La interfaz no menciona las herramientas con que se construyó.

## 9. Lista de revisión antes de cerrar una pantalla

- [ ] Funciona solo con teclado y el foco se ve en todo momento.
- [ ] Tiene un `h1`, landmarks (`header`, `nav`, `main`, `footer`) y orden de títulos sin saltos.
- [ ] A 390 px de ancho no hay scroll horizontal.
- [ ] Ningún estado depende solo del color.
- [ ] Los objetivos táctiles miden 24×24 px o más (44 px en acciones principales).
- [ ] Las cadenas salen de `src/i18n/es.ts`.
- [ ] Si usa datos sintéticos, se ve la banda.
- [ ] axe sin violaciones en su prueba.
