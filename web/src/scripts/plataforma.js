// Guardia de sesión, rutas por fragmento (#vista o #radar/<destino_id>) y panel de ficha (docs/diseno.md §5.2).
import { cerrarSesion, completarInicio, iniciarSesion, sesion } from './acceso.js';
import { alSeleccionar, seleccionar } from './comun.js';

const VISTAS = ['radar', 'fichas', 'asistentes', 'redes'];
let seleccionadoAhora = null;

function leerRuta() {
  const [vista, destino] = window.location.hash.replace(/^#/, '').split('/');
  return { vista: VISTAS.includes(vista) ? vista : 'radar', destino: destino || null };
}

function mostrarRuta() {
  const { vista, destino } = leerRuta();
  document.querySelectorAll('[data-vista]').forEach((el) => {
    el.hidden = el.dataset.vista !== vista;
  });
  document.querySelectorAll('[data-vista-enlace]').forEach((a) => {
    if (a.dataset.vistaEnlace === vista) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });

  const panel = document.getElementById('panel-ficha');
  const abierto = vista === 'radar' && destino !== null;
  panel.hidden = !abierto;
  document.documentElement.classList.toggle('ficha-abierta', abierto);
  if (abierto) panel.scrollTop = 0;
  document.querySelector('[data-vista="radar"]')?.classList.toggle('con-panel', abierto);
  if (abierto) {
    panel.dataset.destino = destino;
    document.getElementById('panel-ficha-titulo').textContent = destino;
    if (seleccionadoAhora !== destino) {
      seleccionadoAhora = destino;
      seleccionar(destino, 'ruta');
    }
  } else {
    seleccionadoAhora = null;
  }
}

function prepararPlataforma(datosSesion) {
  document.getElementById('sesion-correo').textContent = datosSesion.local
    ? 'Modo local'
    : datosSesion.correo;
  document.getElementById('banda-modo-local').hidden = !datosSesion.local;
  document.getElementById('salir').addEventListener('click', cerrarSesion);

  document.getElementById('panel-ficha-cerrar').addEventListener('click', () => {
    window.location.hash = '#radar';
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && leerRuta().destino) window.location.hash = '#radar';
  });

  // Cualquier vista que elija un destino abre su ficha en el panel de la vista Radar.
  alSeleccionar((destinoId, origen) => {
    seleccionadoAhora = destinoId;
    if (origen !== 'ruta') window.location.hash = `#radar/${destinoId}`;
  });

  window.addEventListener('hashchange', mostrarRuta);
  mostrarRuta();
  document.getElementById('app').hidden = false;
  document.getElementById('estado-acceso').hidden = true;
}

async function arrancar() {
  const mensaje = document.getElementById('estado-acceso-mensaje');
  const reintentar = document.getElementById('estado-acceso-reintentar');
  reintentar.addEventListener('click', () => iniciarSesion());

  try {
    await completarInicio();
    const actual = sesion();
    if (!actual) {
      mensaje.textContent = 'Te llevamos al inicio de sesión…';
      await iniciarSesion();
      return;
    }
    prepararPlataforma(actual);
  } catch (error) {
    mensaje.textContent = `No se pudo iniciar sesión: ${error.message}. Vuelve a intentarlo.`;
    reintentar.hidden = false;
  }
}

arrancar();
