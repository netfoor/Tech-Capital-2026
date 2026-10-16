# Tareas 016 · PWA del visitante

Formato: `[ ]` pendiente, `[~]` en curso, `[x]` hecha. `[P]` = paralelizable con otras tareas de esta spec.

## Base

- [x] T016-01 Spec, plan, tareas y `docs/diseno.md` con tokens, tipografía, espaciado y componentes. Verificación: documentos en el repositorio.
- [x] T016-02 Tipos del contrato, cliente tipado y modo de demostración con banda sintética. Verificación: sin API, la app muestra la banda y los POI de ejemplo.
- [x] T016-03 [P] Tokens CSS, estilos base, `lang="es-MX"`, cadenas en `src/i18n/es.ts` y modo de lenguaje claro. Verificación: `tokens.test.ts` (contraste AA).
- [x] T016-04 [P] Almacén local con `try/catch` para guardados, etiquetas, notas, planes y preferencias. Verificación: `guardados.test.tsx`.

## Flujos P0

- [x] T016-05 Descubrir: lista, mapa equivalente con atribución y filtros en la URL. Verificación: `filtros.test.tsx`.
- [x] T016-06 Ficha de POI con accesibilidad por atributo, barreras, fuentes, guardar y reportar. Verificación: `ficha.test.tsx`.
- [x] T016-07 Mi mapa agrupado por destino, con etiquetas, nota, lista y mapa. Verificación: `guardados.test.tsx`.
- [x] T016-08 Planear desde cero y desde mis guardados; itinerario editable y guardable. Verificación: `motor.test.ts` y prueba de la página.
- [x] T016-09 [P] Reportar barrera y reseña por dimensiones. Verificación: `formularios.test.tsx`.
- [x] T016-10 [P] Pantalla «Mi recorrido» con aviso honesto (spec 017). Verificación: enlace en la navegación.

## PWA y calidad

- [x] T016-11 `vite-plugin-pwa` con manifest, iconos locales y caché del shell y de POI. Verificación: `npm run build` genera `sw.js` y `manifest.webmanifest`.
- [x] T016-12 axe sin violaciones en los componentes P0 y revisión a 390 px. Verificación: `axe.test.tsx` y capturas.

## Integración (después de la spec 014)

- [ ] T016-13 Probar contra la API real y retirar diferencias del contrato. Verificación: flujos P0 sin banda sintética con datos reales.
- [ ] T016-14 Prueba manual con lector de pantalla (NVDA o TalkBack) de los flujos P0, documentada en `docs/accesibilidad.md` (spec 020).
