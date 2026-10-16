import { Link } from 'react-router'
import type { POIResumen } from '../api/tipos'
import { guardarPoi, quitarPoi, useAlmacen } from '../almacen/almacen'
import { textoCategoria, textoCosto } from '../dominio/formato'
import { useTextos } from '../i18n/textos'
import { PastillaCobertura, PastillaSintetica } from './Estados'
import { Icono, IconoCategoria } from './Icono'

interface PropsGuardar {
  poi: POIResumen
  completo?: boolean
}

/**
 * «Guardar en mi mapa». El nombre accesible empieza con el texto visible
 * y dice qué hará el siguiente clic.
 */
export function BotonGuardar({ poi, completo = false }: PropsGuardar) {
  const t = useTextos()
  const { guardados } = useAlmacen()
  const guardado = Boolean(guardados[poi.poi_id])
  const visible = completo ? (guardado ? t.ficha.guardado : t.ficha.guardar) : guardado ? t.tarjeta.guardado : t.tarjeta.guardar
  const oculto = completo
    ? guardado
      ? `. ${t.ficha.quitar}`
      : ''
    : guardado
      ? `. ${t.tarjeta.quitarDe(poi.nombre)}`
      : ` ${t.tarjeta.enMiMapa(poi.nombre)}`
  return (
    <button
      type="button"
      className={`boton ${guardado ? 'boton--activo' : 'boton--acento'} ${completo ? '' : 'boton--pequeno'}`}
      onClick={() => (guardado ? quitarPoi(poi.poi_id) : guardarPoi(poi))}
    >
      <Icono nombre={guardado ? 'guardado' : 'guardar'} className="boton__icono" />
      {visible}
      {oculto && <span className="visualmente-oculto">{oculto}</span>}
    </button>
  )
}

interface Props {
  poi: POIResumen
  destino: string
  nivel?: 2 | 3
}

export function TarjetaPoi({ poi, destino, nivel = 3 }: Props) {
  const t = useTextos()
  const Titulo = nivel === 2 ? 'h2' : 'h3'
  return (
    <article className="tarjeta-poi">
      <div className="tarjeta-poi__cabeza">
        <span className="icono-categoria">
          <IconoCategoria categoria={poi.categoria} />
        </span>
        <div>
          <Titulo className="tarjeta-poi__titulo">
            <Link to={`/lugar/${encodeURIComponent(poi.poi_id)}`}>{poi.nombre}</Link>
          </Titulo>
          <p className="tarjeta-poi__meta">
            {textoCategoria(t, poi.categoria)} · {destino}
          </p>
        </div>
      </div>
      <div className="tarjeta-poi__estados">
        <PastillaCobertura cobertura={poi.cobertura_accesibilidad} />
        {poi.is_synthetic && <PastillaSintetica />}
      </div>
      <div className="tarjeta-poi__pie">
        <span className="costo">{textoCosto(t, poi.costo_rango)}</span>
        <BotonGuardar poi={poi} />
      </div>
    </article>
  )
}
