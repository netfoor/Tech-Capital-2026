// Carga de datos con verificación de huella SHA-256 contra el manifiesto (FR-009-03).

const BASE = '/datos/';

async function sha256(buffer) {
  const resumen = await crypto.subtle.digest('SHA-256', buffer);
  return [...new Uint8Array(resumen)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

function urlDe(ruta, base) {
  return new URL(ruta, new URL(base, globalThis.location?.href ?? 'http://localhost/')).pathname;
}

let manifiestoPendiente = null;

/** Manifiesto de datos; se pide una sola vez. */
export function manifiesto(base = BASE) {
  manifiestoPendiente ??= fetch(`${base}manifiesto.json`).then((r) => {
    if (!r.ok) throw new Error(`No se pudo leer el manifiesto (${r.status})`);
    return r.json();
  });
  return manifiestoPendiente;
}

/** Verifica un archivo contra su huella. Devuelve {ruta, ok, motivo?, bytes}. */
export async function verificarArchivo(entrada, base = BASE, pedir = fetch) {
  try {
    const respuesta = await pedir(urlDe(entrada.ruta, base));
    if (!respuesta.ok) return { ruta: entrada.ruta, ok: false, motivo: `HTTP ${respuesta.status}` };
    const buffer = await respuesta.arrayBuffer();
    const huella = await sha256(buffer);
    return huella === entrada.sha256
      ? { ruta: entrada.ruta, ok: true, bytes: buffer.byteLength, buffer }
      : { ruta: entrada.ruta, ok: false, motivo: 'la huella no coincide' };
  } catch (error) {
    return { ruta: entrada.ruta, ok: false, motivo: error.message };
  }
}

const cache = new Map();

/** Carga un JSON del paquete solo si su huella coincide; si no, lanza un error. */
export async function cargar(ruta, base = BASE) {
  if (!cache.has(ruta)) {
    cache.set(
      ruta,
      (async () => {
        const m = await manifiesto(base);
        const entrada = m.archivos.find((a) => a.ruta === ruta);
        if (!entrada) throw new Error(`${ruta} no está en el manifiesto`);
        const r = await verificarArchivo(entrada, base);
        if (!r.ok) throw new Error(`${ruta}: ${r.motivo}`);
        return JSON.parse(new TextDecoder().decode(r.buffer));
      })(),
    );
  }
  return cache.get(ruta);
}

/** Verifica todos los archivos del manifiesto. */
export async function verificarTodo(base = BASE, pedir = fetch) {
  const m = await manifiesto(base);
  const resultados = await Promise.all(m.archivos.map((a) => verificarArchivo(a, base, pedir)));
  const fallas = resultados.filter((r) => !r.ok);
  return { manifiesto: m, total: resultados.length, fallas };
}

function fechaLegible(iso) {
  return new Date(iso).toLocaleDateString('es-MX', { dateStyle: 'long', timeZone: 'UTC' });
}

/** Pinta el resultado en un elemento: bloque verificado, o aviso y sin bloque. */
export async function montarVerificacion(elemento, { compacto = false } = {}) {
  if (!elemento) return null;
  try {
    if (!globalThis.crypto?.subtle) throw new Error('el navegador no permite verificar huellas aquí');
    const { manifiesto: m, total, fallas } = await verificarTodo();
    elemento.hidden = false;
    if (fallas.length) {
      elemento.dataset.estado = 'falla';
      const detalle = `Aviso: ${fallas.length} de ${total} archivos de datos no coinciden con su huella (${fallas
        .slice(0, 3)
        .map((f) => f.ruta)
        .join(', ')}). No uses estas cifras.`;
      // En la barra, texto corto para no desplazar la navegación; el detalle queda en el título.
      elemento.textContent = compacto ? `Datos sin verificar (${fallas.length} de ${total})` : detalle;
      elemento.title = detalle;
    } else {
      elemento.dataset.estado = 'ok';
      elemento.textContent = compacto
        ? `Datos verificados · ${total} archivos`
        : `Datos verificados: ${total} de ${total} archivos coinciden con su huella SHA-256. Generados el ${fechaLegible(m.generado)} · versión ${m.commit}.`;
    }
    return { total, fallas };
  } catch (error) {
    elemento.hidden = false;
    elemento.dataset.estado = 'falla';
    elemento.textContent = `Aviso: no se pudo verificar la integridad de los datos (${error.message}).`;
    return null;
  }
}
