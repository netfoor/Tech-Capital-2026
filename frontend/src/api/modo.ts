import { useSyncExternalStore } from 'react'

// Origen de los datos durante la sesión. Pasa a «demo» al primer fallo de la API
// y ya no regresa, para que la persona no vea datos mezclados sin aviso.
export type OrigenDatos = 'desconocido' | 'api' | 'demo'

interface EstadoModo {
  origen: OrigenDatos
  vioSinteticos: boolean
}

let estado: EstadoModo = { origen: 'desconocido', vioSinteticos: false }
const oyentes = new Set<() => void>()

function emitir(nuevo: EstadoModo) {
  if (nuevo.origen === estado.origen && nuevo.vioSinteticos === estado.vioSinteticos) return
  estado = nuevo
  oyentes.forEach((oyente) => oyente())
}

export function marcarOrigen(origen: Exclude<OrigenDatos, 'desconocido'>) {
  if (estado.origen === 'demo') return
  emitir({ ...estado, origen })
}

export function marcarSinteticos(items: { is_synthetic: boolean }[]) {
  if (items.some((item) => item.is_synthetic)) emitir({ ...estado, vioSinteticos: true })
}

export function obtenerModo(): EstadoModo {
  return estado
}

export function reiniciarModo() {
  estado = { origen: 'desconocido', vioSinteticos: false }
  oyentes.forEach((oyente) => oyente())
}

function suscribir(oyente: () => void) {
  oyentes.add(oyente)
  return () => oyentes.delete(oyente)
}

export function useModoDatos(): EstadoModo {
  return useSyncExternalStore(suscribir, obtenerModo, obtenerModo)
}
