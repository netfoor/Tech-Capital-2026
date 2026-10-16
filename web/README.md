# Sitio

Sitio estático del radar (spec 009). Lo visual se rige por [`docs/diseno.md`](../docs/diseno.md) y los datos por [`contracts/`](../contracts/).

```bash
npm ci            # dependencias exactas de package-lock.json
npm run dev       # servidor local en http://localhost:4321
npm run build     # compila en dist/
npm run preview   # sirve dist/ para revisarlo
```

Requisito: Node.js ≥ 22.22.

## Organización

```
src/
├── secciones.ts        Orden, títulos, entradas y notas de las 9 secciones
├── styles/global.css   Tokens de color y tipografía (@theme) y reglas base
├── layouts/Base.astro
├── components/
│   ├── Encabezado.astro   Botón «n de 9», lista de secciones y riel de avance
│   ├── Acento.astro       Motivo de las tres formas bajo cada título
│   ├── Seccion.astro      Título, acento, entrada y nota de las bases
│   ├── Inicio.astro … DatosYCodigo.astro   Una por sección
│   └── Pie.astro          Banda del motivo y verificación de datos
└── scripts/
    └── comun.js           Escalas de color, formatos y selección compartida
public/
├── datos/              Paquete de datos: lo escribe `make exportar` (no se edita a mano)
└── descargas/          Copias exactas de data/curado/: también las escribe `make exportar`
```

Cada sección tiene su propio componente para que se pueda trabajar en paralelo sin conflictos. Los scripts de cada vista (`datos.js`, `mapa.js`, `radar.js`, `ficha.js`, `asistentes.js` y `escenas.js`) se agregan con sus tareas de la spec 009.

## Reglas

- Sin recursos externos: ni CDN, ni fuentes descargadas, ni llamadas a otros dominios. El sitio debe funcionar sin conexión.
- Sin scripts ni estilos en línea (`assetsInlineLimit: 0` y `inlineStylesheets: 'never'`), para que la política de contenido de CloudFront pueda ser solo `'self'`.
- Ninguna cifra escrita en los `.astro`: todo dato sale de `public/datos/`.
- Antes de desplegar se revisa la lista de `docs/diseno.md` §12.
