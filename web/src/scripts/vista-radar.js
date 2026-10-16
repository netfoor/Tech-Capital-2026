// Vista Radar: resumen por cuadrante, mapa por brecha y gráfica; la tabla completa va plegada al final.
import { axisBottom, axisLeft, scaleLinear, select } from 'd3';
import { ajustarEtiquetas, cargarBase, colocarEtiquetas, lienzoBase } from './mapa.js';
import { CUADRANTES, ESCALAS, alSeleccionar, colorDe, formato, necesitaBorde, seleccionado, seleccionar } from './comun.js';

const COLUMNAS = [
  { id: 'nombre', titulo: 'Destino', valor: (d) => d.nombre, texto: true },
  { id: 'cuadrante', titulo: 'Cuadrante', valor: (d) => CUADRANTES[d.cuadrante]?.nombre ?? 'Sin clasificar', texto: true },
  { id: 'indice_atencion', titulo: 'Atención', valor: (d) => d.indice_atencion, formato: formato.decimal },
  { id: 'indice_desempeno', titulo: 'Desempeño', valor: (d) => d.indice_desempeno, formato: formato.decimal },
  { id: 'brecha', titulo: 'Brecha', valor: (d) => d.brecha, formato: formato.decimal },
  { id: 'ocupacion_12m', titulo: 'Ocupación 12 m', valor: (d) => d.ocupacion_12m, formato: formato.porcentaje },
  { id: 'llegadas_12m', titulo: 'Llegadas 12 m', valor: (d) => d.llegadas_12m, formato: formato.entero },
];

// Orden de lectura: primero lo que pide acción.
const ORDEN_CUADRANTES = ['atencion_sin_estancia', 'demanda_poco_visible', 'por_posicionar', 'consolidado'];

const NOMBRES_COMPONENTES = { busqueda: 'búsqueda', video: 'video', panel: 'panel', asistentes: 'asistentes' };

function enlistar(lista) {
  if (lista.length < 2) return lista.join('');
  return `${lista.slice(0, -1).join(', ')} y ${lista[lista.length - 1]}`;
}

export async function montarRadar(contenedor) {
  const base = await cargarBase();
  const { radar, filas } = base;
  const destinos = filas.filter((f) => !f.referencia);
  const porId = new Map(filas.map((f) => [f.destino_id, f]));
  const disponibles = enlistar(radar.componentes_disponibles.map((c) => NOMBRES_COMPONENTES[c] ?? c));

  contenedor.innerHTML = `
    <p class="nota-radar">Brecha = atención − desempeño. Toca un destino para abrir su ficha.</p>
    <div class="resumen-cuadrantes" id="radar-resumen"></div>
    <div class="rejilla-radar">
      <figure class="mapa-brecha" id="radar-mapa" aria-label="Mapa de brecha por destino"></figure>
      <figure class="cuadrantes" id="radar-cuadrantes" aria-label="Gráfica de cuadrantes"></figure>
    </div>
    <details class="detalle-radar">
      <summary>Ver la tabla completa de los 12 destinos</summary>
      <p class="nota-radar">
        Índice de atención con ${disponibles}; periodo de referencia ${radar.periodo_ref.desde} a ${radar.periodo_ref.hasta}.
        Los índices son percentiles entre los 12 Pueblos Mágicos (0 a 100).
      </p>
      <div class="tabla-radar-caja"><table class="tabla-radar" id="radar-tabla"></table></div>
    </details>
  `;

  // --- resumen por cuadrante ---
  const resumen = select(contenedor.querySelector('#radar-resumen'));
  ORDEN_CUADRANTES.forEach((id) => {
    const miembros = destinos.filter((d) => d.cuadrante === id).sort((a, b) => b.brecha - a.brecha);
    const q = CUADRANTES[id];
    const tarjeta = resumen.append('section').attr('class', 'tarjeta-cuadrante').style('border-top-color', q.color);
    const cabeza = tarjeta.append('header');
    cabeza.append('h2').style('color', q.color).text(q.nombre);
    cabeza.append('span').attr('class', 'cuenta').text(miembros.length === 1 ? '1 destino' : `${miembros.length} destinos`);
    tarjeta.append('p').attr('class', 'accion').text(q.accion);
    const lista = tarjeta.append('ul').attr('class', 'fichas-destino');
    if (!miembros.length) lista.append('li').attr('class', 'sin-miembros').text('Ninguno por ahora');
    lista
      .selectAll('li.destino')
      .data(miembros)
      .join('li')
      .attr('class', 'destino')
      .append('button')
      .attr('type', 'button')
      .attr('data-destino', (d) => d.destino_id)
      .attr('aria-label', (d) => `${d.nombre}, brecha ${formato.decimal(d.brecha)}`)
      .on('click', (_, d) => seleccionar(d.destino_id, 'resumen'))
      .html((d) => `${d.nombre} <span class="brecha">${d.brecha > 0 ? '+' : ''}${formato.decimal(d.brecha)}</span>`);
  });

  // --- mapa por brecha ---
  const figura = contenedor.querySelector('#radar-mapa');
  const { raiz, lienzo } = lienzoBase(figura, base);
  lienzo.attr('aria-hidden', null).attr('role', 'group').attr('aria-label', 'Destinos del mapa');
  colocarEtiquetas(filas, 10);
  const puntos = lienzo
    .append('g')
    .selectAll('g')
    .data(filas)
    .join('g')
    .attr('class', 'punto-radar')
    .attr('data-destino', (d) => d.destino_id)
    .attr('transform', (d) => `translate(${d.xy[0]},${d.xy[1]})`)
    .attr('tabindex', 0)
    .attr('role', 'button')
    .attr('aria-label', (d) => `${d.nombre}, brecha ${formato.decimal(d.brecha)}`)
    .on('click', (_, d) => seleccionar(d.destino_id, 'mapa'))
    .on('keydown', (e, d) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        seleccionar(d.destino_id, 'mapa');
      }
    });
  puntos.append('circle').attr('class', 'anillo-sel').attr('r', 15).attr('fill', 'none');
  puntos
    .append('circle')
    .attr('r', 10)
    .attr('fill', (d) => (d.referencia ? '#FFFFFF' : (colorDe(d.brecha, ESCALAS.brecha) ?? '#FFFFFF')))
    .attr('stroke', (d) => (d.referencia ? '#374151' : necesitaBorde(colorDe(d.brecha, ESCALAS.brecha) ?? '#FFFFFF') ? '#9CA3AF' : '#FFFFFF'))
    .attr('stroke-dasharray', (d) => (d.referencia ? '3 2' : null))
    .attr('stroke-width', 1.2)
    .append('title')
    .text((d) => `${d.nombre}: brecha ${formato.decimal(d.brecha)}`);
  puntos
    .append('text')
    .attr('class', 'etiqueta nombre-punto')
    .attr('x', (d) => (d.etiqueta.derecha ? 16 : -16))
    .attr('y', (d) => d.etiqueta.y)
    .attr('text-anchor', (d) => (d.etiqueta.derecha ? 'start' : 'end'))
    .text((d) => d.nombre);

  ajustarEtiquetas(figura);
  const leyenda = raiz.append('div').attr('class', 'leyenda-mapa');
  leyenda.append('p').attr('class', 'leyenda-titulo').text('Relleno: brecha (atención − desempeño)');
  const e = ESCALAS.brecha;
  const etiquetas = ['< −45', '−45 a −25', '−25 a −8', '−8 a 8', '8 a 25', '25 a 45', '≥ 45'];
  const lista = leyenda.append('ul').attr('class', 'leyenda-clases');
  e.colores.forEach((c, i) => {
    const li = lista.append('li');
    li.append('span')
      .attr('class', 'muestra')
      .style('background', c)
      .style('border', necesitaBorde(c) ? '0.5px solid #9CA3AF' : 'none');
    li.append('span').text(etiquetas[i]);
  });
  leyenda.append('p').attr('class', 'leyenda-texto').text('La capital (círculo punteado) es referencia y no entra en los índices.');
  raiz.append('figcaption').attr('class', 'fuente-mapa').text('Límites: INEGI, Marco Geoestadístico 2025.');

  // --- tabla ---
  let orden = { id: 'brecha', descendente: true };
  const tabla = select(contenedor.querySelector('#radar-tabla'));
  function pintarTabla() {
    const col = COLUMNAS.find((c) => c.id === orden.id);
    const datos = [...destinos].sort((a, b) => {
      const va = col.valor(a);
      const vb = col.valor(b);
      if (va === null || va === undefined) return 1;
      if (vb === null || vb === undefined) return -1;
      const r = col.texto ? String(va).localeCompare(String(vb), 'es') : va - vb;
      return orden.descendente ? -r : r;
    });
    tabla.selectAll('*').remove();
    tabla
      .append('thead')
      .append('tr')
      .selectAll('th')
      .data(COLUMNAS)
      .join('th')
      .attr('scope', 'col')
      .attr('class', (c) => (c.texto ? '' : 'num'))
      .attr('aria-sort', (c) => (c.id === orden.id ? (orden.descendente ? 'descending' : 'ascending') : 'none'))
      .append('button')
      .attr('type', 'button')
      .text((c) => c.titulo)
      .on('click', (_, c) => {
        orden = { id: c.id, descendente: orden.id === c.id ? !orden.descendente : !c.texto };
        pintarTabla();
        marcar(seleccionado());
      });
    tabla
      .append('tbody')
      .selectAll('tr')
      .data(datos)
      .join('tr')
      .attr('data-destino', (d) => d.destino_id)
      .attr('tabindex', 0)
      .on('click', (_, d) => seleccionar(d.destino_id, 'tabla'))
      .on('keydown', (ev, d) => {
        if (ev.key === 'Enter') seleccionar(d.destino_id, 'tabla');
      })
      .selectAll('td')
      .data((d) => COLUMNAS.map((c) => ({ c, d })))
      .join('td')
      .attr('class', ({ c }) => (c.texto ? '' : 'num'))
      .text(({ c, d }) => (c.formato ? c.formato(c.valor(d)) : c.valor(d)));
  }
  pintarTabla();

  // --- cuadrantes ---
  const caja = contenedor.querySelector('#radar-cuadrantes');
  function pintarCuadrantes() {
    const ancho = Math.max(320, caja.clientWidth || 640);
    const alto = ancho < 520 ? 380 : 460;
    const m = { arriba: 40, derecha: 24, abajo: 48, izquierda: 52 };
    const x = scaleLinear().domain([0, 100]).range([m.izquierda, ancho - m.derecha]);
    const y = scaleLinear().domain([0, 100]).range([alto - m.abajo, m.arriba]);
    select(caja).selectAll('*').remove();
    const s = select(caja).append('svg').attr('viewBox', `0 0 ${ancho} ${alto}`).attr('width', '100%').attr('role', 'group').attr('aria-label', 'Dispersión de atención contra desempeño');
    s.append('g').selectAll('line').data([0, 25, 50, 75, 100]).join('line')
      .attr('x1', m.izquierda).attr('x2', ancho - m.derecha).attr('y1', (v) => y(v)).attr('y2', (v) => y(v)).attr('stroke', '#E8EBEF');
    s.append('g').attr('transform', `translate(0,${alto - m.abajo})`).call(axisBottom(x).ticks(5).tickSize(0)).call((g) => g.select('.domain').remove()).selectAll('text').attr('fill', '#6b7280').style('font-size', '12.5px');
    s.append('g').attr('transform', `translate(${m.izquierda},0)`).call(axisLeft(y).ticks(5).tickSize(0)).call((g) => g.select('.domain').remove()).selectAll('text').attr('fill', '#6b7280').style('font-size', '12.5px');
    s.append('text').attr('x', ancho / 2).attr('y', alto - 10).attr('text-anchor', 'middle').attr('class', 'eje').text('Índice de atención (más a la derecha, más atención)');
    s.append('text').attr('transform', `translate(14,${alto / 2}) rotate(-90)`).attr('text-anchor', 'middle').attr('class', 'eje').text('Índice de desempeño (más arriba, más desempeño)');
    s.append('line').attr('x1', x(radar.cortes.atencion)).attr('x2', x(radar.cortes.atencion)).attr('y1', m.arriba).attr('y2', alto - m.abajo).attr('stroke', '#9CA3AF').attr('stroke-dasharray', '4 3');
    s.append('line').attr('x1', m.izquierda).attr('x2', ancho - m.derecha).attr('y1', y(radar.cortes.desempeno)).attr('y2', y(radar.cortes.desempeno)).attr('stroke', '#9CA3AF').attr('stroke-dasharray', '4 3');
    const rotulos = [
      ['consolidado', ancho - m.derecha, m.arriba - 16, 'end'],
      ['demanda_poco_visible', m.izquierda + 6, m.arriba - 16, 'start'],
      ['atencion_sin_estancia', ancho - m.derecha, alto - m.abajo - 8, 'end'],
      ['por_posicionar', m.izquierda + 6, alto - m.abajo - 8, 'start'],
    ];
    rotulos.forEach(([id, rx, ry, ancla]) => {
      s.append('text').attr('x', rx).attr('y', ry).attr('text-anchor', ancla).attr('class', 'rotulo-cuadrante').attr('fill', CUADRANTES[id].color).text(CUADRANTES[id].nombre);
    });
    const con = destinos.filter((d) => d.indice_atencion !== null && d.indice_desempeno !== null);
    const g = s.append('g').selectAll('g').data(con).join('g')
      .attr('class', 'punto-cuadrante')
      .attr('data-destino', (d) => d.destino_id)
      .attr('transform', (d) => `translate(${x(d.indice_atencion)},${y(d.indice_desempeno)})`)
      .attr('tabindex', 0).attr('role', 'button')
      .attr('aria-label', (d) => `${d.nombre}, atención ${formato.decimal(d.indice_atencion)}, desempeño ${formato.decimal(d.indice_desempeno)}`)
      .on('click', (_, d) => seleccionar(d.destino_id, 'cuadrantes'))
      .on('keydown', (ev, d) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); seleccionar(d.destino_id, 'cuadrantes'); } });
    g.append('circle').attr('class', 'anillo-sel').attr('r', 11).attr('fill', 'none');
    g.append('circle').attr('r', 6).attr('fill', (d) => CUADRANTES[d.cuadrante]?.color ?? '#6b7280').attr('stroke', '#fff').attr('stroke-width', 1);
    g.append('text').attr('class', 'etiqueta').attr('x', (d) => (x(d.indice_atencion) > ancho - 110 ? -10 : 10)).attr('y', 4).attr('text-anchor', (d) => (x(d.indice_atencion) > ancho - 110 ? 'end' : 'start')).text((d) => d.nombre);
    marcar(seleccionado());
  }
  pintarCuadrantes();
  new ResizeObserver(() => {
    if (caja.clientWidth) pintarCuadrantes();
  }).observe(caja);

  // --- selección compartida ---
  function marcar(id) {
    contenedor.querySelectorAll('[data-destino]').forEach((el) => {
      const activo = el.dataset.destino === id;
      el.classList.toggle('seleccionado', activo);
      if (el.tagName === 'TR') el.setAttribute('aria-selected', String(activo));
    });
  }
  alSeleccionar((id) => marcar(id));
  marcar(seleccionado());
  return { porId };
}
