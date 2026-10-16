// Contrato de la API (spec 014, docs/api/contrato-p0.md). JSON en snake_case. No renombrar
// campos aquí: si el contrato cambia, se cambia primero en la spec y después en este archivo.

export type EstadoAtributo = 'verificado' | 'sin_verificar' | 'reportado' | 'en_moderacion'

export const ATRIBUTOS_ACCESIBILIDAD = [
  'acceso_sin_escalones',
  'rampa',
  'banio_accesible',
  'elevador',
  'superficie',
  'asientos',
  'estacionamiento_reservado',
  'pendiente_pct',
  'numero_escalones',
] as const

export type AtributoAccesibilidad = (typeof ATRIBUTOS_ACCESIBILIDAD)[number]

/**
 * Binarios: `si`, `no` o `limitado`. `pendiente_pct` y `numero_escalones`: número en texto.
 * `superficie`: texto libre. Sin dato: `null` (estado `sin_verificar`).
 * Se toleran booleanos y números por robustez, pero el contrato usa texto.
 */
export type ValorAtributo = 'si' | 'no' | 'limitado' | string | number | boolean | null

export interface DatoAccesibilidad {
  valor: ValorAtributo
  estado: EstadoAtributo
  origen: string | null
  confianza: number | null
  fecha: string | null
}

export type Accesibilidad = Partial<Record<AtributoAccesibilidad, DatoAccesibilidad>>

export type CoberturaAccesibilidad = 'verificada' | 'parcial' | 'sin_verificar'

/** Escala de costo y de presupuesto (supuesto documentado en la spec 016). */
export type RangoCosto = 'gratis' | 'bajo' | 'medio' | 'alto'

export interface POIResumen {
  poi_id: string
  nombre: string
  categoria: string
  destino_id: string
  corredor_id: string | null
  lat: number
  lon: number
  costo_rango: RangoCosto | string | null
  accesibilidad: Accesibilidad
  cobertura_accesibilidad: CoberturaAccesibilidad
  is_synthetic: boolean
}

export interface Fuente {
  id: string
  nombre: string
  url: string | null
}

export type TipoBarrera =
  | 'escalones'
  | 'rampa_bloqueada'
  | 'sin_banio_accesible'
  | 'superficie'
  | 'senalizacion'
  | 'otro'

export const TIPOS_BARRERA: TipoBarrera[] = [
  'escalones',
  'rampa_bloqueada',
  'sin_banio_accesible',
  'superficie',
  'senalizacion',
  'otro',
]

export interface BarreraReportada {
  tipo: TipoBarrera | string
  /** `en_moderacion` o `aceptado`. */
  estado: string
  fecha: string
}

export interface POIDetalle extends POIResumen {
  descripcion: string | null
  direccion: string | null
  horario_osm: string | null
  fuentes: Fuente[]
  barreras_reportadas: BarreraReportada[]
}

export interface ListaPOI {
  items: POIResumen[]
  total: number
}

export interface FiltrosPOI {
  q?: string
  categoria?: string
  destino_id?: string
  corredor_id?: string
  costo_max?: RangoCosto
  sin_escalones?: boolean
  banio_accesible?: boolean
  solo_verificados?: boolean
  limit?: number
  offset?: number
}

export interface Destino {
  destino_id: string
  nombre: string
  pueblo_magico: boolean
  lat: number
  lon: number
  zona: string | null
}

export interface Restricciones {
  sin_escalones?: boolean
  banio_accesible?: boolean
  descansos_cada_min?: number
  pendiente_max_pct?: number
}

export interface SolicitudRecomendacion {
  horas_disponibles: number
  punto_partida?: { lat: number; lon: number }
  intereses?: string[]
  presupuesto?: RangoCosto
  restricciones?: Restricciones
  incluir_alternativos?: boolean
}

export interface Parada {
  orden: number
  poi: POIResumen
  llegada_min: number
  estancia_min: number
  traslado_min: number
  motivo: string
  advertencias: string[]
}

export interface NoIncluido {
  poi_id: string
  motivo: string
}

export interface Itinerario {
  itinerario_id: number | string
  paradas: Parada[]
  no_incluidos: NoIncluido[]
  alternativos: POIResumen[]
  explicacion: string
  datos_desconocidos: string[]
}

export interface SolicitudDesdeGuardados {
  poi_ids: string[]
  dias: number
  horas_por_dia: number
  restricciones?: Restricciones
}

export interface DiaPlan {
  dia: number
  paradas: Parada[]
}

export interface PlanMultidia {
  itinerario_id?: number | string
  dias: DiaPlan[]
  no_incluidos: NoIncluido[]
  alternativos: POIResumen[]
}

/** Cada dimensión es un entero de 1 a 5. Solo `global` es obligatoria. */
export interface DimensionesResena {
  accesibilidad?: number
  limpieza?: number
  servicio?: number
  precio_percibido?: number
  senalizacion?: number
  comodidad?: number
  inclusion?: number
  global: number
}

export type DimensionResena = keyof DimensionesResena

export const DIMENSIONES_RESENA: DimensionResena[] = [
  'global',
  'accesibilidad',
  'limpieza',
  'servicio',
  'precio_percibido',
  'senalizacion',
  'comodidad',
  'inclusion',
]

export interface SolicitudResena {
  poi_id: string
  dimensiones: DimensionesResena
  texto?: string
}

export interface SolicitudBarrera {
  poi_id: string
  tipo: TipoBarrera
  descripcion?: string
  /** JPEG, PNG o WebP en base64 (con o sin prefijo `data:`), máximo 5 MB. El servidor quita los metadatos. */
  foto?: string
}

export interface Credenciales {
  correo: string
  contrasena: string
}

export interface SolicitudRegistro extends Credenciales {
  nombre_visible?: string
}

export interface Usuario {
  id: string
  correo: string
  rol: 'visitante' | 'viewer' | 'analista' | 'admin'
  nombre_visible: string | null
}

export interface RespuestaToken {
  access_token: string
  token_type: string
  usuario: Usuario
}

export interface LugarGuardado {
  id: number
  poi_id: string | null
  nombre_propio: string | null
  nota: string | null
  url_origen: string | null
  plataforma_origen: string | null
  creado_en: string
  poi: POIResumen | null
}

export interface SolicitudGuardado {
  poi_id?: string
  nombre_propio?: string
  nota?: string
  url_origen?: string
  plataforma_origen?: string
}

export interface ElementoLista {
  id: number
  saved_place_id: number | null
  poi_id: string | null
}

export interface ListaGuardados {
  id: number
  nombre: string
  etiquetas: string[]
  items: ElementoLista[]
}

/** Resultado de un envío: `local` significa que quedó solo en este dispositivo. */
export interface ResultadoEnvio {
  destino: 'servidor' | 'local'
  /** Por qué quedó en local: modo de demostración o falta iniciar sesión. */
  motivo?: 'demo' | 'sin_sesion'
}

