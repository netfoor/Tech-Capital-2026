// Secciones de la página pública que salen de public/datos/ (T009-10 y T009-11). Ninguna cifra se escribe a mano.
import { formato } from './comun.js';
import { cargar, manifiesto } from './datos.js';

const esc = (t) =>
  String(t ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

function cifraLegible(h) {
  if (typeof h.cifra === 'number') {
    if (Number.isInteger(h.cifra)) return formato.entero(h.cifra);
    return Number.isInteger(h.cifra * 10) ? formato.decimal(h.cifra) : String(h.cifra);
  }
  return h.cifra;
}

function enlazar(destino, funcion) {
  const contenedor = document.getElementById(destino);
  if (!contenedor) return;
  funcion(contenedor).catch((error) => {
    contenedor.innerHTML = `<p class="aviso-error">No se pudieron cargar los datos de esta sección: ${esc(error.message)}</p>`;
  });
}

export function montarProblema() {
  enlazar('problema-contenido', async (c) => {
    const { hallazgos } = await cargar('evidencia.json');
    const hallazgosProblema = hallazgos.filter((h) => h.id !== 'tianguis');
    c.innerHTML = `<ul class="hallazgos">${hallazgosProblema
      .map(
        (h) => `<li class="hallazgo" id="hallazgo-${esc(h.id)}">
          <p class="hallazgo-cifra">${esc(cifraLegible(h))}</p>
          <p class="hallazgo-unidad">${esc(h.unidad)}</p>
          <h3 class="text-[19px]">${esc(h.titulo)}</h3>
          <p class="mt-2 text-tinta-2">${esc(h.texto)}</p>
          ${h.serie ? serieBarras(h.serie) : ''}
          <p class="hallazgo-fuente">Fuente: ${esc(h.fuente_id)} · ${esc(h.periodo)}</p></li>`,
      )
      .join('')}</ul>`;
  });
}

function serieBarras(serie) {
  const max = Math.max(...serie.map((s) => s.valor), 1);
  return `<ul class="mini-barras" aria-label="Cuartos libres por día, por destino">${serie
    .map((s) => `<li><span class="mb-nombre">${esc(s.etiqueta)}</span><span class="mb-pista" aria-hidden="true"><span data-estilo="width:${(s.valor / max) * 100}%"></span></span><span class="mb-valor">${formato.entero(s.valor)}</span></li>`)
    .join('')}</ul>`;
}

export function montarTianguis() {
  enlazar('tianguis-contenido', async (c) => {
    const [{ hallazgos }, asistentes, destinos] = await Promise.all([cargar('evidencia.json'), cargar('asistentes.json'), cargar('destinos.json')]);
    const t = hallazgos.find((h) => h.id === 'tianguis');
    const pueblos = new Set(destinos.destinos.filter((d) => d.pueblo_magico).map((d) => d.destino_id));
    const nombresIdioma = { es: 'Español', en: 'Inglés', fr: 'Francés', ko: 'Coreano', zh: 'Chino' };
    const filas = Object.keys(nombresIdioma).map((idioma) => {
      const seg = asistentes.segmentos.find((s) => s.idioma === idioma && s.proveedor === 'todos');
      const valores = (seg?.destinos ?? []).filter((d) => pueblos.has(d.destino_id)).map((d) => d.pct);
      const promedio = valores.length ? valores.reduce((a, b) => a + b, 0) / valores.length : null;
      return { idioma, promedio };
    });
    c.innerHTML = `
      <div class="tianguis-rejilla">
        <div>
          <p class="hallazgo-cifra">${esc(t.cifra)}</p>
          <p class="text-tinta-2">${esc(t.texto)}</p>
          <p class="hallazgo-fuente">Fuente: ${esc(t.fuente_id)}</p>
        </div>
        <div>
          <h3 class="text-[19px]">Una ficha por destino para cada cita</h3>
          <p class="mt-2 text-tinta-2">Cada Pueblo Mágico tiene una hoja con su ocupación, su atención digital, lo que dicen los asistentes y su cuadrante, lista para imprimir y llevar al encuentro con compradores.</p>
          <h3 class="mt-6 text-[19px]">La visibilidad cambia con el idioma</h3>
          <p class="mt-1 text-[14.5px] text-gris">Promedio simple de la visibilidad de los Pueblos Mágicos, por idioma del comprador.</p>
          <ul class="mini-barras" aria-label="Visibilidad promedio por idioma">${filas
            .map((f) => `<li><span class="mb-nombre">${esc(nombresIdioma[f.idioma])}</span><span class="mb-pista" aria-hidden="true"><span data-estilo="width:${f.promedio ?? 0}%"></span></span><span class="mb-valor">${formato.porcentaje(f.promedio)}</span></li>`)
            .join('')}</ul>
          <h3 class="mt-6 text-[19px]">Medir antes y después</h3>
          <p class="mt-2 text-tinta-2">El radar se vuelve a calcular con los mismos prompts y las mismas fuentes después de cada campaña. La diferencia de visibilidad, de búsquedas y de ocupación entre una fecha y otra muestra el efecto de la promoción.</p>
        </div>
      </div>`;
  });
}

export function montarMetodo() {
  enlazar('metodo-contenido', async (c) => {
    const m = await cargar('metodo.json');
    c.innerHTML = `
      <div class="metodo-bloques">
        <section><h3 class="text-[19px]">Procesos</h3><ol class="metodo-lista">${m.procesos.map((p) => `<li><strong>${esc(p.etapa)}.</strong> ${esc(p.descripcion)} <span class="vis-n">(spec ${esc(p.spec)})</span></li>`).join('')}</ol></section>
        <section><h3 class="text-[19px]">Fórmulas</h3><dl class="formulas">${m.formulas.map((f) => `<div><dt>${esc(f.nombre)}</dt><dd><code>${esc(f.expresion)}</code><br />${esc(f.descripcion)}</dd></div>`).join('')}</dl></section>
        <section><h3 class="text-[19px]">Componentes con inteligencia artificial</h3>
          <ul class="metodo-lista">${m.componentes_ia.map((i) => `<li><strong>${esc(i.nombre)}.</strong> ${esc(i.funcion)} <span class="vis-n">Modelo: ${esc(i.modelo)}. Validación: ${esc(i.validacion)}. Resultado: ${esc(i.resultado ?? 'pendiente de validar')}.</span></li>`).join('')}</ul></section>
        <section><h3 class="text-[19px]">Límites</h3><ul class="metodo-lista">${m.limitaciones.map((l) => `<li>${esc(l)}</li>`).join('')}</ul></section>
        <section class="metodo-fuentes"><h3 class="text-[19px]">Fuentes</h3>
          <ul class="metodo-lista">${m.fuentes.map((f) => `<li><strong>${esc(f.titulo)}.</strong> ${esc(f.institucion)}. ${f.url ? `<a href="${esc(f.url)}" rel="noopener">enlace</a>` : ''} <span class="vis-n">${esc(f.uso_en_el_proyecto)}</span></li>`).join('')}</ul></section>
      </div>`;
  });
}

export function montarDatos() {
  enlazar('datos-contenido', async (c) => {
    const m = await manifiesto();
    const descargas = m.archivos.filter((a) => a.ruta.startsWith('../descargas/'));
    const datos = m.archivos.filter((a) => !a.ruta.startsWith('../descargas/'));
    const kb = (b) => (b >= 1048576 ? `${formato.decimal(b / 1048576)} MB` : `${formato.entero(b / 1024)} KB`);
    c.innerHTML = `
      <p class="text-tinta-2">Versión ${esc(m.commit)}, generada el ${esc(m.generado.slice(0, 10))}. Cada archivo se compara con su huella SHA-256 en tu navegador al abrir la página; el resultado está al pie.</p>
      <h3 class="mt-6 text-[19px]">Tablas para descargar</h3>
      <ul class="descargas">${descargas
        .map((a) => {
          const nombre = a.ruta.split('/').pop();
          return `<li><a href="/descargas/${esc(nombre)}" download>${esc(nombre)}</a><span class="vis-n">${kb(a.bytes)} · SHA-256 <code>${esc(a.sha256.slice(0, 12))}…</code></span></li>`;
        })
        .join('')}</ul>
      <details class="mt-6"><summary class="font-bold">Manifiesto: ${datos.length} archivos de datos del sitio</summary>
        <ul class="descargas">${datos.map((a) => `<li><a href="/datos/${esc(a.ruta)}">${esc(a.ruta)}</a><span class="vis-n">${kb(a.bytes)} · <code>${esc(a.sha256.slice(0, 12))}…</code></span></li>`).join('')}</ul></details>`;
  });
}
