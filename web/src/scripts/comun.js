// Selección compartida, formatos y escalas de color (docs/diseno.md §3 y §8).

export const ESCALAS = {
  desempeno: {
    cortes: [30, 38, 46, 54, 62],
    colores: ['#FDECD3', '#F8CF98', '#EBA75A', '#D07F2C', '#A85A12', '#7A3E0B'],
  },
  atencion: {
    cortes: [17, 33, 50, 67, 83],
    colores: ['#DCE8FE', '#AFC9FB', '#7EA6F7', '#4C7FF0', '#1E5BE3', '#0B3FAE'],
  },
  brecha: {
    cortes: [-45, -25, -8, 8, 25, 45],
    colores: ['#7A3E0B', '#B45309', '#E7B46E', '#EEF0F3', '#8FB3F7', '#2F6EEA', '#0B3FAE'],
  },
};

export const CUADRANTES = {
  consolidado: { nombre: 'Consolidado', color: '#374151' },
  atencion_sin_estancia: { nombre: 'Atención sin estancia', color: '#0058F8' },
  demanda_poco_visible: { nombre: 'Demanda poco visible', color: '#B45309' },
  por_posicionar: { nombre: 'Por posicionar', color: '#00796B' },
};

export const IDIOMAS = {
  es: { nombre: 'Español', color: '#0058F8' },
  en: { nombre: 'Inglés', color: '#00796B' },
  fr: { nombre: 'Francés', color: '#6D28D9' },
  ko: { nombre: 'Coreano', color: '#B45309' },
  zh: { nombre: 'Chino', color: '#9F1239' },
};

export const PROVEEDORES = {
  openai: { nombre: 'OpenAI', color: '#374151' },
  google: { nombre: 'Google', color: '#0058F8' },
};

export const BORDE_RELLENO_CLARO = '#9CA3AF';

/** Índice de clase de un valor según los cortes de una escala. */
export function clase(valor, escala) {
  let i = 0;
  while (i < escala.cortes.length && valor >= escala.cortes[i]) i += 1;
  return i;
}

/** Color de relleno de un valor; null si no hay dato. */
export function colorDe(valor, escala) {
  if (valor === null || valor === undefined || Number.isNaN(valor)) return null;
  return escala.colores[clase(valor, escala)];
}

/** Los rellenos claros llevan borde de 0.5 px (docs/diseno.md §3). */
export function necesitaBorde(hex) {
  const canal = (i) => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255;
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  };
  const luminancia = 0.2126 * canal(1) + 0.7152 * canal(3) + 0.0722 * canal(5);
  return luminancia > 0.55;
}

// Formatos de México: coma de miles y punto decimal.
const decimal1 = new Intl.NumberFormat('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const entero = new Intl.NumberFormat('es-MX', { maximumFractionDigits: 0 });
const SIN_DATO = 'sin dato';

export const formato = {
  porcentaje: (x) => (x === null || x === undefined ? SIN_DATO : `${decimal1.format(x)} %`),
  decimal: (x) => (x === null || x === undefined ? SIN_DATO : decimal1.format(x)),
  entero: (x) => (x === null || x === undefined ? SIN_DATO : entero.format(x)),
  pesos: (x) => (x === null || x === undefined ? SIN_DATO : `$${entero.format(x)}`),
};

// Selección compartida entre mapa, tabla, cuadrantes, ficha y asistentes (FR-009-04).
const EVENTO = 'destino:seleccionado';
let actual = null;

export function seleccionar(destinoId, origen) {
  actual = destinoId;
  document.dispatchEvent(new CustomEvent(EVENTO, { detail: { destinoId, origen } }));
}

export function alSeleccionar(funcion) {
  const manejador = (e) => funcion(e.detail.destinoId, e.detail.origen);
  document.addEventListener(EVENTO, manejador);
  return () => document.removeEventListener(EVENTO, manejador);
}

export function seleccionado() {
  return actual;
}

export function movimientoReducido() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}
