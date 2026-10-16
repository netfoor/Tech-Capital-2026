import type { DiaPlan, Itinerario, NoIncluido, Parada, PlanMultidia, POIResumen } from '../api/tipos'
import { trasladoMin } from './tiempo'

/** Plan editable en la interfaz: siempre por días (desde cero = un solo día). */
export interface PlanEditable {
  id?: string
  nombre: string
  hora_inicio: string
  dias: DiaPlan[]
  no_incluidos: NoIncluido[]
  alternativos: POIResumen[]
  explicacion: string
  datos_desconocidos: string[]
  /** Días cuyos traslados se recalcularon tras una edición. */
  editados: number[]
  /** Paradas agregadas desde las alternativas (se muestran como «sugerencia»). */
  sugeridos: string[]
}

export function desdeItinerario(itinerario: Itinerario, hora_inicio: string, nombre: string): PlanEditable {
  return {
    nombre,
    hora_inicio,
    dias: [{ dia: 1, paradas: itinerario.paradas }],
    no_incluidos: itinerario.no_incluidos,
    alternativos: itinerario.alternativos,
    explicacion: itinerario.explicacion,
    datos_desconocidos: itinerario.datos_desconocidos,
    editados: [],
    sugeridos: [],
  }
}

export function desdeMultidia(plan: PlanMultidia, hora_inicio: string, nombre: string, explicacion: string): PlanEditable {
  return {
    nombre,
    hora_inicio,
    dias: plan.dias,
    no_incluidos: plan.no_incluidos,
    alternativos: plan.alternativos,
    explicacion,
    datos_desconocidos: [],
    editados: [],
    sugeridos: [],
  }
}

/** Recalcula orden, traslados y llegadas de un día después de editarlo. */
export function recalcularDia(paradas: Parada[]): Parada[] {
  let reloj = 0
  return paradas.map((parada, indice) => {
    const anterior = paradas[indice - 1]
    const traslado = anterior ? trasladoMin(anterior.poi, parada.poi) : 0
    reloj += traslado
    const nueva: Parada = { ...parada, orden: indice + 1, traslado_min: traslado, llegada_min: reloj }
    reloj += parada.estancia_min
    return nueva
  })
}

function conDia(plan: PlanEditable, dia: number, paradas: Parada[]): PlanEditable {
  return {
    ...plan,
    dias: plan.dias.map((actual) => (actual.dia === dia ? { ...actual, paradas: recalcularDia(paradas) } : actual)),
    editados: plan.editados.includes(dia) ? plan.editados : [...plan.editados, dia],
  }
}

export function moverParada(plan: PlanEditable, dia: number, indice: number, delta: -1 | 1): PlanEditable {
  const paradas = [...(plan.dias.find((actual) => actual.dia === dia)?.paradas ?? [])]
  const destino = indice + delta
  if (destino < 0 || destino >= paradas.length) return plan
  ;[paradas[indice], paradas[destino]] = [paradas[destino], paradas[indice]]
  return conDia(plan, dia, paradas)
}

export function quitarParada(plan: PlanEditable, dia: number, indice: number): PlanEditable {
  const paradas = (plan.dias.find((actual) => actual.dia === dia)?.paradas ?? []).filter((_, i) => i !== indice)
  return conDia(plan, dia, paradas)
}

export function agregarAlternativo(plan: PlanEditable, poi: POIResumen, estancia_min: number, motivo: string): PlanEditable {
  const ultimo = plan.dias[plan.dias.length - 1] ?? { dia: 1, paradas: [] }
  const nueva: Parada = { orden: 0, poi, llegada_min: 0, estancia_min, traslado_min: 0, motivo, advertencias: [] }
  const base = plan.dias.length === 0 ? { ...plan, dias: [ultimo] } : plan
  const actualizado = conDia(base, ultimo.dia, [...ultimo.paradas, nueva])
  return {
    ...actualizado,
    alternativos: plan.alternativos.filter((alternativo) => alternativo.poi_id !== poi.poi_id),
    sugeridos: [...plan.sugeridos, poi.poi_id],
  }
}

export function totalParadas(plan: PlanEditable): number {
  return plan.dias.reduce((suma, dia) => suma + dia.paradas.length, 0)
}
