# Tareas 009 · Sitio: página pública y plataforma

## Base

- [x] T009-01 Andamiaje de Astro con Tailwind 4, tokens de `docs/diseno.md`, layout, encabezado con riel y secciones vacías. Verificación: `npm run build` en `web/`.
- [x] T009-15 Página pública de 6 secciones y plataforma con barra, cuatro vistas vacías, rutas por fragmento, panel de ficha y acceso con Cognito Hosted UI (PKCE) o modo local (ADR-0009). Verificación: `npm run build`; en modo local `/plataforma/#fichas` muestra la vista Fichas.
- [ ] T009-02 `radar exportar` con `destinos.json`, `geo/*`, `radar.json` parcial (desempeño), descargas y manifiesto; validación contra `contracts/`. Verificación: `uv run radar exportar --validar` pasa, se agrega a `make verificar` y `web/public/datos/manifiesto.json` existe.
- [ ] T009-03 `datos.js` con verificación SHA-256 y el bloque de verificación en el pie de la página pública y en la barra de la plataforma. Verificación: alterar un byte de un JSON local muestra el aviso y oculta el bloque.
- [ ] T009-04 Mapa de portada (proyección INEGI, puntos con relleno de ocupación) y su animación única de carga. Verificación: capturas a 1440 y 390.
- [ ] T009-05 **Primer despliegue** con desempeño, mapa y acceso con Cognito. Depende de T010-04 y T010-08. Verificación: URL pública con HTTPS; `/plataforma/` pide iniciar sesión y entra con una cuenta de prueba.

## Plataforma

- [ ] T009-06 Vista Radar: mapa por brecha, tabla y gráfica de cuadrantes con selección compartida y ruta `#radar/<destino_id>`. Depende de T008-05. Verificación: elegir un destino en cualquier vista lo marca en las tres y abre el panel.
- [ ] T009-07 Panel de ficha y vista Fichas (`fichas/<id>.json`) con impresión de una hoja. Verificación: impresión a PDF de Cuetzalan en una sola hoja carta.
- [ ] T009-08 Vista Asistentes con alternas de idioma y proveedor, barras con intervalo y dominios citados. Depende de T006-10. Verificación: los 5 idiomas seleccionables.
- [ ] T009-09 Vista Redes: presencia en el panel y en YouTube; opinión agregada si existe. Depende de T005-08 (y de T004-05 y T007-06 en P1). Verificación: datos visibles con n e intervalo.

## Página pública y cierre

- [ ] T009-10 [P] Secciones El problema, Para el Tianguis 2027 y Cómo se hizo, con datos de `evidencia.json` y `metodo.json`. Verificación: ninguna cifra escrita a mano (`grep` de dígitos en los `.astro` revisado).
- [ ] T009-11 [P] Datos y código: descargas y manifiesto legible. Verificación: cada descarga coincide en SHA-256 con su archivo de `data/curado/`.
- [ ] T009-14 Sección «La plataforma» con capturas reales de las cuatro vistas (`public/capturas/`), tomadas con `scripts/revisar.mjs`. Depende de T009-06 a T009-09. Verificación: cuatro imágenes con texto alternativo.
- [ ] T009-12 Revisión en teléfono y accesibilidad; lista de `docs/diseno.md` §12 completa. Verificación: `node scripts/revisar.mjs` sin fallas y casillas marcadas.
- [ ] T009-13 (P1) Prueba sin conexión: servir `web/dist/` compilado en modo local sin internet. Verificación: página pública y plataforma funcionan completas.
