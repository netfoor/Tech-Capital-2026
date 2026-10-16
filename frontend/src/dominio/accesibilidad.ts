import type {
  Accesibilidad,
  AtributoAccesibilidad,
  DatoAccesibilidad,
  POIResumen,
  RangoCosto,
  Restricciones,
} from '../api/tipos'
import { es } from '../i18n/es'

const r = es.reglas

/** Dato que se muestra cuando la fuente no trae el atributo. Nunca se asume «accesible». */
export const SIN_DATO: DatoAccesibilidad = {
  valor: null,
  estado: 'sin_verificar',
  origen: null,
  confianza: null,
  fecha: null,
}

/** Devuelve el dato del atributo; si falta o viene vacío, su estado es «sin verificar». */
export function datoDe(accesibilidad: Accesibilidad | undefined, atributo: AtributoAccesibilidad): DatoAccesibilidad {
  const dato = accesibilidad?.[atributo]
  if (!dato) return SIN_DATO
  if (dato.valor === null || dato.valor === undefined) {
    return { ...dato, valor: null, estado: dato.estado === 'reportado' ? 'reportado' : 'sin_verificar' }
  }
  return dato
}

/** Solo «si» es afirmativo. «limitado» no cumple una necesidad indispensable. */
export function esAfirmativo(valor: DatoAccesibilidad['valor']): boolean {
  if (valor === true) return true
  if (typeof valor === 'string') return ['si', 'sí', 'yes', 'true', 'designated'].includes(valor.trim().toLowerCase())
  return false
}

/** El contrato manda los números como texto («8», «0»). */
export function aNumero(valor: DatoAccesibilidad['valor']): number | null {
  if (typeof valor === 'number') return Number.isFinite(valor) ? valor : null
  if (typeof valor === 'string' && valor.trim() !== '') {
    const numero = Number(valor.replace(',', '.'))
    return Number.isFinite(numero) ? numero : null
  }
  return null
}

/**
 * Un atributo cumple una necesidad solo si su valor es afirmativo y no hay barrera
 * reportada. Con «solo verificados», además debe estar verificado.
 */
export function cumple(dato: DatoAccesibilidad, soloVerificados = false): boolean {
  if (!esAfirmativo(dato.valor)) return false
  if (dato.estado === 'reportado') return false
  if (soloVerificados && dato.estado !== 'verificado') return false
  return true
}

export function sinEscalones(poi: POIResumen, soloVerificados = false): boolean {
  const acceso = datoDe(poi.accesibilidad, 'acceso_sin_escalones')
  if (acceso.estado === 'reportado') return false
  if (cumple(acceso, soloVerificados)) return true
  const escalones = datoDe(poi.accesibilidad, 'numero_escalones')
  if (acceso.valor === null && aNumero(escalones.valor) === 0 && escalones.estado !== 'reportado') {
    return !soloVerificados || escalones.estado === 'verificado'
  }
  return false
}

export function banioAccesible(poi: POIResumen, soloVerificados = false): boolean {
  return cumple(datoDe(poi.accesibilidad, 'banio_accesible'), soloVerificados)
}

export const ORDEN_COSTO: RangoCosto[] = ['gratis', 'bajo', 'medio', 'alto']

export function rangoCosto(costo: POIResumen['costo_rango']): number | null {
  const indice = ORDEN_COSTO.indexOf(costo as RangoCosto)
  return indice === -1 ? null : indice
}

/** Cabe en el presupuesto. Un costo desconocido no cabe si el presupuesto es «gratis». */
export function cabeEnPresupuesto(poi: POIResumen, presupuesto: RangoCosto | undefined): boolean {
  if (!presupuesto) return true
  const costo = rangoCosto(poi.costo_rango)
  if (costo === null) return presupuesto !== 'gratis'
  return costo <= ORDEN_COSTO.indexOf(presupuesto)
}

export interface Evaluacion {
  cumple: boolean
  motivo?: string
  advertencias: string[]
  desconocidos: AtributoAccesibilidad[]
}

/**
 * Restricciones indispensables. Si falta el dato, el lugar se excluye (opción conservadora)
 * y se explica por qué. Si el dato existe pero no está verificado, se incluye con advertencia.
 */
export function evaluarRestricciones(poi: POIResumen, restricciones: Restricciones = {}): Evaluacion {
  const advertencias: string[] = []
  const desconocidos: AtributoAccesibilidad[] = []
  const rechazo = (motivo: string): Evaluacion => ({ cumple: false, motivo, advertencias, desconocidos })

  if (restricciones.sin_escalones) {
    const acceso = datoDe(poi.accesibilidad, 'acceso_sin_escalones')
    if (acceso.estado === 'reportado') return rechazo(r.barreraEscalones)
    if (!sinEscalones(poi)) {
      const escalones = datoDe(poi.accesibilidad, 'numero_escalones')
      return rechazo(acceso.valor === null && escalones.valor === null ? r.sinDatoEscalones : r.conEscalones)
    }
    if (acceso.estado !== 'verificado') {
      advertencias.push(r.escalonesSinVerificar)
      desconocidos.push('acceso_sin_escalones')
    }
  }

  if (restricciones.banio_accesible) {
    const banio = datoDe(poi.accesibilidad, 'banio_accesible')
    if (!banioAccesible(poi)) {
      if (banio.estado === 'reportado') return rechazo(r.banioReportado)
      return rechazo(banio.valor === null ? r.sinDatoBanio : r.sinBanio)
    }
    if (banio.estado !== 'verificado') {
      advertencias.push(r.banioSinVerificar)
      desconocidos.push('banio_accesible')
    }
  }

  if (restricciones.pendiente_max_pct !== undefined) {
    const pendiente = datoDe(poi.accesibilidad, 'pendiente_pct')
    const valor = aNumero(pendiente.valor)
    if (valor === null) return rechazo(r.sinDatoPendiente)
    if (pendiente.estado === 'reportado') return rechazo(r.pendienteAlta(valor, restricciones.pendiente_max_pct))
    if (valor > restricciones.pendiente_max_pct) {
      return rechazo(r.pendienteAlta(valor, restricciones.pendiente_max_pct))
    }
    if (pendiente.estado !== 'verificado') {
      advertencias.push(r.pendienteSinVerificar)
      desconocidos.push('pendiente_pct')
    }
  }

  if (restricciones.descansos_cada_min !== undefined) {
    const asientos = datoDe(poi.accesibilidad, 'asientos')
    if (!cumple(asientos)) {
      advertencias.push(asientos.valor === null ? r.sinDatoAsientos : r.sinAsientos)
      if (asientos.valor === null) desconocidos.push('asientos')
    }
  }

  return { cumple: true, advertencias, desconocidos }
}
