// Motor local del modo de demostración. Aplica las mismas restricciones indispensables
// que la interfaz promete; no sustituye al recomendador de la spec 015.

import type {
  AtributoAccesibilidad,
  Destino,
  FiltrosPOI,
  Itinerario,
  ListaPOI,
  NoIncluido,
  Parada,
  PlanMultidia,
  POIDetalle,
  POIResumen,
  Restricciones,
  SolicitudDesdeGuardados,
  SolicitudRecomendacion,
} from '../api/tipos'
import { banioAccesible, cabeEnPresupuesto, evaluarRestricciones, sinEscalones } from '../dominio/accesibilidad'
import { distanciaKm, trasladoMin } from '../dominio/tiempo'
import { es } from '../i18n/es'
import { DESTINOS_DEMO, POIS_DEMO } from './datos'

const m = es.motor

function normalizar(texto: string): string {
  return texto
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
}

function resumen(poi: POIDetalle): POIResumen {
  const { poi_id, nombre, categoria, destino_id, corredor_id, lat, lon, costo_rango, accesibilidad, cobertura_accesibilidad, is_synthetic } = poi
  return { poi_id, nombre, categoria, destino_id, corredor_id, lat, lon, costo_rango, accesibilidad, cobertura_accesibilidad, is_synthetic }
}

export function filtrarPois(pois: POIResumen[], filtros: FiltrosPOI): POIResumen[] {
  const consulta = filtros.q ? normalizar(filtros.q.trim()) : ''
  const solo = Boolean(filtros.solo_verificados)
  return pois.filter((poi) => {
    if (consulta && !normalizar(poi.nombre).includes(consulta)) return false
    if (filtros.categoria && poi.categoria !== filtros.categoria) return false
    if (filtros.destino_id && poi.destino_id !== filtros.destino_id) return false
    if (filtros.corredor_id && poi.corredor_id !== filtros.corredor_id) return false
    if (filtros.costo_max && !cabeEnPresupuesto(poi, filtros.costo_max)) return false
    if (filtros.sin_escalones && !sinEscalones(poi, solo)) return false
    if (filtros.banio_accesible && !banioAccesible(poi, solo)) return false
    if (solo && poi.cobertura_accesibilidad === 'sin_verificar') return false
    return true
  })
}

export function listarPois(filtros: FiltrosPOI = {}): ListaPOI {
  const todos = filtrarPois(POIS_DEMO.map(resumen), filtros)
  const inicio = filtros.offset ?? 0
  const fin = filtros.limit ? inicio + filtros.limit : undefined
  return { items: todos.slice(inicio, fin), total: todos.length }
}

export function obtenerPoi(poiId: string): POIDetalle | null {
  return POIS_DEMO.find((poi) => poi.poi_id === poiId) ?? null
}

export function listarDestinos(): Destino[] {
  return DESTINOS_DEMO
}

const ESTANCIA: Record<string, number> = {
  museo: 75,
  zona_arqueologica: 90,
  templo: 30,
  plaza: 30,
  mercado: 45,
  artesanias: 40,
  mirador: 45,
  biblioteca: 40,
}

export function estanciaMin(poi: POIResumen): number {
  return ESTANCIA[poi.categoria] ?? 45
}

interface Candidato {
  poi: POIResumen
  puntaje: number
  advertencias: string[]
  desconocidos: AtributoAccesibilidad[]
}

function nombreCategoria(categoria: string): string {
  return es.categorias[categoria] ?? categoria.replace(/_/g, ' ')
}

function clasificar(
  pois: POIResumen[],
  restricciones: Restricciones | undefined,
  presupuesto: SolicitudRecomendacion['presupuesto'],
  intereses: string[] = [],
): { candidatos: Candidato[]; noIncluidos: NoIncluido[] } {
  const candidatos: Candidato[] = []
  const noIncluidos: NoIncluido[] = []
  for (const poi of pois) {
    if (!cabeEnPresupuesto(poi, presupuesto)) {
      noIncluidos.push({ poi_id: poi.poi_id, motivo: m.fueraPresupuesto })
      continue
    }
    const evaluacion = evaluarRestricciones(poi, restricciones)
    if (!evaluacion.cumple) {
      noIncluidos.push({ poi_id: poi.poi_id, motivo: evaluacion.motivo ?? '' })
      continue
    }
    let puntaje = 1
    if (intereses.includes(poi.categoria)) puntaje += 3
    if (poi.cobertura_accesibilidad === 'verificada') puntaje += 1
    if (poi.cobertura_accesibilidad === 'parcial') puntaje += 0.5
    if (poi.costo_rango === 'gratis') puntaje += 0.5
    candidatos.push({ poi, puntaje, advertencias: evaluacion.advertencias, desconocidos: evaluacion.desconocidos })
  }
  return { candidatos, noIncluidos }
}

function motivoDe(candidato: Candidato, intereses: string[], cercano: boolean): string {
  const partes: string[] = []
  if (intereses.includes(candidato.poi.categoria)) partes.push(m.motivoInteres(nombreCategoria(candidato.poi.categoria)))
  if (candidato.poi.cobertura_accesibilidad === 'verificada') partes.push(m.motivoVerificado)
  if (candidato.poi.costo_rango === 'gratis') partes.push(m.motivoGratis)
  if (cercano) partes.push(m.motivoCercano)
  if (partes.length === 0) partes.push(m.motivoGeneral)
  const texto = partes.join(', ')
  return texto.charAt(0).toUpperCase() + texto.slice(1) + '.'
}

interface Secuencia {
  paradas: Parada[]
  usados: Set<string>
  desconocidos: string[]
}

/** Secuencia voraz: en cada paso elige el candidato con mejor puntaje y menor traslado que quepa. */
function secuenciar(
  candidatos: Candidato[],
  minutos: number,
  intereses: string[],
  restricciones: Restricciones | undefined,
  inicio?: { lat: number; lon: number },
): Secuencia {
  const pendientes = [...candidatos]
  const paradas: Parada[] = []
  const usados = new Set<string>()
  const desconocidos: string[] = []
  let posicion = inicio
  let reloj = 0
  let desdeDescanso = 0

  while (pendientes.length > 0) {
    let mejor = -1
    let mejorValor = -Infinity
    for (let i = 0; i < pendientes.length; i++) {
      const candidato = pendientes[i]
      const traslado = posicion ? trasladoMin(posicion, candidato.poi) : 0
      if (reloj + traslado + estanciaMin(candidato.poi) > minutos) continue
      const valor = candidato.puntaje - traslado / 15
      if (valor > mejorValor) {
        mejorValor = valor
        mejor = i
      }
    }
    if (mejor === -1) break
    const [elegido] = pendientes.splice(mejor, 1)
    const traslado = posicion ? trasladoMin(posicion, elegido.poi) : 0
    const estancia = estanciaMin(elegido.poi)
    const advertencias = [...elegido.advertencias]
    if (traslado > 30) advertencias.push(m.trasladoLargo)
    desdeDescanso += traslado
    if (restricciones?.descansos_cada_min && desdeDescanso >= restricciones.descansos_cada_min) {
      advertencias.unshift(m.descanso(desdeDescanso))
      desdeDescanso = 0
    }
    reloj += traslado
    paradas.push({
      orden: paradas.length + 1,
      poi: elegido.poi,
      llegada_min: reloj,
      estancia_min: estancia,
      traslado_min: traslado,
      motivo: motivoDe(elegido, intereses, paradas.length > 0 && traslado <= 10),
      advertencias,
    })
    for (const atributo of elegido.desconocidos) {
      desconocidos.push(m.desconocido(es.atributos[atributo], elegido.poi.nombre))
    }
    reloj += estancia
    desdeDescanso += estancia
    usados.add(elegido.poi.poi_id)
    posicion = elegido.poi
  }
  return { paradas, usados, desconocidos }
}

function alternativosDe(candidatos: Candidato[], usados: Set<string>, referencia: POIResumen[], cuantos: number): POIResumen[] {
  if (referencia.length === 0) return []
  const destinos = new Set(referencia.map((poi) => poi.destino_id))
  const centro = {
    lat: referencia.reduce((suma, poi) => suma + poi.lat, 0) / referencia.length,
    lon: referencia.reduce((suma, poi) => suma + poi.lon, 0) / referencia.length,
  }
  return candidatos
    .filter((candidato) => !usados.has(candidato.poi.poi_id))
    .sort((x, y) => {
      const otroX = destinos.has(x.poi.destino_id) ? 1 : 0
      const otroY = destinos.has(y.poi.destino_id) ? 1 : 0
      if (otroX !== otroY) return otroX - otroY
      return distanciaKm(centro, x.poi) - distanciaKm(centro, y.poi)
    })
    .slice(0, cuantos)
    .map((candidato) => candidato.poi)
}

let contador = 0

export function recomendar(solicitud: SolicitudRecomendacion): Itinerario {
  const intereses = solicitud.intereses ?? []
  const todos = POIS_DEMO.map(resumen)
  const { candidatos, noIncluidos } = clasificar(todos, solicitud.restricciones, solicitud.presupuesto, intereses)
  const minutos = Math.round(solicitud.horas_disponibles * 60)

  // Se planea en un solo destino: el del candidato mejor puntuado (o el más cercano al punto de partida).
  const ordenados = [...candidatos].sort((x, y) => {
    if (solicitud.punto_partida) {
      return distanciaKm(solicitud.punto_partida, x.poi) - distanciaKm(solicitud.punto_partida, y.poi)
    }
    return y.puntaje - x.puntaje
  })
  const destino = ordenados[0]?.poi.destino_id
  const delDestino = candidatos.filter((candidato) => candidato.poi.destino_id === destino)
  const { paradas, usados, desconocidos } = secuenciar(delDestino, minutos, intereses, solicitud.restricciones, solicitud.punto_partida)

  for (const candidato of delDestino) {
    if (!usados.has(candidato.poi.poi_id)) noIncluidos.push({ poi_id: candidato.poi.poi_id, motivo: m.noCabe })
  }

  const restricciones = solicitud.restricciones ?? {}
  const conRestricciones = Boolean(
    restricciones.sin_escalones || restricciones.banio_accesible || restricciones.pendiente_max_pct !== undefined,
  )
  const explicacion = [m.explicacion(paradas.length, solicitud.horas_disponibles), conRestricciones ? m.explicacionRestricciones : '']
    .filter(Boolean)
    .join(' ')

  contador += 1
  return {
    itinerario_id: `demo-${Date.now()}-${contador}`,
    paradas,
    no_incluidos: noIncluidos,
    alternativos: solicitud.incluir_alternativos
      ? alternativosDe(
          candidatos.filter((candidato) => candidato.poi.destino_id !== destino),
          usados,
          paradas.map((parada) => parada.poi),
          2,
        )
      : [],
    explicacion,
    datos_desconocidos: desconocidos,
  }
}

export function planearDesdeGuardados(solicitud: SolicitudDesdeGuardados): PlanMultidia {
  const todos = POIS_DEMO.map(resumen)
  const elegidos = solicitud.poi_ids
    .map((id) => todos.find((poi) => poi.poi_id === id))
    .filter((poi): poi is POIResumen => Boolean(poi))
  const { candidatos, noIncluidos } = clasificar(elegidos, solicitud.restricciones, undefined, [])
  for (const id of solicitud.poi_ids) {
    if (!todos.some((poi) => poi.poi_id === id)) noIncluidos.push({ poi_id: id, motivo: m.sinDatos })
  }

  // Agrupa por destino (los más numerosos primero) y llena los días en ese orden.
  const grupos = new Map<string, Candidato[]>()
  for (const candidato of candidatos) {
    const grupo = grupos.get(candidato.poi.destino_id) ?? []
    grupo.push(candidato)
    grupos.set(candidato.poi.destino_id, grupo)
  }
  let restantes = [...grupos.values()].sort((x, y) => y.length - x.length).flat()
  const minutos = Math.round(solicitud.horas_por_dia * 60)
  const dias: PlanMultidia['dias'] = []
  const usadosTotal = new Set<string>()

  for (let dia = 1; dia <= solicitud.dias && restantes.length > 0; dia++) {
    const destinoDelDia = restantes[0].poi.destino_id
    const delDia = restantes.filter((candidato) => candidato.poi.destino_id === destinoDelDia)
    const { paradas, usados } = secuenciar(delDia, minutos, [], solicitud.restricciones)
    // Si sobra tiempo, el día continúa con el siguiente destino más cercano.
    let reloj = paradas.reduce((suma, parada) => suma + parada.traslado_min + parada.estancia_min, 0)
    const resto = restantes.filter((candidato) => !usados.has(candidato.poi.poi_id) && candidato.poi.destino_id !== destinoDelDia)
    const ultimo = paradas[paradas.length - 1]?.poi
    if (ultimo && resto.length > 0) {
      const extra = secuenciar(resto, minutos - reloj, [], solicitud.restricciones, ultimo)
      for (const parada of extra.paradas) {
        paradas.push({ ...parada, orden: paradas.length + 1, llegada_min: parada.llegada_min + reloj })
      }
      extra.usados.forEach((id) => usados.add(id))
      reloj = paradas.reduce((suma, parada) => suma + parada.traslado_min + parada.estancia_min, 0)
    }
    if (paradas.length === 0) break
    dias.push({ dia, paradas })
    usados.forEach((id) => usadosTotal.add(id))
    restantes = restantes.filter((candidato) => !usados.has(candidato.poi.poi_id))
  }

  for (const candidato of restantes) noIncluidos.push({ poi_id: candidato.poi.poi_id, motivo: m.noCabe })

  const otros = clasificar(
    todos.filter((poi) => !solicitud.poi_ids.includes(poi.poi_id)),
    solicitud.restricciones,
    undefined,
    [],
  ).candidatos
  return {
    dias,
    no_incluidos: noIncluidos,
    alternativos: alternativosDe(otros, usadosTotal, dias.flatMap((dia) => dia.paradas.map((parada) => parada.poi)), 2),
  }
}
