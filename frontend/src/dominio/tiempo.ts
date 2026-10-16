/** Distancia en km entre dos puntos (fórmula del haversine). */
export function distanciaKm(a: { lat: number; lon: number }, b: { lat: number; lon: number }): number {
  const radio = 6371
  const rad = (grados: number) => (grados * Math.PI) / 180
  const dLat = rad(b.lat - a.lat)
  const dLon = rad(b.lon - a.lon)
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLon / 2) ** 2
  return 2 * radio * Math.asin(Math.sqrt(h))
}

/**
 * Traslado estimado en minutos: a pie (4 km/h, factor de rodeo 1.3) hasta 1.5 km;
 * después, en vehículo (25 km/h promedio con el mismo factor) más 10 min de espera.
 */
export function trasladoMin(a: { lat: number; lon: number }, b: { lat: number; lon: number }): number {
  const km = distanciaKm(a, b) * 1.3
  if (km <= 1.5) return Math.max(2, Math.round((km / 4) * 60))
  return Math.round((km / 25) * 60 + 10)
}

/** «10:00» + 95 min → «11:35». */
export function horaDesde(inicio: string, minutos: number): string {
  const [h, m] = inicio.split(':').map(Number)
  const total = (h || 0) * 60 + (m || 0) + Math.round(minutos)
  const horas = Math.floor(total / 60) % 24
  return `${String(horas).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`
}

const DIAS: Record<string, string> = {
  Mo: 'lun',
  Tu: 'mar',
  We: 'mié',
  Th: 'jue',
  Fr: 'vie',
  Sa: 'sáb',
  Su: 'dom',
  PH: 'festivos',
}

/** Traducción simple del formato `opening_hours` de OpenStreetMap. Lo que no reconoce queda igual. */
export function horarioLegible(horario: string): string {
  if (horario.trim() === '24/7') return 'Abierto las 24 horas'
  return horario
    .split(';')
    .map((tramo) =>
      tramo
        .trim()
        .replace(/\b(Mo|Tu|We|Th|Fr|Sa|Su|PH)\b/g, (dia) => DIAS[dia])
        .replace(/-(?=[a-záéíóú])/g, ' a ')
        .replace(/\boff\b/g, 'cerrado')
        .replace(/,(?=\S)/g, ', '),
    )
    .join(' · ')
}

/** «2026-10-03» → «3 oct 2026». */
export function fechaCorta(fecha: string): string {
  const valor = new Date(`${fecha.slice(0, 10)}T12:00:00`)
  if (Number.isNaN(valor.getTime())) return fecha
  return valor.toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' })
}
