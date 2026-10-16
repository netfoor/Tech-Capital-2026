// Vista Asistentes: visibilidad por destino con alternas de idioma y proveedor (spec 009, FR-009-07).
import { IDIOMAS, PROVEEDORES, alSeleccionar, formato, seleccionado, seleccionar } from './comun.js';
import { cargar } from './datos.js';

const esc = (t) =>
  String(t ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

const TIPOS = { gobierno: 'Gobierno', medio: 'Medio', agencia_viajes: 'Agencia o plataforma', red_social: 'Red social', enciclopedia: 'Enciclopedia', blog: 'Blog', otro: 'Otro' };

function alterna(titulo, opciones, activa, alCambiar) {
  const caja = document.createElement('div');
  caja.className = 'alterna';
  caja.setAttribute('role', 'group');
  caja.setAttribute('aria-label', titulo);
  opciones.forEach(([id, nombre]) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = nombre;
    b.dataset.valor = id;
    b.setAttribute('aria-pressed', String(id === activa));
    b.addEventListener('click', () => {
      caja.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      alCambiar(id);
    });
    caja.appendChild(b);
  });
  return caja;
}

export async function montarAsistentes(contenedor, filtros) {
  const [datos, destinos] = await Promise.all([cargar('asistentes.json'), cargar('destinos.json')]);
  const nombres = new Map(destinos.destinos.map((d) => [d.destino_id, d.nombre]));
  let idioma = 'todos';
  let proveedor = 'todos';

  filtros.appendChild(alterna('Idioma de los prompts', [['todos', 'Todos'], ...Object.entries(IDIOMAS).map(([id, i]) => [id, i.nombre])], idioma, (v) => { idioma = v; pintar(); }));
  filtros.appendChild(alterna('Proveedor', [['todos', 'Todos'], ...Object.entries(PROVEEDORES).map(([id, p]) => [id, p.nombre])], proveedor, (v) => { proveedor = v; pintar(); }));

  const c = datos.corridas;
  contenedor.innerHTML = `
    <p class="nota-radar">${formato.entero(c.n)} corridas del ${esc(c.desde)} al ${esc(c.hasta)}, ${c.repeticiones} repeticiones por prompt.
      Modelos: ${c.modelos.map((m) => `${esc(PROVEEDORES[m.proveedor]?.nombre ?? m.proveedor)} (${esc(m.modelo)}, ${esc(m.herramienta)})`).join('; ')}.
      Cada barra es el porcentaje de corridas en que el destino aparece; la línea negra es el intervalo de 95 %.</p>
    <div class="rejilla-asistentes">
      <div><p class="subtitulo-vista" id="as-resumen" aria-live="polite"></p><ul class="barras-vis" id="as-barras"></ul></div>
      <div>
        <h2 class="text-[18px]">Fuentes que citan</h2>
        <ul class="dom-tabla" id="as-dominios"></ul>
        <h2 class="mt-6 text-[18px]">Ejemplo de respuesta</h2>
        <div id="as-ejemplo"></div>
      </div>
    </div>`;
  const barras = contenedor.querySelector('#as-barras');
  const resumen = contenedor.querySelector('#as-resumen');

  function pintar() {
    const seg = datos.segmentos.find((s) => s.idioma === idioma && s.proveedor === proveedor);
    if (!seg) {
      barras.innerHTML = '<li class="vacio border border-dashed border-linea bg-banda px-5 py-8 text-center text-tinta-2">No hay corridas para esta combinación.</li>';
      resumen.textContent = '';
    } else {
      const lista = [...seg.destinos].sort((a, b) => b.pct - a.pct);
      const n = Math.max(...lista.map((d) => d.n));
      resumen.textContent = `Visibilidad por destino · ${idioma === 'todos' ? 'todos los idiomas' : IDIOMAS[idioma].nombre} · ${proveedor === 'todos' ? 'todos los proveedores' : PROVEEDORES[proveedor].nombre} · hasta ${formato.entero(n)} corridas por destino`;
      barras.innerHTML = lista
        .map(
          (d) => `<li class="barra-vis" data-destino="${esc(d.destino_id)}" tabindex="0" role="button" title="n = ${d.n}, k = ${d.k}" aria-label="${esc(nombres.get(d.destino_id))}: ${formato.porcentaje(d.pct)}, ${d.k} de ${d.n} corridas">
            <span class="bv-nombre">${esc(nombres.get(d.destino_id) ?? d.destino_id)}</span>
            <span class="bv-pista" aria-hidden="true"><span class="bv-valor" style="width:${d.pct}%"></span><span class="bv-ic" style="left:${d.ic95_bajo}%;width:${Math.max(d.ic95_alto - d.ic95_bajo, 0.4)}%"></span></span>
            <span class="bv-texto">${formato.porcentaje(d.pct)} <span class="vis-n">(${d.k} de ${d.n})</span></span></li>`,
        )
        .join('');
      barras.querySelectorAll('.barra-vis').forEach((li) => {
        li.addEventListener('click', () => seleccionar(li.dataset.destino, 'asistentes'));
        li.addEventListener('keydown', (e) => { if (e.key === 'Enter') seleccionar(li.dataset.destino, 'asistentes'); });
      });
      marcar(seleccionado());
    }
    const dom = datos.dominios.filter((d) => d.idioma === idioma).slice(0, 10);
    contenedor.querySelector('#as-dominios').innerHTML = dom.length
      ? dom.map((d) => `<li><span>${esc(d.dominio)}</span><span class="vis-n">${esc(TIPOS[d.tipo_dominio] ?? d.tipo_dominio)} · ${formato.porcentaje(d.pct_corridas)} de las corridas</span></li>`).join('')
      : '<li class="vis-n">Sin fuentes citadas en esta selección.</li>';
    const ej = datos.ejemplos.find((e) => (idioma === 'todos' || e.idioma === idioma) && (proveedor === 'todos' || e.proveedor === proveedor)) ?? datos.ejemplos.find((e) => idioma === 'todos' || e.idioma === idioma);
    contenedor.querySelector('#as-ejemplo').innerHTML = ej
      ? `<p class="vis-n">${esc(IDIOMAS[ej.idioma].nombre)} · ${esc(PROVEEDORES[ej.proveedor].nombre)}</p><p class="ejemplo-prompt">${esc(ej.prompt)}</p><blockquote class="ejemplo-resp">${esc(ej.fragmento)}</blockquote>
         <p class="vis-n">Destinos detectados: ${ej.destinos_mencionados.map((id) => esc(nombres.get(id) ?? id)).join(', ') || 'ninguno'}.</p>`
      : '<p class="vis-n">Sin ejemplo para esta selección.</p>';
  }

  function marcar(id) {
    barras.querySelectorAll('.barra-vis').forEach((li) => li.classList.toggle('seleccionado', li.dataset.destino === id));
  }
  alSeleccionar(marcar);
  pintar();
}
