// Revisión del sitio compilado (docs/diseno.md §12). Uso:
//   node scripts/revisar.mjs               revisa web/dist y falla si algo no cumple
//   node scripts/revisar.mjs --capturas    además guarda las capturas de la plataforma en public/capturas/
import { createServer } from 'node:http';
import { readFileSync, existsSync, statSync, writeFileSync, readdirSync } from 'node:fs';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const RAIZ = fileURLToPath(new URL('..', import.meta.url));
const DIST = join(RAIZ, 'dist');
const TIPOS = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.csv': 'text/csv' };
const capturas = process.argv.includes('--capturas');
const fallas = [];
const falla = (m) => fallas.push(m);

function servir() {
  return new Promise((resolver) => {
    const s = createServer((req, res) => {
      let ruta = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname));
      let archivo = join(DIST, ruta);
      if (existsSync(archivo) && statSync(archivo).isDirectory()) archivo = join(archivo, 'index.html');
      if (!archivo.startsWith(DIST) || !existsSync(archivo)) {
        res.writeHead(404).end('no encontrado');
        return;
      }
      // Misma CSP que CloudFront (infra/sitio.tf) para detectar estilos en línea bloqueados.
      res.writeHead(200, {
        'content-type': TIPOS[extname(archivo)] ?? 'application/octet-stream',
        'content-security-policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'",
      }).end(readFileSync(archivo));
    });
    s.listen(0, '127.0.0.1', () => resolver({ s, url: `http://127.0.0.1:${s.address().port}` }));
  });
}

function recorrer(carpeta, salida = []) {
  for (const e of readdirSync(carpeta, { withFileTypes: true })) {
    const r = join(carpeta, e.name);
    if (e.isDirectory()) recorrer(r, salida);
    else if (/\.(astro|ts|js|css)$/.test(e.name)) salida.push(r);
  }
  return salida;
}

// 1. El sitio no menciona herramientas de construcción.
const prohibido = /hecho con|generado (por|con)|copilot|claude|opus/i;
for (const archivo of recorrer(join(RAIZ, 'src'))) {
  if (prohibido.test(readFileSync(archivo, 'utf8'))) falla(`Menciona herramientas de construcción: ${archivo.replace(RAIZ, '')}`);
}

const { s, url } = await servir();
const navegador = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
const VISTAS = [
  { ancho: 1440, alto: 900, nombre: '1440' },
  { ancho: 1280, alto: 720, nombre: '1280' },
  { ancho: 390, alto: 844, nombre: '390' },
];

for (const v of VISTAS) {
  for (const ruta of ['/', '/plataforma/']) {
    const contexto = await navegador.newContext({ viewport: { width: v.ancho, height: v.alto } });
    const p = await contexto.newPage();
    const errores = [];
    const externas = [];
    p.on('console', (m) => m.type() === 'error' && errores.push(m.text()));
    p.on('pageerror', (e) => errores.push(String(e)));
    p.on('request', (r) => {
      if (!r.url().startsWith(url) && !r.url().startsWith('data:')) externas.push(r.url());
    });
    await p.goto(url + ruta);
    if (ruta === '/') await p.waitForSelector('#mapa-portada .punto', { timeout: 15000 });
    else await p.waitForSelector('.punto-cuadrante', { timeout: 15000 });
    await p.waitForTimeout(1500);
    const donde = `${ruta} a ${v.ancho}px`;
    externas.forEach((u) => falla(`${ruta} a ${v.ancho}px: pide un recurso externo: ${u}`));
    errores.forEach((e) => falla(`${donde}: error de consola: ${e}`));

    const medidas = await p.evaluate(() => {
      const ancho = document.documentElement.clientWidth;
      const desborde = document.documentElement.scrollWidth > ancho + 1;
      const chicos = [];
      document.querySelectorAll('svg text').forEach((t) => {
        const svg = t.ownerSVGElement;
        const escala = svg && svg.viewBox?.baseVal?.width ? svg.getBoundingClientRect().width / svg.viewBox.baseVal.width : 1;
        const tam = parseFloat(getComputedStyle(t).fontSize) * escala;
        if (t.textContent.trim() && t.getBoundingClientRect().width > 0 && tam < 11.9) chicos.push(`${t.textContent.trim().slice(0, 20)} (${tam.toFixed(1)} px)`);
      });
      const encabezados = [...document.querySelectorAll('h1,h2,h3')].filter((h) => h.offsetParent && parseInt(getComputedStyle(h).fontWeight, 10) < 700).map((h) => h.textContent.trim().slice(0, 30));
      const verificacion = document.querySelector('#verificacion, #verificacion-barra')?.dataset.estado;
      const sinTexto = [...document.querySelectorAll('img')].filter((i) => !i.alt).length;
      return { desborde, chicos: [...new Set(chicos)], encabezados, verificacion, sinTexto };
    });
    if (medidas.desborde) falla(`${donde}: hay desborde horizontal`);
    if (v.ancho === 390 && medidas.chicos.length) falla(`${donde}: texto de SVG menor de 12 px: ${medidas.chicos.slice(0, 4).join(', ')}`);
    if (medidas.encabezados.length) falla(`${donde}: encabezados sin negritas: ${medidas.encabezados.join(', ')}`);
    if (medidas.verificacion !== 'ok') falla(`${donde}: la verificación de datos no está en «ok» (${medidas.verificacion})`);
    if (medidas.sinTexto) falla(`${donde}: ${medidas.sinTexto} imágenes sin texto alternativo`);

    if (capturas && ruta === '/plataforma/' && v.ancho === 1440) {
      for (const vista of ['radar', 'fichas', 'asistentes', 'redes']) {
        await p.evaluate((h) => { window.location.hash = h; }, vista === 'radar' ? 'radar/cuetzalan' : vista);
        await p.waitForTimeout(vista === 'radar' ? 800 : 500);
        if (vista === 'fichas') await p.waitForSelector('.tarjeta-ficha');
        if (vista === 'asistentes') await p.waitForSelector('.barra-vis');
        await p.screenshot({ path: join(RAIZ, 'public', 'capturas', `${vista}.png`) });
      }
    }
    await contexto.close();
  }
}
await navegador.close();
s.close();

if (fallas.length) {
  console.error(`Revisión: ${fallas.length} problema(s)`);
  fallas.forEach((f) => console.error(`  - ${f}`));
  process.exit(1);
}
console.log('Revisión: correcta');
