// Vista Radar: mapa por brecha, atención contra desempeño por destino y gráfica de cuadrantes, con selección compartida.
import { axisBottom, axisLeft, scaleLinear, select } from 'd3';
import { ajustarEtiquetas, cargarBase, colocarEtiquetas, lienzoBase } from './mapa.js';
import { CUADRANTES, ESCALAS, alSeleccionar, colorDe, formato, necesitaBorde, seleccionado, seleccionar } from './comun.js';

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
    <p class="nota-radar">
      Índice de atención con ${disponibles}; periodo de referencia ${radar.periodo_ref.desde} a ${radar.periodo_ref.hasta}.
      Brecha = atención − desempeño: positiva si el destino recibe más atención que desempeño.
    </p>
    <div class="rejilla-radar">
      <figure class="mapa-brecha" id="radar-mapa" aria-label="Mapa de brecha por destino"></figure>
    </div>
    <figure class="brechas" id="radar-brechas" aria-label="Atención y desempeño por destino, ordenados por brecha"></figure>
    <figure class="cuadrantes" id="radar-cuadrantes" aria-label="Gráfica de cuadrantes"></figure>
  `;

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

  // --- atención contra desempeño (gráfica de pesas), ordenada por brecha ---
  const cajaB = contenedor.querySelector('#radar-brechas');
  const ordenB = destinos
    .filter((d) => d.indice_atencion !== null && d.indice_desempeno !== null)
    .sort((a, b) => b.brecha - a.brecha);
  const COLOR_ATENCION = '#0058F8';
  const COLOR_DESEMPENO = '#374151';
  const tip = select(cajaB).append('div').attr('class', 'tip-brecha').attr('role', 'status').property('hidden', true);
  function pintarBrechas() {
    const ancho = Math.max(300, cajaB.clientWidth || 600);
    const fila = 32;
    const estrecho = ancho < 480;
    const m = { arriba: estrecho ? 74 : 56, derecha: 56, abajo: 34, izquierda: estrecho ? 124 : 142 };
    const alto = m.arriba + fila * ordenB.length + m.abajo;
    const x = scaleLinear().domain([0, 100]).range([m.izquierda, ancho - m.derecha]);
    const yF = (i) => m.arriba + fila * i + fila / 2;
    select(cajaB).select('svg').remove();
    const s = select(cajaB).insert('svg', '.tip-brecha').attr('viewBox', `0 0 ${ancho} ${alto}`).attr('width', '100%').attr('role', 'group').attr('aria-label', 'Atención y desempeño por destino');
    // leyenda arriba, con la misma forma que la marca
    const ley = s.append('g').attr('class', 'leyenda-brechas').attr('transform', `translate(${estrecho ? 4 : m.izquierda},16)`);
    ley.append('circle').attr('cx', 6).attr('cy', 0).attr('r', 6).attr('fill', COLOR_ATENCION);
    ley.append('text').attr('x', 18).attr('y', 4).text('Atención digital');
    ley.append('rect').attr('x', estrecho ? 0.5 : 140).attr('y', estrecho ? 16.5 : -5.5).attr('width', 11).attr('height', 11).attr('fill', COLOR_DESEMPENO);
    ley.append('text').attr('x', 18).attr('x', estrecho ? 18 : 158).attr('y', estrecho ? 26 : 4).text('Desempeño (ocupación)');
    s.append('text').attr('class', 'eje').attr('x', ancho - 4).attr('y', m.arriba - 12).attr('text-anchor', 'end').text('Brecha');
    // rejilla recesiva
    s.append('g').selectAll('line').data([0, 25, 50, 75, 100]).join('line')
      .attr('x1', (v) => x(v)).attr('x2', (v) => x(v)).attr('y1', m.arriba - 4).attr('y2', alto - m.abajo + 4).attr('stroke', '#E8EBEF');
    s.append('g').attr('transform', `translate(0,${alto - m.abajo + 4})`).call(axisBottom(x).ticks(5).tickSize(0)).call((g) => g.select('.domain').remove()).selectAll('text').attr('fill', '#6b7280').style('font-size', '12.5px');
    s.append('text').attr('class', 'eje').attr('x', (m.izquierda + ancho - m.derecha) / 2).attr('y', alto - 2).attr('text-anchor', 'middle').text('Percentil entre los 12 Pueblos Mágicos');
    const g = s.append('g').selectAll('g').data(ordenB).join('g')
      .attr('class', 'fila-brecha')
      .attr('data-destino', (d) => d.destino_id)
      .attr('transform', (_, i) => `translate(0,${yF(i)})`)
      .attr('tabindex', 0).attr('role', 'button')
      .attr('aria-label', (d) => `${d.nombre}: atención ${formato.decimal(d.indice_atencion)}, desempeño ${formato.decimal(d.indice_desempeno)}, brecha ${formato.decimal(d.brecha)}, ${CUADRANTES[d.cuadrante]?.nombre ?? ''}`)
      .on('click', (_, d) => seleccionar(d.destino_id, 'brechas'))
      .on('keydown', (ev, d) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); seleccionar(d.destino_id, 'brechas'); } })
      .on('mouseenter focus', (ev, d) => {
        tip.property('hidden', false).html(
          `<strong>${d.nombre}</strong><span>${CUADRANTES[d.cuadrante]?.nombre ?? ''}</span>` +
          `<span>Ocupación 12 m: ${formato.porcentaje(d.ocupacion_12m)}</span>` +
          `<span>Llegadas 12 m: ${formato.entero(d.llegadas_12m)}</span>`);
        // Junto a la pesa, sin tapar la fila: a la derecha si cabe, si no a la izquierda.
        const escala = cajaB.clientWidth / ancho;
        const i = ordenB.indexOf(d);
        const derecha = x(Math.max(d.indice_atencion, d.indice_desempeno)) * escala + 16;
        const izquierda = x(Math.min(d.indice_atencion, d.indice_desempeno)) * escala - 16 - 220;
        let left = derecha;
        let top = (yF(i) - 14) * escala;
        if (derecha + 220 > cajaB.clientWidth - m.derecha * escala) {
          if (izquierda >= m.izquierda * escala) left = izquierda;
          else {
            // No cabe a ningún lado: debajo de la fila, pegado a la derecha.
            left = cajaB.clientWidth - 220 - m.derecha * escala;
            top = (yF(i) + fila / 2 + 4) * escala;
          }
        }
        tip.style('top', `${top}px`).style('left', `${left}px`);
      })
      .on('mouseleave blur', () => tip.property('hidden', true));
    // zona de toque más grande que la marca
    g.append('rect').attr('class', 'fondo-fila').attr('x', 0).attr('y', -fila / 2).attr('width', ancho).attr('height', fila).attr('fill', 'transparent');
    g.append('text').attr('class', 'nombre-fila').attr('x', m.izquierda - 12).attr('y', 4).attr('text-anchor', 'end').text((d) => d.nombre);
    g.append('line')
      .attr('x1', (d) => x(Math.min(d.indice_atencion, d.indice_desempeno)))
      .attr('x2', (d) => x(Math.max(d.indice_atencion, d.indice_desempeno)))
      .attr('stroke', '#9CA3AF').attr('stroke-width', 2);
    g.append('rect').attr('x', (d) => x(d.indice_desempeno) - 5.5).attr('y', -5.5).attr('width', 11).attr('height', 11)
      .attr('fill', COLOR_DESEMPENO).attr('stroke', '#fff').attr('stroke-width', 2);
    g.append('circle').attr('cx', (d) => x(d.indice_atencion)).attr('r', 6.5)
      .attr('fill', COLOR_ATENCION).attr('stroke', '#fff').attr('stroke-width', 2);
    g.append('text').attr('class', 'valor-brecha').attr('x', ancho - 4).attr('y', 4).attr('text-anchor', 'end')
      .text((d) => `${d.brecha > 0 ? '+' : ''}${formato.decimal(d.brecha)}`);
    marcar(seleccionado());
  }
  pintarBrechas();
  new ResizeObserver(() => {
    if (cajaB.clientWidth) pintarBrechas();
  }).observe(cajaB);

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
    });
  }
  alSeleccionar((id) => marcar(id));
  marcar(seleccionado());
  return { porId };
}
