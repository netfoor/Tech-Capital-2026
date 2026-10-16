# Sitio

Dos superficies sobre los mismos datos (spec 009, [ADR-0009](../docs/decisiones/0009-landing-publica-y-plataforma-con-cognito.md)):

- **Página pública** (`/`): el problema, qué hace la plataforma, su uso rumbo al Tianguis, el método y las descargas.
- **Plataforma** (`/plataforma/`): la herramienta, con las vistas Radar, Fichas, Asistentes y Redes. Pide iniciar sesión con Cognito.

Lo visual se rige por [`docs/diseno.md`](../docs/diseno.md) y los datos por [`contracts/`](../contracts/).

```bash
npm ci            # dependencias exactas de package-lock.json
npm run dev       # servidor local en http://localhost:4321
npm run build     # compila en dist/
npm run preview   # sirve dist/ para revisarlo
```

Requisito: Node.js ≥ 22.22.

## Acceso y modo local

La configuración pública de Cognito va en `web/.env` (plantilla: `.env.example`). La escribe `make web-config` desde la raíz con las salidas de Terraform. No son llaves: el dominio y el id de cliente son públicos.

- **Sin `web/.env`:** modo local. La plataforma entra sin cuenta y muestra una banda que lo dice. Sirve para desarrollar antes de aplicar la infraestructura.
- **Con `web/.env`:** `/plataforma/` lleva a la Hosted UI de Cognito y vuelve con la sesión. `http://localhost:4321/plataforma/` también está registrado como dirección de regreso.

`infra/desplegar.sh` no publica una compilación en modo local.

## Organización

```
src/
├── secciones.ts        Orden y textos de las 6 secciones de la página pública
├── vistas.ts           Orden y textos de las 4 vistas de la plataforma
├── styles/global.css   Tokens de color y tipografía (@theme) y reglas base
├── layouts/Base.astro
├── pages/
│   ├── index.astro             Página pública
│   ├── plataforma/index.astro  Plataforma
│   └── 404.astro
├── components/
│   ├── Encabezado.astro   Botón «n de 6», «Entrar a la plataforma» y riel de avance
│   ├── Acento.astro       Motivo de las tres formas bajo cada título
│   ├── Seccion.astro      Título, acento, entrada y nota de las bases
│   ├── Inicio.astro … DatosYCodigo.astro   Una por sección pública
│   ├── Pie.astro          Banda del motivo y verificación de datos
│   └── plataforma/
│       ├── Barra.astro          Vistas, correo de la sesión y «Salir»
│       ├── MarcoVista.astro     Título, filtros y estado vacío de cada vista
│       ├── VistaRadar.astro … VistaRedes.astro   Una por vista
│       └── PanelFicha.astro     Ficha del destino elegido
└── scripts/
    ├── acceso.js          Cognito Hosted UI con PKCE y modo local
    ├── plataforma.js      Guardia de sesión, rutas (#radar, #radar/<destino_id>…) y panel de ficha
    └── comun.js           Escalas de color, formatos y selección compartida
public/
├── datos/              Paquete de datos: lo escribe `make exportar` (no se edita a mano)
└── descargas/          Copias exactas de data/curado/: también las escribe `make exportar`
```

Cada sección y cada vista tiene su propio componente para que se pueda trabajar en paralelo sin conflictos. Los scripts de datos y gráficas (`datos.js`, `mapa.js`, `radar.js`, `ficha.js`, `asistentes.js` y `escenas.js`) se agregan con sus tareas de la spec 009.

## Reglas

- Sin recursos externos: ni CDN, ni fuentes descargadas, ni llamadas a otros dominios, salvo Cognito para el inicio de sesión.
- Sin scripts ni estilos en línea (`assetsInlineLimit: 0` y `inlineStylesheets: 'never'`), para que la política de contenido de CloudFront pueda ser `'self'` más el dominio de Cognito.
- Ninguna cifra escrita en los `.astro`: todo dato sale de `public/datos/`.
- Antes de desplegar se revisa la lista de `docs/diseno.md` §12.
