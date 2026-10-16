const numero = new Intl.NumberFormat('es-MX', { maximumFractionDigits: 0 })
const decimal = new Intl.NumberFormat('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
const dos = new Intl.NumberFormat('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

export const SIN_DATO = '—'

export const entero = (v: number | null | undefined) => (v == null ? SIN_DATO : numero.format(v))
export const uno = (v: number | null | undefined) => (v == null ? SIN_DATO : decimal.format(v))
export const pct = (v: number | null | undefined) => (v == null ? SIN_DATO : `${decimal.format(v)} %`)
export const prop = (v: number | null | undefined) =>
  v == null ? SIN_DATO : `${decimal.format(100 * v)} %`
export const dosDec = (v: number | null | undefined) => (v == null ? SIN_DATO : dos.format(v))
export const intervalo = (ic: [number, number] | null | undefined, f: (v: number) => string) =>
  ic ? `${f(ic[0])} a ${f(ic[1])}` : SIN_DATO

export const ATRIBUTOS: Record<string, string> = {
  acceso_sin_escalones: 'Acceso sin escalones',
  rampa: 'Rampa',
  banio_accesible: 'Baño accesible',
  elevador: 'Elevador',
  superficie: 'Superficie',
  asientos: 'Asientos de descanso',
  estacionamiento_reservado: 'Estacionamiento reservado',
  pendiente_pct: 'Pendiente',
  numero_escalones: 'Número de escalones',
}

export const DIMENSIONES: Record<string, string> = {
  accesibilidad: 'Accesibilidad',
  limpieza: 'Limpieza',
  servicio: 'Servicio',
  precio_percibido: 'Precio percibido',
  senalizacion: 'Señalización',
  comodidad: 'Comodidad',
  inclusion: 'Inclusión',
  global: 'Global',
}

export const TIPOS_BARRERA: Record<string, string> = {
  escalones: 'Escalones',
  rampa_bloqueada: 'Rampa bloqueada',
  sin_banio_accesible: 'Sin baño accesible',
  superficie: 'Superficie irregular',
  senalizacion: 'Señalización',
  otro: 'Otro',
}

export const fecha = (iso: string) =>
  new Date(iso).toLocaleString('es-MX', { dateStyle: 'medium', timeStyle: 'short' })
