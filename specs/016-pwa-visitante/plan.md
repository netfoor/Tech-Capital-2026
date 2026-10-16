# Plan 016 · PWA del visitante

## Enfoque

Una sola aplicación Vite + React 19 + TypeScript con react-router 7. La lista es el componente principal de cada vista con lugares; el mapa (MapLibre con el estilo `liberty` de OpenFreeMap) recibe los mismos datos y se carga bajo demanda para no pesar en la primera visita. El sistema visual vive en `docs/diseno.md` y en tokens CSS propios, sin bibliotecas de componentes.

La API real la construye la spec 014 en paralelo. El cliente intenta la API y, si no responde, cambia a un modo de demostración con datos sintéticos rotulados y un motor local que aplica las mismas reglas de elegibilidad. Así la PWA se puede desarrollar, probar y demostrar sin backend, y al integrarse no cambia la interfaz.

## Archivos

| Archivo | Contenido |
|---|---|
| `frontend/src/api/tipos.ts` | Tipos del contrato (snake_case) |
| `frontend/src/api/cliente.ts` | Cliente tipado; cambio a demostración si la API no responde |
| `frontend/src/api/modo.ts` | Estado global del origen de datos (API o demostración) y de si se vieron datos sintéticos |
| `frontend/src/demo/datos.ts` | POI y destinos sintéticos (`is_synthetic: true`) |
| `frontend/src/demo/motor.ts` | Filtros y planes locales con las mismas restricciones indispensables |
| `frontend/src/dominio/` | Reglas puras: accesibilidad (cumple o no un atributo), tiempos, formato de horario |
| `frontend/src/almacen/` | `localStorage` con `try/catch`: guardados, etiquetas, notas, planes y preferencias |
| `frontend/src/i18n/es.ts` | Cadenas en español y su variante de lenguaje claro |
| `frontend/src/componentes/` | Piezas reutilizables: estado de atributo, tarjeta, filtros, mapa, banda sintética, calificación |
| `frontend/src/paginas/` | Descubrir, Ficha, MiMapa, Planear, Reportar, Reseña, MiRecorrido |
| `frontend/src/estilos/` | Tokens, base y componentes CSS |
| `frontend/public/iconos/` | Iconos de la PWA generados localmente desde un SVG propio |

## Reglas de accesibilidad física en la interfaz

- Un atributo «cumple» una necesidad solo si su valor es afirmativo y su estado no es «reportado». Con «solo verificados», además debe estar «verificado».
- Sin dato → estado «sin verificar» y texto «No tenemos este dato todavía».
- Cada estado tiene ícono, texto y color: verificado (✓), sin verificar (?), reportado (!), en moderación (reloj).

## Modo de demostración

- Se activa al primer fallo de red, 404 o 5xx de la API y se mantiene durante la sesión.
- La banda «DATOS SINTÉTICOS DE DEMOSTRACIÓN» se muestra arriba de cada pantalla mientras esté activo o cuando se haya mostrado un POI con `is_synthetic=true`.
- Reseñas y reportes se guardan solo en el dispositivo y se avisa.

## PWA

- `vite-plugin-pwa` 1.0.3 con `generateSW`: precarga del shell; `NetworkFirst` para `/api/pois` y `/api/destinos` con caché `poi-ultima` (30 entradas, 7 días); los mosaicos del mapa no se guardan.
- Manifest en español, `lang: es-MX`, colores del sistema visual e iconos 192, 512 y maskable.

## Pruebas

- Vitest + Testing Library + jest-axe.
- `filtros.test.tsx`: filtros de accesibilidad y «solo verificados».
- `ficha.test.tsx`: «Sin verificar» cuando falta el dato; nunca «accesible».
- `guardados.test.tsx`: guardar, etiquetas, nota y almacenamiento bloqueado.
- `formularios.test.tsx`: validación del reporte de barrera y de la reseña.
- `motor.test.ts`: cero violaciones de restricciones indispensables en el plan local.
- `axe.test.tsx`: sin violaciones en Descubrir, Ficha, Mi mapa, Planear, Reportar y Reseña.
- `tokens.test.ts`: contraste AA de los pares de color del sistema.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| La API de la spec 014 cambia el contrato | Tipos en un solo archivo; el modo de demostración permite seguir |
| El mapa no carga (sin WebGL o sin red) | La lista es la vista principal; el mapa muestra un aviso y remite a la lista |
| `localStorage` bloqueado | Todo acceso en `try/catch`; aviso visible |
| Contraste insuficiente | Prueba automática de los pares de tokens |
