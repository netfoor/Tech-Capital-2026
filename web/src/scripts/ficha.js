// Ficha de destino: panel lateral, vista Fichas e impresión de una hoja carta (docs/diseno.md §5.2 y §6).
import { CUADRANTES, IDIOMAS, alSeleccionar, formato, seleccionar } from './comun.js';
import { cargar } from './datos.js';

const ORIGEN = {
  oficial: { forma: '■', color: '#1E7D12', nombre: 'Oficial' },
  senal: { forma: '▰', color: '#00796B', nombre: 'Señal' },
  asistente: { forma: '●', color: '#0058F8', nombre: 'Asistentes' },
};

const COMPONENTES = {
  busqueda: { nombre: 'Búsqueda en Google', origen: 'senal' },
  video: { nombre: 'Video en YouTube', origen: 'senal' },
  panel: { nombre: 'Panel de TikTok', origen: 'senal' },
  asistentes: { nombre: 'Asistentes', origen: 'asistente' },
};

const esc = (t) =>
  String(t ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

const marca = (origen) =>
  `<span class="marca-origen" data-estilo="color:${ORIGEN[origen].color}" aria-label="${ORIGEN[origen].nombre}" title="${ORIGEN[origen].nombre}">${ORIGEN[origen].forma}</span>`;

function sparkline(serie) {
  const valores = serie.map((s) => s.ocupacion_pct).filter((v) => v !== null);
  if (valores.length < 2) return '';
  const w = 360;
  const h = 70;
  const max = Math.max(...valores, 1);
  const puntos = serie
    .map((s, i) => (s.ocupacion_pct === null ? null : `${((i / (serie.length - 1)) * w).toFixed(1)},${(h - (s.ocupacion_pct / max) * (h - 6) - 3).toFixed(1)}`))
    .filter(Boolean)
    .join(' ');
  return `<svg viewBox="0 0 ${w} ${h}" class="spark" role="img" aria-label="Ocupación mensual de los últimos 36 meses, de ${serie[0].periodo} a ${serie[serie.length - 1].periodo}"><polyline points="${puntos}" fill="none" stroke="#A85A12" stroke-width="2"/></svg>`;
}

function barraVisibilidad(i) {
  const bajo = i.ic95_bajo ?? i.pct;
  const alto = i.ic95_alto ?? i.pct;
  return `<li class="vis-fila" title="n = ${i.n}, k = ${i.k}">
    <span class="vis-idioma">${esc(IDIOMAS[i.idioma]?.nombre ?? i.idioma)}</span>
    <span class="vis-barra" aria-hidden="true"><span class="vis-valor" data-estilo="width:${i.pct}%"></span><span class="vis-ic" data-estilo="left:${bajo}%;width:${Math.max(alto - bajo, 0.5)}%"></span></span>
    <span class="vis-texto">${formato.porcentaje(i.pct)} <span class="vis-n">(${i.k} de ${i.n})</span></span>
  </li>`;
}

/** HTML de una ficha completa; sirve igual para el panel y para la hoja impresa. */
export function htmlFicha(f, { titulo = true } = {}) {
  const d = f.desempeno;
  const r = f.radar;
  const cuadrante = r.cuadrante ? CUADRANTES[r.cuadrante] : null;
  const todos = f.asistentes?.por_idioma ?? [];
  const global = todos.length ? { k: todos.reduce((s, i) => s + i.k, 0), n: todos.reduce((s, i) => s + i.n, 0) } : null;
  const componentes = Object.entries(r.componentes)
    .map(([id, c]) => {
      const def = COMPONENTES[id] ?? { nombre: id, origen: 'senal' };
      return `<li class="comp-fila">${marca(def.origen)}<span class="comp-nombre">${esc(def.nombre)}</span>
        <span class="comp-barra" aria-hidden="true"><span data-estilo="width:${c.pctl}%"></span></span>
        <span class="comp-valor">${formato.decimal(c.pctl)}</span></li>`;
    })
    .join('');
  return `<article class="ficha" data-destino="${esc(f.destino.destino_id)}">
    ${titulo ? `<header><h2 class="ficha-nombre">${esc(f.destino.nombre)}</h2><p class="ficha-zona">${esc(f.destino.zona)}</p></header>` : ''}
    ${cuadrante ? `<p class="ficha-cuadrante" data-estilo="color:${cuadrante.color}">${esc(cuadrante.nombre)}</p>` : '<p class="ficha-cuadrante">Referencia: no entra en el radar</p>'}
    ${r.recomendacion ? `<p class="ficha-reco">${esc(r.recomendacion)}</p>` : ''}
    <dl class="cifras">
      <div><dt>${marca('oficial')} Ocupación, 12 meses</dt><dd>${formato.porcentaje(d.ocupacion_12m)}</dd><dd class="cifra-nota">Mediana de los Pueblos Mágicos: ${formato.porcentaje(d.mediana_pm_ocupacion_12m)}</dd></div>
      <div><dt>${marca('asistente')} Visibilidad en asistentes</dt><dd>${global ? formato.porcentaje((global.k / global.n) * 100) : 'sin dato'}</dd><dd class="cifra-nota">${global ? `${global.k} de ${global.n} corridas` : ''}</dd></div>
      <div><dt>${marca('oficial')} Llegadas de turistas</dt><dd>${formato.entero(d.llegadas_12m)}</dd><dd class="cifra-nota">${d.crecimiento_llegadas_pct === null ? '' : `${formato.porcentaje(d.crecimiento_llegadas_pct)} frente al año anterior`}</dd></div>
      <div><dt>${marca('oficial')} Estadía y derrama</dt><dd>${formato.decimal(d.estadia_promedio_dias)} noches</dd><dd class="cifra-nota">${formato.pesos(d.derrama_por_visitante_mxn)} por visitante</dd></div>
    </dl>
    ${componentes ? `<h3 class="ficha-sub">Atención por componente (percentil entre los 12)</h3><ul class="comp-lista">${componentes}</ul>` : ''}
    ${todos.length ? `<h3 class="ficha-sub">Visibilidad por idioma (intervalo de 95 %)</h3><ul class="vis-lista">${todos.map(barraVisibilidad).join('')}</ul>` : ''}
    ${f.asistentes?.dominios?.length ? `<h3 class="ficha-sub">Fuentes que citan los asistentes</h3><ul class="dom-lista">${f.asistentes.dominios.map((x) => `<li>${esc(x.dominio)} <span class="vis-n">(${x.n_citas})</span></li>`).join('')}</ul>` : ''}
    ${f.serie_mensual.length ? `<h3 class="ficha-sub">Ocupación mensual</h3>${sparkline(f.serie_mensual)}` : ''}
    ${f.notas.length ? `<ul class="ficha-notas">${f.notas.map((n) => `<li>${esc(n)}</li>`).join('')}</ul>` : ''}
    <p class="ficha-pie">Periodo ${esc(f.periodo_ref.desde)} a ${esc(f.periodo_ref.hasta)}. Fuentes: ${f.fuentes.map(esc).join(', ')}.</p>
  </article>`;
}

/** Imprime una sola hoja carta con la ficha indicada. */
export async function imprimirFicha(destinoId) {
  const f = await cargar(`fichas/${destinoId}.json`);
  let hoja = document.getElementById('hoja-impresion');
  if (!hoja) {
    hoja = document.createElement('div');
    hoja.id = 'hoja-impresion';
    document.body.appendChild(hoja);
  }
  hoja.innerHTML = `<div class="hoja"><p class="hoja-marca">Radar de Atención Turística de Puebla</p>${htmlFicha(f)}</div>`;
  window.print();
}

/** Panel lateral: se llena cada vez que cambia la selección. */
export function montarPanel() {
  const titulo = document.getElementById('panel-ficha-titulo');
  const cuerpo = document.getElementById('panel-ficha-contenido');
  alSeleccionar(async (id) => {
    cuerpo.innerHTML = '<p class="text-tinta-2">Cargando la ficha…</p>';
    try {
      const f = await cargar(`fichas/${id}.json`);
      titulo.textContent = f.destino.nombre;
      cuerpo.innerHTML =
        htmlFicha(f, { titulo: false }) +
        `<div class="ficha-acciones"><button type="button" class="boton boton-primario" data-accion="imprimir">Descargar ficha</button>
         <a class="boton boton-secundario" href="#radar" data-accion="mapa">Ver en el mapa</a></div>`;
      cuerpo.querySelector('[data-accion="imprimir"]').addEventListener('click', () => imprimirFicha(id));
      cuerpo.querySelector('[data-accion="mapa"]').addEventListener('click', () => document.getElementById('radar-mapa')?.scrollIntoView({ block: 'center' }));
    } catch (error) {
      titulo.textContent = id;
      cuerpo.innerHTML = `<p class="aviso-error">No se pudo cargar la ficha: ${esc(error.message)}</p>`;
    }
  });
}

/** Vista Fichas: una tarjeta por destino con su descarga. */
export async function montarFichas(contenedor) {
  const destinos = await cargar('destinos.json');
  const radar = await cargar('radar.json');
  const filas = new Map([...radar.destinos, radar.referencia].map((r) => [r.destino_id, r]));
  const lista = [...destinos.destinos]
    .filter((d) => filas.has(d.destino_id))
    .sort((a, b) => (filas.get(b.destino_id).brecha ?? -999) - (filas.get(a.destino_id).brecha ?? -999));
  contenedor.innerHTML = `<ul class="rejilla-fichas">${lista
    .map((d) => {
      const r = filas.get(d.destino_id);
      const c = r.cuadrante ? CUADRANTES[r.cuadrante] : null;
      return `<li class="tarjeta-ficha">
        <h2 class="text-[19px]">${esc(d.nombre)}</h2>
        <p class="ficha-zona">${esc(d.zona)}</p>
        <p class="ficha-cuadrante" data-estilo="color:${c ? c.color : '#6b7280'}">${esc(c ? c.nombre : 'Referencia')}</p>
        <p class="cifra-nota">Ocupación ${formato.porcentaje(r.ocupacion_12m)} · Atención ${formato.decimal(r.indice_atencion)}</p>
        <div class="ficha-acciones">
          <button type="button" class="boton boton-secundario" data-ver="${esc(d.destino_id)}">Ver ficha</button>
          <button type="button" class="boton boton-primario" data-imprimir="${esc(d.destino_id)}">Descargar para la cita</button>
        </div></li>`;
    })
    .join('')}</ul>`;
  contenedor.querySelectorAll('[data-ver]').forEach((b) => b.addEventListener('click', () => seleccionar(b.dataset.ver, 'fichas')));
  contenedor.querySelectorAll('[data-imprimir]').forEach((b) => b.addEventListener('click', () => imprimirFicha(b.dataset.imprimir)));
}
