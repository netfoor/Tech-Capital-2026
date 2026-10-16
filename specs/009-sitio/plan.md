# Plan 009 · Sitio

## Estructura de `web/`

```
web/
├── astro.config.mjs          salida estática, Tailwind 4 vía @tailwindcss/vite
├── package.json
├── public/
│   ├── datos/                generado por `radar exportar` (no se edita a mano)
│   │   ├── manifiesto.json
│   │   ├── destinos.json
│   │   ├── radar.json
│   │   ├── evidencia.json
│   │   ├── asistentes.json
│   │   ├── redes.json
│   │   ├── metodo.json
│   │   ├── fichas/<destino_id>.json
│   │   └── geo/municipios.json, estado.json
│   └── descargas/            copias exactas de data/curado/*.csv
└── src/
    ├── secciones.ts          orden y títulos de las 9 secciones
    ├── styles/global.css     tokens (@theme) y reglas base
    ├── layouts/Base.astro
    ├── components/
    │   ├── Encabezado.astro  logos, botón «n de 9» y riel
    │   ├── Acento.astro      motivo ■▰● bajo cada H2
    │   ├── Seccion.astro     título, acento, entrada y nota de bases
    │   ├── Inicio.astro … DatosYCodigo.astro   una por sección
    │   └── Pie.astro         verificación de datos y banda del motivo
    └── scripts/
        ├── datos.js          carga con verificación SHA-256
        ├── comun.js          seleccionar(), formatos y escalas de color
        ├── mapa.js           proyección INEGI, mapa de portada y de brecha
        ├── radar.js          tabla y gráfica de cuadrantes
        ├── asistentes.js     barras con intervalo, alternas y dominios
        ├── ficha.js          ficha e impresión
        └── escenas.js        figuras de «Cómo se hizo»
```

## Exportador (`radar exportar`)

`pipelines/src/radar/exportar/`:
1. Lee `data/curado/` y `data/referencia/`.
2. Arma los JSON de los contratos. Los nombres de campos y las unidades vienen de `contracts/*.schema.json`.
3. Valida con `jsonschema` (Draft 2020-12). Si algún archivo falla, no se escribe ninguno.
4. Copia las descargas y la geometría (redondeada a 4 decimales).
5. Escribe `manifiesto.json`: `{generado, commit, archivos: [{ruta, sha256, bytes, fuentes}]}`.

`radar exportar --validar` solo valida, sin escribir. Lo usa `make verificar`.

## Verificación en el navegador (`datos.js`)

```js
const manifiesto = await (await fetch('/datos/manifiesto.json')).json();
export async function cargar(ruta) {
  const entrada = manifiesto.archivos.find(a => a.ruta === ruta);
  const buf = await (await fetch(`/datos/${ruta}`)).arrayBuffer();
  const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', buf))]
    .map(b => b.toString(16).padStart(2, '0')).join('');
  registrarVerificacion(ruta, hash === entrada?.sha256);
  if (hash !== entrada?.sha256) throw new Error(`La huella de ${ruta} no coincide`);
  return JSON.parse(new TextDecoder().decode(buf));
}
```

## Orden de construcción

1. Base: tokens, layout, encabezado con riel, secciones vacías con título, acento y entrada. Ya está el andamiaje.
2. Exportador con `destinos.json`, `geo/*` y desempeño (`radar.json` parcial) → mapa de portada y de desempeño → **primer despliegue** (FR-009-08).
3. Radar completo: tabla, cuadrantes y brecha.
4. Fichas e impresión.
5. Asistentes.
6. Redes (panel y YouTube).
7. Cómo se hizo, y Datos y código.
8. Revisión en teléfono y lista de verificación de `docs/diseno.md` §12.

## Pruebas

- `npm run build` sin errores ni advertencias de tipos.
- `scripts/revisar.mjs` (Playwright con Chromium preinstalado): abre el sitio compilado a 1440×900, 1280×720 y 390×844; toma capturas; comprueba que no hay desborde horizontal ni errores en la consola y que el pie dice «n de n».
- `grep` de palabras prohibidas según `docs/diseno.md` §12.
