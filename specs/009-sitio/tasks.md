# Tareas 009 · Sitio

## Base

- [x] T009-01 Andamiaje de Astro con Tailwind 4, tokens de `docs/diseno.md`, `secciones.ts`, layout, encabezado con riel y secciones vacías. Verificación: `npm run build` en `web/`.
- [ ] T009-02 `radar exportar` con `destinos.json`, `geo/*`, `radar.json` parcial (desempeño), descargas y manifiesto; validación contra `contracts/`. Depende de T010-* solo para desplegar. Verificación: `uv run radar exportar --validar` pasa, se agrega a `make verificar` y `web/public/datos/manifiesto.json` existe.
- [ ] T009-03 `datos.js` con verificación SHA-256 y el bloque de verificación en el pie. Verificación: alterar un byte de un JSON local muestra el aviso y oculta el bloque.
- [ ] T009-04 Mapa de portada (proyección INEGI, puntos con relleno de ocupación) y su animación única de carga. Verificación: capturas a 1440 y 390.
- [ ] T009-05 **Primer despliegue** con desempeño y mapa. Depende de T010-04. Verificación: URL pública con HTTPS.

## Radar y fichas

- [ ] T009-06 Sección Radar: mapa por brecha, tabla y gráfica de cuadrantes con selección compartida. Depende de T008-05. Verificación: elegir un destino en cualquier vista lo marca en las tres.
- [ ] T009-07 Fichas por destino (`fichas/<id>.json`) con impresión de una página. Verificación: impresión a PDF de Cuetzalan en una sola hoja carta.

## Asistentes y redes

- [ ] T009-08 Sección de asistentes con alternas de idioma y proveedor, barras con intervalo y dominios citados. Depende de T006-10. Verificación: los 5 idiomas seleccionables.
- [ ] T009-09 Sección de redes: presencia en el panel y en YouTube; opinión agregada si existe. Depende de T005-08 (y de T004-05 y T007-06 en P1). Verificación: datos visibles con n e intervalo.

## Contenido y cierre

- [ ] T009-10 [P] Secciones El problema, Para el Tianguis 2027 y Cómo se hizo, con datos de `evidencia.json` y `metodo.json`. Verificación: ninguna cifra escrita a mano (`grep` de dígitos en los `.astro` revisado).
- [ ] T009-11 [P] Datos y código: descargas y manifiesto legible. Verificación: cada descarga coincide en SHA-256 con su archivo de `data/curado/`.
- [ ] T009-12 Revisión en teléfono y accesibilidad; lista de `docs/diseno.md` §12 completa. Verificación: `node scripts/revisar.mjs` sin fallas y casillas marcadas.
- [ ] T009-13 (P1) Prueba sin conexión: servir `web/dist/` sin internet. Verificación: el sitio funciona completo.
