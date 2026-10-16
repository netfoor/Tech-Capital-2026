import type { ReactNode } from 'react'
import { useModoDatos } from '../api/modo'
import { useAlmacen } from '../almacen/almacen'
import { useTextos } from '../i18n/textos'
import { Icono, type NombreIcono } from './Icono'

type Tono = 'info' | 'exito' | 'alerta' | 'error' | 'sintetico'

const ICONO_TONO: Record<Tono, NombreIcono> = {
  info: 'info',
  exito: 'verificado',
  alerta: 'reportado',
  error: 'reportado',
  sintetico: 'info',
}

export function Aviso({ tono = 'info', children, rol }: { tono?: Tono; children: ReactNode; rol?: 'status' | 'alert' }) {
  return (
    <div className={`aviso aviso--${tono}`} role={rol}>
      <Icono nombre={ICONO_TONO[tono]} className="aviso__icono" />
      <div>{children}</div>
    </div>
  )
}

/** Banda fija que se muestra siempre que la pantalla use datos sintéticos. */
export function BandaSintetica() {
  const modo = useModoDatos()
  const t = useTextos()
  if (modo.origen !== 'demo' && !modo.vioSinteticos) return null
  return (
    <div className="banda-sintetica" role="note" aria-label={t.sintetico.banda}>
      <div className="contenedor banda-sintetica__interior">
        <strong className="banda-sintetica__titulo">
          <Icono nombre="info" className="pastilla__icono" />
          {t.sintetico.banda}
        </strong>
        <span className="banda-sintetica__detalle">{t.sintetico.detalle}</span>
      </div>
    </div>
  )
}

export function AvisoAlmacenamiento() {
  const { disponible } = useAlmacen()
  const t = useTextos()
  if (disponible) return null
  return (
    <Aviso tono="alerta" rol="status">
      <p>{t.general.almacenamientoBloqueado}</p>
    </Aviso>
  )
}

export function Cargando({ texto }: { texto?: string }) {
  const t = useTextos()
  return (
    <p className="cargando" role="status">
      {texto ?? t.general.cargando}
    </p>
  )
}

export function ErrorCarga({ alReintentar }: { alReintentar: () => void }) {
  const t = useTextos()
  return (
    <Aviso tono="error" rol="alert">
      <p>{t.general.errorCarga}</p>
      <button type="button" className="boton boton--secundario boton--pequeno" onClick={alReintentar}>
        {t.general.reintentar}
      </button>
    </Aviso>
  )
}
