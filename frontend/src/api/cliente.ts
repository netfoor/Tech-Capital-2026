import { agregarEnvioLocal, iniciarSesionLocal, obtenerAlmacen } from '../almacen/almacen'
import * as demo from '../demo/motor'
import { marcarOrigen, marcarSinteticos, obtenerModo } from './modo'
import type {
  Credenciales,
  Destino,
  FiltrosPOI,
  Itinerario,
  ListaGuardados,
  ListaPOI,
  LugarGuardado,
  PlanMultidia,
  POIDetalle,
  RespuestaToken,
  ResultadoEnvio,
  SolicitudBarrera,
  SolicitudDesdeGuardados,
  SolicitudGuardado,
  SolicitudRecomendacion,
  SolicitudRegistro,
  SolicitudResena,
  Usuario,
} from './tipos'

const BASE = import.meta.env.VITE_API_URL ?? '/api'
const ESPERA_MS = 8000

/** Error de la API que sí debe verse (datos inválidos, sin sesión, no encontrado). */
export class ErrorApi extends Error {
  readonly estado: number
  readonly detalle: unknown
  constructor(estado: number, mensaje: string, detalle?: unknown) {
    super(mensaje)
    this.estado = estado
    this.detalle = detalle
  }
}

/** La API no respondió: sin red, sin servidor, ruta aún no implementada o error 5xx. */
class ApiNoDisponible extends Error {}

async function pedir<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  const control = new AbortController()
  const temporizador = setTimeout(() => control.abort(), ESPERA_MS)
  const token = obtenerAlmacen().sesion?.token
  let respuesta: Response
  try {
    respuesta = await fetch(`${BASE}${ruta}`, {
      ...opciones,
      signal: control.signal,
      headers: {
        Accept: 'application/json',
        ...(opciones.body ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    })
  } catch {
    throw new ApiNoDisponible(ruta)
  } finally {
    clearTimeout(temporizador)
  }
  const tipo = respuesta.headers.get('content-type') ?? ''
  if (respuesta.status >= 500) throw new ApiNoDisponible(ruta)
  if (respuesta.status === 204) return undefined as T
  if (!tipo.includes('json')) throw new ApiNoDisponible(ruta)
  const cuerpo: unknown = await respuesta.json().catch(() => null)
  if (!respuesta.ok) {
    const detalle = (cuerpo as { detail?: unknown } | null)?.detail
    // FastAPI responde «Not Found» cuando la ruta no existe: la API aún no tiene ese endpoint.
    if (respuesta.status === 404 && detalle === 'Not Found') throw new ApiNoDisponible(ruta)
    throw new ErrorApi(respuesta.status, typeof detalle === 'string' ? detalle : `Error ${respuesta.status}`, detalle)
  }
  return cuerpo as T
}

/** Intenta la API; si no responde, usa el modo de demostración y lo deja marcado. */
async function conRespaldo<T>(real: () => Promise<T>, local: () => T | Promise<T>): Promise<T> {
  if (obtenerModo().origen === 'demo') return local()
  try {
    const datos = await real()
    marcarOrigen('api')
    return datos
  } catch (error) {
    if (error instanceof ApiNoDisponible) {
      marcarOrigen('demo')
      return local()
    }
    throw error
  }
}

function aConsulta(filtros: FiltrosPOI): string {
  const parametros = new URLSearchParams()
  for (const [clave, valor] of Object.entries(filtros)) {
    if (valor === undefined || valor === '' || valor === false) continue
    parametros.set(clave, String(valor))
  }
  const texto = parametros.toString()
  return texto ? `?${texto}` : ''
}

function json(cuerpo: unknown, metodo = 'POST'): RequestInit {
  return { method: metodo, body: JSON.stringify(cuerpo) }
}

export async function obtener<T>(ruta: string): Promise<T> {
  return pedir<T>(ruta)
}

export async function listarPois(filtros: FiltrosPOI = {}): Promise<ListaPOI> {
  const lista = await conRespaldo(
    () => pedir<ListaPOI>(`/pois${aConsulta(filtros)}`),
    () => demo.listarPois(filtros),
  )
  marcarSinteticos(lista.items)
  return lista
}

export async function obtenerPoi(poiId: string): Promise<POIDetalle | null> {
  try {
    const poi = await conRespaldo(
      () => pedir<POIDetalle>(`/pois/${encodeURIComponent(poiId)}`),
      () => demo.obtenerPoi(poiId),
    )
    if (poi) marcarSinteticos([poi])
    return poi
  } catch (error) {
    if (error instanceof ErrorApi && error.estado === 404) return null
    throw error
  }
}

export async function listarDestinos(): Promise<Destino[]> {
  return conRespaldo(
    async () => {
      const respuesta = await pedir<{ items: Destino[] } | Destino[]>('/destinos')
      return Array.isArray(respuesta) ? respuesta : respuesta.items
    },
    () => demo.listarDestinos(),
  )
}

export async function recomendar(solicitud: SolicitudRecomendacion): Promise<Itinerario> {
  const itinerario = await conRespaldo(
    () => pedir<Itinerario>('/itineraries/recommend', json(solicitud)),
    () => demo.recomendar(solicitud),
  )
  marcarSinteticos(itinerario.paradas.map((parada) => parada.poi))
  return itinerario
}

export async function planearDesdeGuardados(solicitud: SolicitudDesdeGuardados): Promise<PlanMultidia> {
  const plan = await conRespaldo(
    () => pedir<PlanMultidia>('/itineraries/from-saved', json(solicitud)),
    () => demo.planearDesdeGuardados(solicitud),
  )
  marcarSinteticos(plan.dias.flatMap((dia) => dia.paradas.map((parada) => parada.poi)))
  return plan
}

/**
 * Envío que requiere cuenta. En modo de demostración o sin sesión, queda solo en el
 * dispositivo y se dice por qué; nunca se pierde en silencio.
 */
async function enviarConCuenta(tipo: 'resena' | 'barrera', ruta: string, cuerpo: object): Promise<ResultadoEnvio> {
  const local = (motivo: ResultadoEnvio['motivo']): ResultadoEnvio => {
    agregarEnvioLocal(tipo, cuerpo)
    return { destino: 'local', motivo }
  }
  if (obtenerModo().origen === 'demo') return local('demo')
  if (!obtenerAlmacen().sesion) return local('sin_sesion')
  try {
    await pedir<unknown>(ruta, json(cuerpo))
    marcarOrigen('api')
    return { destino: 'servidor' }
  } catch (error) {
    if (error instanceof ApiNoDisponible) {
      marcarOrigen('demo')
      return local('demo')
    }
    if (error instanceof ErrorApi && error.estado === 401) return local('sin_sesion')
    throw error
  }
}

export async function enviarResena(solicitud: SolicitudResena): Promise<ResultadoEnvio> {
  return enviarConCuenta('resena', '/reviews', solicitud)
}

export async function reportarBarrera(solicitud: SolicitudBarrera): Promise<ResultadoEnvio> {
  return enviarConCuenta('barrera', '/reports/barrier', solicitud)
}

/** Registro e inicio de sesión (opcionales: el MVP guarda los lugares en el dispositivo). */
export async function registrar(solicitud: SolicitudRegistro): Promise<RespuestaToken> {
  const respuesta = await pedir<RespuestaToken>('/auth/registro', json(solicitud))
  iniciarSesionLocal({ token: respuesta.access_token, usuario: respuesta.usuario })
  return respuesta
}

export async function iniciarSesion(credenciales: Credenciales): Promise<RespuestaToken> {
  const respuesta = await pedir<RespuestaToken>('/auth/login', json(credenciales))
  iniciarSesionLocal({ token: respuesta.access_token, usuario: respuesta.usuario })
  return respuesta
}

export async function obtenerUsuario(): Promise<Usuario> {
  return pedir<Usuario>('/me')
}

export async function guardarEnServidor(solicitud: SolicitudGuardado): Promise<LugarGuardado> {
  return pedir<LugarGuardado>('/saved-places', json(solicitud))
}

export async function listarGuardadosServidor(): Promise<{ items: LugarGuardado[]; total: number }> {
  return pedir('/saved-places')
}

export async function borrarGuardadoServidor(id: number): Promise<void> {
  await pedir<void>(`/saved-places/${id}`, { method: 'DELETE' })
}

export async function listarListas(): Promise<{ items: ListaGuardados[] }> {
  return pedir('/lists')
}

export async function crearLista(nombre: string, etiquetas: string[] = []): Promise<ListaGuardados> {
  return pedir<ListaGuardados>('/lists', json({ nombre, etiquetas }))
}
