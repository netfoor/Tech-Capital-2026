// Mapa de Puebla con proyección de INEGI (docs/diseno.md §7 y §8).
import { geoConicConformal, geoPath, select } from 'd3';
import { animate, stagger, svg as svgAnime } from 'animejs';
import { cargar } from './datos.js';
import { ESCALAS, colorDe, formato, movimientoReducido, necesitaBorde } from './comun.js';

const ANCHO = 600;
const ALTO = 800;
const NS = 'http://www.w3.org/2000/svg';

function proyeccion(estado) {
  return geoConicConformal()
    .parallels([17.5, 29.5])
    .rotate([102, 0])
    .fitExtent(
      [
        [16, 16],
        [ANCHO - 16, ALTO - 16],
      ],
      estado,
    );
}

function leyendaDesempeno(contenedor) {
  const e = ESCALAS.desempeno;
  const lista = contenedor.append('div').attr('class', 'leyenda-mapa');
  lista.append('p').attr('class', 'leyenda-titulo').text('Relleno: ocupación hotelera, últimos 12 meses');
  const etiquetas = ['< 30', '30–38', '38–46', '46–54', '54–62', '≥ 62'];
  const fila = lista.append('ul').attr('class', 'leyenda-clases');
  e.colores.forEach((c, i) => {
    const li = fila.append('li');
    li.append('span')
      .attr('class', 'muestra')
      .style('background', c)
      .style('border', necesitaBorde(c) ? '0.5px solid #9CA3AF' : 'none');
    li.append('span').text(`${etiquetas[i]} %`);
  });
  lista
    .append('p')
    .attr('class', 'leyenda-texto')
    .text('Anillo: índice de atención; el trazo completo equivale a 100.');
}

/**
 * En pantallas angostas el lienzo se reduce y las etiquetas quedarían de menos de 12 px reales:
 * se ocultan y el nombre queda en el aria-label y en la tabla (docs/diseno.md §8).
 */
export function ajustarEtiquetas(figura) {
  const revisar = () => {
    const svg = figura.querySelector('svg');
    if (!svg) return;
    const escala = svg.getBoundingClientRect().width / ANCHO;
    figura.classList.toggle('sin-nombres', escala < 0.96);
  };
  new ResizeObserver(revisar).observe(figura);
  revisar();
}

/** Datos y proyección comunes a los mapas; `filas` ya trae la posición `xy` de cada destino. */
export async function cargarBase() {
  const [destinos, radar, estado, municipios] = await Promise.all([
    cargar('destinos.json'),
    cargar('radar.json'),
    cargar('geo/estado.json'),
    cargar('geo/municipios.json'),
  ]);
  const p = proyeccion(estado);
  const porId = new Map(destinos.destinos.map((d) => [d.destino_id, d]));
  const filas = [...radar.destinos.map((r) => ({ ...r, referencia: false })), { ...radar.referencia, referencia: true }]
    .map((r) => ({ ...r, ...porId.get(r.destino_id) }))
    .map((r) => ({ ...r, xy: p([r.lon, r.lat]) }))
    .sort((a, b) => a.xy[0] - b.xy[0]);
  return { destinos, radar, estado, municipios, p, ruta: geoPath(p), filas };
}

/** Lienzo con los municipios y el contorno del estado. */
export function lienzoBase(figura, { estado, municipios, ruta }) {
  const raiz = select(figura);
  raiz.selectAll('*').remove();
  const lienzo = raiz
    .append('svg')
    .attr('viewBox', `0 0 ${ANCHO} ${ALTO}`)
    .attr('class', 'lienzo-mapa')
    .attr('aria-hidden', 'true')
    .attr('focusable', 'false');

  lienzo
    .append('g')
    .selectAll('path')
    .data(municipios.features)
    .join('path')
    .attr('d', ruta)
    .attr('fill', (d) => (d.properties.destino_id ? '#EEF0F3' : '#F7F8FA'))
    .attr('stroke', '#FFFFFF')
    .attr('stroke-width', 0.6);
  lienzo
    .append('g')
    .selectAll('path')
    .data(estado.features)
    .join('path')
    .attr('d', ruta)
    .attr('fill', 'none')
    .attr('stroke', '#9CA3AF')
    .attr('stroke-width', 1);

  return { raiz, lienzo };
}

/** Etiquetas sin traslape: se colocan de norte a sur y se bajan si chocan con otra. */
export function colocarEtiquetas(filas, radio) {
  const cajas = [];
  const ancho = (t) => t.length * 6.6;
  [...filas]
    .sort((a, b) => a.xy[1] - b.xy[1])
    .forEach((d) => {
      const derecha = d.xy[0] <= ANCHO * 0.62;
      const w = ancho(d.nombre);
      const x = derecha ? d.xy[0] + radio + 6 : d.xy[0] - radio - 6 - w;
      let y = d.xy[1] + 4;
      while (cajas.some((c) => x < c.x + c.w && x + w > c.x && Math.abs(y - c.y) < 13)) y += 13;
      cajas.push({ x, w, y });
      d.etiqueta = { derecha, y: y - d.xy[1] };
    });
}

/** Mapa de la portada con relleno de ocupación y anillo de atención. */
export async function mapaPortada(figura) {
  const base = await cargarBase();
  const { p, filas } = base;
  const { raiz, lienzo } = lienzoBase(figura, base);

  const puntos = lienzo
    .append('g')
    .selectAll('g')
    .data(filas)
    .join('g')
    .attr('class', 'punto')
    .attr('transform', (d) => `translate(${d.xy[0]},${d.xy[1]})`);

  const R = 8;
  const RA = 14;
  puntos
    .append('circle')
    .attr('class', 'relleno')
    .attr('r', R)
    .attr('fill', (d) => colorDe(d.ocupacion_12m, ESCALAS.desempeno) ?? '#FFFFFF')
    .attr('stroke', (d) => (necesitaBorde(colorDe(d.ocupacion_12m, ESCALAS.desempeno) ?? '#FFFFFF') ? '#9CA3AF' : '#FFFFFF'))
    .attr('stroke-width', 0.8);
  puntos
    .filter((d) => d.indice_atencion !== null && d.indice_atencion !== undefined)
    .append('circle')
    .attr('class', 'anillo')
    .attr('r', RA)
    .attr('fill', 'none')
    .attr('stroke', '#0058F8')
    .attr('stroke-width', 3)
    .attr('stroke-linecap', 'round')
    .attr('transform', 'rotate(-90)')
    .attr('data-atencion', (d) => d.indice_atencion);
  colocarEtiquetas(filas, RA);
  puntos
    .append('text')
    .attr('class', 'etiqueta nombre-punto')
    .attr('x', (d) => (d.etiqueta.derecha ? RA + 6 : -(RA + 6)))
    .attr('y', (d) => d.etiqueta.y)
    .attr('text-anchor', (d) => (d.etiqueta.derecha ? 'start' : 'end'))
    .text((d) => d.nombre);

  // Escala gráfica en kilómetros (aprox. en el paralelo del centro del estado).
  const [x0, y0] = p([-98.9, 17.95]);
  const [x1] = p([-98.9 + 50 / (111.32 * Math.cos((19 * Math.PI) / 180)), 17.95]);
  const barra = lienzo.append('g').attr('transform', `translate(${x0},${y0})`);
  barra.append('line').attr('x1', 0).attr('x2', x1 - x0).attr('stroke', '#374151').attr('stroke-width', 2);
  barra.append('text').attr('class', 'etiqueta escala-km').attr('y', -6).text('50 km');

  ajustarEtiquetas(figura);
  leyendaDesempeno(raiz);
  raiz
    .append('figcaption')
    .attr('class', 'fuente-mapa')
    .text('Límites: INEGI, Marco Geoestadístico 2025. Ocupación: Observatorio Turístico de Puebla.');
  figura.setAttribute(
    'aria-label',
    `Mapa del estado de Puebla con ${filas.length} destinos: relleno por ocupación hotelera y anillo por atención digital`,
  );

  if (movimientoReducido()) {
    figura.querySelectorAll('.anillo').forEach((a) => {
      a.setAttribute('pathLength', '1');
      a.setAttribute('stroke-dasharray', `${a.dataset.atencion / 100} 1`);
    });
    return;
  }
  animarCarga(figura);
}

/** Única coreografía de carga: de oeste a este, el relleno sube y el anillo se traza. */
function animarCarga(figura) {
  const puntos = [...figura.querySelectorAll('.punto')];
  const rellenos = figura.querySelectorAll('.relleno');
  const anillos = [...figura.querySelectorAll('.anillo')];
  const pasos = stagger(70);
  animate(rellenos, { r: [0, Number(rellenos[0]?.getAttribute('r') ?? 8)], opacity: [0, 1], duration: 500, delay: pasos, ease: 'outCubic' });
  anillos.forEach((a, i) => {
    const fraccion = Number(a.dataset.atencion) / 100;
    const [dibujo] = svgAnime.createDrawable(a);
    const indice = puntos.indexOf(a.parentNode);
    animate(dibujo, { draw: ['0 0', `0 ${fraccion}`], duration: 900, delay: 250 + 70 * (indice >= 0 ? indice : i), ease: 'inOutQuad' });
  });
  animate(figura.querySelectorAll('.etiqueta'), { opacity: [0, 1], duration: 400, delay: 900 });
}
