# Plan 009 · Sitio: página pública y plataforma

## Estructura de `web/`

```
web/
├── astro.config.mjs              salida estática, Tailwind 4 vía @tailwindcss/vite, sin scripts en línea
├── .env.example                  PUBLIC_COGNITO_DOMINIO y PUBLIC_COGNITO_CLIENTE_ID (públicos, no son llaves)
├── public/
│   ├── datos/                    generado por `radar exportar` (no se edita a mano)
│   │   ├── manifiesto.json, destinos.json, radar.json, evidencia.json
│   │   ├── asistentes.json, redes.json, metodo.json
│   │   ├── fichas/<destino_id>.json
│   │   └── geo/municipios.json, estado.json
│   ├── descargas/                copias exactas de data/curado/*.csv
│   └── capturas/                 imágenes de las vistas para la sección «La plataforma» (T009-14)
└── src/
    ├── secciones.ts              orden y textos de las 6 secciones de la página pública
    ├── vistas.ts                 orden y textos de las 4 vistas de la plataforma
    ├── styles/global.css         tokens (@theme) y reglas base
    ├── layouts/Base.astro
    ├── pages/
    │   ├── index.astro           página pública
    │   ├── plataforma/index.astro
    │   └── 404.astro
    ├── components/
    │   ├── Encabezado.astro      botón «n de 6», «Entrar a la plataforma» y riel
    │   ├── Acento.astro, Seccion.astro, Pie.astro
    │   ├── Inicio.astro … DatosYCodigo.astro      una por sección pública
    │   └── plataforma/
    │       ├── Barra.astro       vistas, correo y «Salir»
    │       ├── VistaRadar.astro, VistaFichas.astro, VistaAsistentes.astro, VistaRedes.astro
    │       └── PanelFicha.astro
    └── scripts/
        ├── acceso.js             Cognito Hosted UI con PKCE y modo local
        ├── plataforma.js         guardia de sesión, rutas por fragmento y panel de ficha
        ├── comun.js              seleccionar(), formatos y escalas de color
        ├── datos.js              carga con verificación SHA-256 (T009-03)
        ├── mapa.js, radar.js, ficha.js, asistentes.js, escenas.js   (tareas de esta spec)
```

## Acceso (`acceso.js`)

1. `iniciarSesion()`: genera `code_verifier` (32 bytes aleatorios en base64url) y `state`, los guarda en `sessionStorage` y redirige a `https://<dominio>/oauth2/authorize` con `response_type=code`, `client_id`, `redirect_uri=<origen>/plataforma/`, `scope=openid email profile`, `code_challenge` (SHA-256 en base64url) y `code_challenge_method=S256`.
2. Al volver con `?code&state`: comprueba `state`, hace `POST https://<dominio>/oauth2/token` (`grant_type=authorization_code`, `client_id`, `code`, `redirect_uri`, `code_verifier`), guarda el `id_token` y su `exp`, y limpia la URL con `history.replaceState`.
3. `sesion()`: devuelve `{correo, exp}` si hay token vigente; si no, `null`.
4. `cerrarSesion()`: borra `sessionStorage` y redirige a `https://<dominio>/logout?client_id=…&logout_uri=<origen>/`.
5. El token solo decide qué se muestra. Los datos son públicos por diseño (ADR-0009); no se envía a ningún otro servicio.

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

1. Base: tokens, página pública con 6 secciones, plataforma con barra, cuatro vistas vacías, panel de ficha y acceso con modo local. Ya está el andamiaje.
2. Exportador con `destinos.json`, `geo/*` y desempeño (`radar.json` parcial) → mapa de portada y mapa de la vista Radar → **primer despliegue con Cognito** (FR-009-08).
3. Radar completo: tabla, cuadrantes, brecha y panel de ficha.
4. Fichas e impresión.
5. Asistentes.
6. Redes (panel y YouTube).
7. Página pública: el problema, la plataforma con capturas, Tianguis, Cómo se hizo, y Datos y código.
8. Revisión en teléfono y lista de verificación de `docs/diseno.md` §12.

## Pruebas

- `npm run build` sin errores ni advertencias de tipos.
- `scripts/revisar.mjs` (Playwright con Chromium preinstalado): abre `/` y `/plataforma/` (modo local) a 1440×900, 1280×720 y 390×844; toma capturas; comprueba que no hay desborde horizontal ni errores en la consola, que el pie dice «n de n» y que las cuatro rutas de la plataforma muestran su vista.
- Prueba manual de acceso con una cuenta de prueba: entrar, recargar (la sesión sigue), abrir `#radar/cuetzalan` directo y salir.
- `grep` de palabras prohibidas según `docs/diseno.md` §12.
