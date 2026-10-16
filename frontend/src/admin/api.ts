// Cliente del tablero institucional (spec 019). El token vive en sessionStorage.
const BASE = import.meta.env.VITE_API_URL ?? '/api'
const LLAVE = 'pv360-tablero-token'

export type Usuario = { id: string; correo: string; rol: string; nombre_visible: string | null }
export type Sesion = { token: string; usuario: Usuario }

export class ErrorApi extends Error {
  estado: number
  constructor(estado: number, mensaje: string) {
    super(mensaje)
    this.estado = estado
  }
}

export function sesionGuardada(): Sesion | null {
  try {
    const texto = sessionStorage.getItem(LLAVE)
    return texto ? (JSON.parse(texto) as Sesion) : null
  } catch {
    return null
  }
}

export function guardarSesion(sesion: Sesion | null) {
  try {
    if (sesion) sessionStorage.setItem(LLAVE, JSON.stringify(sesion))
    else sessionStorage.removeItem(LLAVE)
  } catch {
    // Sin almacenamiento la sesión dura lo que la pestaña.
  }
}

async function pedir<T>(ruta: string, token: string | null, init: RequestInit = {}): Promise<T> {
  const respuesta = await fetch(`${BASE}${ruta}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init.headers ?? {}),
    },
  })
  if (!respuesta.ok) {
    let detalle = `Error ${respuesta.status}`
    try {
      const cuerpo = await respuesta.json()
      if (typeof cuerpo.detail === 'string') detalle = cuerpo.detail
    } catch {
      // Respuesta sin JSON.
    }
    throw new ErrorApi(respuesta.status, detalle)
  }
  return (await respuesta.json()) as T
}

export async function iniciarSesion(correo: string, contrasena: string): Promise<Sesion> {
  const r = await pedir<{ access_token: string; usuario: Usuario }>('/auth/login', null, {
    method: 'POST',
    body: JSON.stringify({ correo, contrasena }),
  })
  return { token: r.access_token, usuario: r.usuario }
}

export const obtener = <T>(ruta: string, token: string) => pedir<T>(ruta, token)

export const enviar = <T>(ruta: string, token: string, cuerpo: unknown) =>
  pedir<T>(ruta, token, { method: 'POST', body: JSON.stringify(cuerpo) })

export async function descargarCsv(ruta: string, token: string, nombre: string) {
  const separador = ruta.includes('?') ? '&' : '?'
  const respuesta = await fetch(`${BASE}${ruta}${separador}formato=csv`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!respuesta.ok) throw new ErrorApi(respuesta.status, `Error ${respuesta.status}`)
  const url = URL.createObjectURL(await respuesta.blob())
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = `${nombre}.csv`
  enlace.click()
  URL.revokeObjectURL(url)
}

// ---------------------------------------------------------------- Tipos de respuesta

export type Ficha = {
  metric_id: string
  nombre: string
  pregunta: string | null
  formula: string | null
  unidad: string | null
  denominador: string | null
  fuentes: string[]
  limitaciones: string | null
  procedencia: 'medido' | 'derivado' | null
  version: string | null
  k_minimo: number | null
  decision_potencial: string | null
}

export type Fuente = {
  fuente_id: string
  nombre: string
  institucion: string | null
  url: string | null
  fecha_consulta: string | null
  sha256: string | null
}

export type DestinoOferta = {
  destino_id: string | null
  centro_ot: string
  nombre: string
  ocupacion_pct: number | null
  cuartos_libres_dia: number | null
  estadia_noches: number | null
  llegadas: number
  afluencia_estimada: number | null
  meses_con_dato: number
  crecimiento_llegadas_pct: number | null
  crecimiento_motivo: string | null
  participacion_pct: number | null
  poi_catalogo: { real: number; sintetico: number }
  candidato: boolean
  serie_ocupacion: { periodo: string; ocupacion_pct: number | null }[]
}

export type OfertaDemanda = {
  modulo: 'oferta_demanda'
  is_synthetic: boolean
  ventana: { desde: string | null; hasta: string | null; meses: number }
  estado: { ocupacion_pct: number | null; cuartos_libres_dia: number | null; estadia_noches: number | null; origen: string }
  hhi: {
    ventana_12m: number | null
    centros: number
    cobertura_estado_pct: number | null
    serie_anual: { anio: number; hhi: number | null; meses: number; centros: number; parcial: boolean }[]
  }
  mediana_cuartos_libres_dia: number | null
  destinos: DestinoOferta[]
  candidatos: {
    destino_id: string | null
    nombre: string
    ocupacion_pct: number
    cuartos_libres_dia: number
    poi_catalogo: { real: number; sintetico: number }
    motivo: string
  }[]
  campos: { campo: string; metric_id: string; procedencia: string }[]
  fichas: Ficha[]
  fuentes: Fuente[]
  calculado_en: string
}

export type Brechas = {
  modulo: 'inclusion'
  k_minimo: number
  aviso: string
  resumen: {
    is_synthetic: boolean
    poi: number
    con_informacion_pct: number
    verificada_pct: number
    parcial_pct: number
    sin_verificar_pct: number
  }[]
  por_destino: {
    destino_id: string
    nombre: string
    is_synthetic: boolean
    poi: number
    con_informacion: number
    con_informacion_pct: number
    verificada: number
    verificada_pct: number
    parcial: number
    sin_verificar: number
  }[]
  por_atributo: {
    atributo: string
    is_synthetic: boolean
    poi: number
    con_valor: number
    con_valor_pct: number
    verificado: number
    verificado_pct: number
    reportado: number
    en_moderacion: number
    sin_verificar: number
    sin_dato: number
  }[]
  barreras: {
    is_synthetic: boolean
    suprimido: boolean
    personas: number | null
    casos: number | null
    abiertos: number | null
    aceptados: number | null
    rechazados: number | null
    tasa_aceptacion: number | null
    tiempo_moderacion_mediano_h: number | null
    por_tipo: { tipo: string; casos: number; aceptados: number }[] | null
  }[]
  prioridades: { tipo: string; is_synthetic: boolean; sugerencia: string }[]
  hay_sinteticos: boolean
  fichas: Ficha[]
  fuentes: Fuente[]
  calculado_en: string
}

export type GrupoPanorama = {
  destino_id: string
  nombre: string
  is_synthetic: boolean
  suprimido: boolean
  supresion_complementaria: boolean
  personas: number | null
  visitas_observadas: number | null
  confianza_media: number | null
  cobertura_poi_pct: number | null
  permanencia: {
    suprimido: boolean
    n: number | null
    p25_min: number | null
    mediana_min: number | null
    p75_min: number | null
  }
}

export type Panorama = {
  modulo: 'panorama'
  k_minimo: number
  aviso: string
  grupos: GrupoPanorama[]
  hay_reales: boolean
  hay_sinteticos: boolean
  fichas: Ficha[]
  fuentes: Fuente[]
  calculado_en: string
}

export type GrupoExperiencia = {
  destino_id: string | null
  nombre: string
  dimension: string
  is_synthetic: boolean
  suprimido: boolean
  personas: number | null
  n: number | null
  media: number | null
  media_ic95: [number, number] | null
  proporcion_baja: number | null
  proporcion_baja_ic95: [number, number] | null
}

export type Experiencia = {
  modulo: 'experiencia'
  k_minimo: number
  aviso: string
  grupos: GrupoExperiencia[]
  dimensiones: string[]
  hay_reales: boolean
  hay_sinteticos: boolean
  fichas: Ficha[]
  fuentes: Fuente[]
  calculado_en: string
}

export type CasoModeracion = {
  id: number
  poi_id: string
  tipo: string
  atributo: string | null
  estado: string
  descripcion: string | null
  creado_en: string
}
