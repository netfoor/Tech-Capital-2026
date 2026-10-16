// Almacén local del visitante. Todo vive en este dispositivo: guardados, etiquetas,
// notas privadas, planes y preferencias. Cada acceso a localStorage va en try/catch;
// si el navegador lo bloquea, la app sigue funcionando en memoria y lo avisa.

import { useSyncExternalStore } from 'react'
import type { POIResumen, Usuario } from '../api/tipos'
import type { PlanEditable } from '../dominio/plan'

export interface Guardado {
  poi: POIResumen
  etiquetas: string[]
  nota: string
  guardado_en: string
}

export type PlanGuardado = PlanEditable & { id: string; creado_en: string }

export interface Preferencias {
  lenguajeClaro: boolean
}

export interface EstadoAlmacen {
  guardados: Record<string, Guardado>
  etiquetas: string[]
  planes: PlanGuardado[]
  preferencias: Preferencias
  /** Sesión opcional para enviar reseñas y reportes. Sin sesión, la app funciona igual. */
  sesion: Sesion | null
  disponible: boolean
}

export interface Sesion {
  token: string
  usuario: Usuario
}

const CLAVES = {
  sesion: 'pv360.sesion',
  guardados: 'pv360.guardados',
  etiquetas: 'pv360.etiquetas',
  planes: 'pv360.planes',
  preferencias: 'pv360.preferencias',
  envios: 'pv360.envios',
} as const

let disponible = true

function leer<T>(clave: string, porDefecto: T): T {
  try {
    const texto = window.localStorage.getItem(clave)
    return texto ? (JSON.parse(texto) as T) : porDefecto
  } catch {
    disponible = false
    return porDefecto
  }
}

function escribir(clave: string, valor: unknown): void {
  try {
    window.localStorage.setItem(clave, JSON.stringify(valor))
    disponible = true
  } catch {
    disponible = false
  }
}

function cargar(): EstadoAlmacen {
  disponible = true
  const guardados = leer<Record<string, Guardado>>(CLAVES.guardados, {})
  const etiquetas = leer<string[]>(CLAVES.etiquetas, [])
  const planes = leer<PlanGuardado[]>(CLAVES.planes, [])
  const preferencias = leer<Preferencias>(CLAVES.preferencias, { lenguajeClaro: false })
  const sesion = leer<Sesion | null>(CLAVES.sesion, null)
  return { guardados, etiquetas, planes, preferencias, sesion, disponible }
}

let estado: EstadoAlmacen = cargar()
const oyentes = new Set<() => void>()

function actualizar(cambios: Partial<Omit<EstadoAlmacen, 'disponible'>>) {
  if (cambios.guardados) escribir(CLAVES.guardados, cambios.guardados)
  if (cambios.etiquetas) escribir(CLAVES.etiquetas, cambios.etiquetas)
  if (cambios.planes) escribir(CLAVES.planes, cambios.planes)
  if (cambios.preferencias) escribir(CLAVES.preferencias, cambios.preferencias)
  if (cambios.sesion !== undefined) escribir(CLAVES.sesion, cambios.sesion)
  estado = { ...estado, ...cambios, disponible }
  oyentes.forEach((oyente) => oyente())
}

/** Vuelve a leer del almacenamiento (útil en pruebas y al regresar a la pestaña). */
export function recargarAlmacen() {
  estado = cargar()
  oyentes.forEach((oyente) => oyente())
}

export function obtenerAlmacen(): EstadoAlmacen {
  return estado
}

function suscribir(oyente: () => void) {
  oyentes.add(oyente)
  return () => oyentes.delete(oyente)
}

export function useAlmacen(): EstadoAlmacen {
  return useSyncExternalStore(suscribir, obtenerAlmacen, obtenerAlmacen)
}

function limpiarEtiqueta(etiqueta: string): string {
  return etiqueta.trim().replace(/\s+/g, ' ').slice(0, 30)
}

export function guardarPoi(poi: POIResumen) {
  if (estado.guardados[poi.poi_id]) return
  actualizar({
    guardados: {
      ...estado.guardados,
      [poi.poi_id]: { poi, etiquetas: [], nota: '', guardado_en: new Date().toISOString() },
    },
  })
}

export function quitarPoi(poiId: string) {
  const guardados = { ...estado.guardados }
  delete guardados[poiId]
  actualizar({ guardados })
}

export function estaGuardado(poiId: string): boolean {
  return Boolean(estado.guardados[poiId])
}

export function etiquetar(poiId: string, etiqueta: string) {
  const guardado = estado.guardados[poiId]
  const limpia = limpiarEtiqueta(etiqueta)
  if (!guardado || !limpia || guardado.etiquetas.includes(limpia)) return
  actualizar({
    guardados: { ...estado.guardados, [poiId]: { ...guardado, etiquetas: [...guardado.etiquetas, limpia] } },
    etiquetas: estado.etiquetas.includes(limpia) ? estado.etiquetas : [...estado.etiquetas, limpia],
  })
}

export function quitarEtiqueta(poiId: string, etiqueta: string) {
  const guardado = estado.guardados[poiId]
  if (!guardado) return
  actualizar({
    guardados: {
      ...estado.guardados,
      [poiId]: { ...guardado, etiquetas: guardado.etiquetas.filter((actual) => actual !== etiqueta) },
    },
  })
}

export function anotar(poiId: string, nota: string) {
  const guardado = estado.guardados[poiId]
  if (!guardado) return
  actualizar({ guardados: { ...estado.guardados, [poiId]: { ...guardado, nota: nota.slice(0, 1000) } } })
}

export function guardarPlan(plan: PlanEditable): PlanGuardado {
  const completo: PlanGuardado = {
    ...plan,
    id: plan.id ?? `plan-${Date.now()}`,
    creado_en: new Date().toISOString(),
  }
  actualizar({ planes: [completo, ...estado.planes.filter((actual) => actual.id !== completo.id)] })
  return completo
}

export function borrarPlan(id: string) {
  actualizar({ planes: estado.planes.filter((plan) => plan.id !== id) })
}

export function cambiarPreferencias(cambios: Partial<Preferencias>) {
  actualizar({ preferencias: { ...estado.preferencias, ...cambios } })
}

export function iniciarSesionLocal(sesion: Sesion) {
  actualizar({ sesion })
}

export function cerrarSesion() {
  actualizar({ sesion: null })
}

/** Reseñas y reportes que no llegaron al servidor: se quedan en el dispositivo. */
export function agregarEnvioLocal(tipo: 'resena' | 'barrera', datos: unknown) {
  const envios = leer<unknown[]>(CLAVES.envios, [])
  escribir(CLAVES.envios, [...envios, { tipo, datos, fecha: new Date().toISOString() }])
}
