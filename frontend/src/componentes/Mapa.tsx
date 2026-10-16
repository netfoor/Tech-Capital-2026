import { Component, lazy, Suspense, type ReactNode } from 'react'
import { useTextos } from '../i18n/textos'

export interface PuntoMapa {
  id: string
  nombre: string
  detalle: string
  lat: number
  lon: number
  ruta: string
  resaltado?: boolean
  numero?: number
}

export interface PropsMapa {
  puntos: PuntoMapa[]
  compacto?: boolean
  /** Une los puntos en orden (itinerario). */
  trazo?: boolean
}

const MapaMapLibre = lazy(() => import('./MapaMapLibre'))

function hayWebGL(): boolean {
  try {
    const lienzo = document.createElement('canvas')
    return Boolean(window.WebGLRenderingContext && (lienzo.getContext('webgl2') || lienzo.getContext('webgl')))
  } catch {
    return false
  }
}

class LimiteError extends Component<{ respaldo: ReactNode; children: ReactNode }, { fallo: boolean }> {
  state = { fallo: false }
  static getDerivedStateFromError() {
    return { fallo: true }
  }
  render() {
    return this.state.fallo ? this.props.respaldo : this.props.children
  }
}

function Atribucion() {
  const t = useTextos()
  return (
    <p className="mapa__atribucion">
      <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">
        {t.mapa.atribucion}
      </a>
    </p>
  )
}

/**
 * Mapa equivalente a la lista. Se carga bajo demanda; si el dispositivo no puede
 * dibujarlo, avisa y remite a la lista, que tiene la misma información.
 */
export function Mapa(props: PropsMapa) {
  const t = useTextos()
  const respaldo = (
    <div className="aviso aviso--alerta" role="status">
      <p>{t.mapa.noDisponible}</p>
    </div>
  )
  return (
    <div className={`mapa ${props.compacto ? 'mapa--compacto' : ''}`}>
      {hayWebGL() ? (
        <LimiteError respaldo={respaldo}>
          <Suspense fallback={<div className="mapa__lienzo" aria-hidden="true" />}>
            <MapaMapLibre {...props} />
          </Suspense>
        </LimiteError>
      ) : (
        respaldo
      )}
      <Atribucion />
    </div>
  )
}
