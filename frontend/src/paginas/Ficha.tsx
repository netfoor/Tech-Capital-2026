import { useMemo } from 'react'
import { Link, useParams } from 'react-router'
import { obtenerPoi } from '../api/cliente'
import { ATRIBUTOS_ACCESIBILIDAD, type POIDetalle } from '../api/tipos'
import { Cargando, ErrorCarga } from '../componentes/Avisos'
import { PastillaCobertura, PastillaEstado, PastillaSintetica } from '../componentes/Estados'
import { Icono, IconoCategoria } from '../componentes/Icono'
import { Mapa } from '../componentes/Mapa'
import { BotonGuardar } from '../componentes/TarjetaPoi'
import { datoDe } from '../dominio/accesibilidad'
import { textoCategoria, textoCosto, textoOrigen, textoValor } from '../dominio/formato'
import { fechaCorta, horarioLegible } from '../dominio/tiempo'
import { nombreDestino, useCarga, useDestinos } from '../hooks/datos'
import { useTextos } from '../i18n/textos'

function Accesibilidad({ poi }: { poi: POIDetalle }) {
  const t = useTextos()
  return (
    <section className="seccion" aria-labelledby="titulo-accesibilidad">
      <h2 id="titulo-accesibilidad" className="seccion__titulo">
        {t.ficha.accesibilidad}
      </h2>
      <p className="texto-suave">{t.ficha.accesibilidadIntro}</p>
      <ul className="lista-atributos">
        {ATRIBUTOS_ACCESIBILIDAD.map((atributo) => {
          const dato = datoDe(poi.accesibilidad, atributo)
          const origen = textoOrigen(t, dato)
          return (
            <li key={atributo} className="atributo">
              <span className="atributo__nombre">{t.atributos[atributo]}</span>
              <span className={`atributo__valor ${dato.valor === null ? 'atributo__valor--vacio' : ''}`}>
                <span className="visualmente-oculto">{t.ficha.valor}: </span>
                {textoValor(t, atributo, dato)}
              </span>
              <span className="atributo__estado">
                <span className="visualmente-oculto">{t.ficha.estado}: </span>
                <PastillaEstado estado={dato.estado} />
              </span>
              {origen && <span className="atributo__meta">{origen}</span>}
            </li>
          )
        })}
      </ul>
    </section>
  )
}

function Barreras({ poi }: { poi: POIDetalle }) {
  const t = useTextos()
  return (
    <section className="seccion" aria-labelledby="titulo-barreras">
      <h2 id="titulo-barreras">{t.ficha.barreras}</h2>
      {poi.barreras_reportadas.length === 0 ? (
        <p className="texto-suave">{t.ficha.sinBarreras}</p>
      ) : (
        <ul className="lista-simple">
          {poi.barreras_reportadas.map((barrera, indice) => (
            <li key={`${barrera.tipo}-${indice}`} className="aviso aviso--error">
              <Icono nombre="reportado" className="aviso__icono" />
              <div>
                <strong>{t.barreras[barrera.tipo as keyof typeof t.barreras] ?? barrera.tipo}</strong>
                <p className="texto-suave" style={{ margin: 0 }}>
                  {t.estadosBarrera[barrera.estado] ?? barrera.estado} · {fechaCorta(barrera.fecha)}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export function Ficha() {
  const t = useTextos()
  const { poiId = '' } = useParams()
  const destinos = useDestinos()
  const carga = useCarga(() => obtenerPoi(poiId), poiId)
  const poi = carga.datos

  const puntos = useMemo(
    () =>
      poi
        ? [{ id: poi.poi_id, nombre: poi.nombre, detalle: poi.direccion ?? '', lat: poi.lat, lon: poi.lon, ruta: `/lugar/${encodeURIComponent(poi.poi_id)}` }]
        : [],
    [poi],
  )

  if (carga.cargando && !poi) return <Cargando />
  if (carga.error) return <ErrorCarga alReintentar={carga.reintentar} />
  if (!poi) {
    return (
      <div className="vacio">
        <h1>{t.ficha.noEncontrado}</h1>
        <Link className="boton boton--principal" to="/">
          {t.ficha.irADescubrir}
        </Link>
      </div>
    )
  }

  const ruta = `/lugar/${encodeURIComponent(poi.poi_id)}`

  return (
    <article className="ficha">
      <div>
        <Link to="/" className="ruta-atras">
          <Icono nombre="atras" className="nav__icono" />
          {t.nav.descubrir}
        </Link>
        <header className="ficha__cabecera">
          <div className="tarjeta-poi__cabeza">
            <span className="icono-categoria">
              <IconoCategoria categoria={poi.categoria} />
            </span>
            <p className="tarjeta-poi__meta" style={{ alignSelf: 'center' }}>
              {textoCategoria(t, poi.categoria)} · {nombreDestino(destinos, poi.destino_id)}
            </p>
          </div>
          <h1 className="ficha__titulo">{poi.nombre}</h1>
          <div className="tarjeta-poi__estados">
            <PastillaCobertura cobertura={poi.cobertura_accesibilidad} />
            {poi.is_synthetic && <PastillaSintetica />}
          </div>
          <div className="acciones">
            <BotonGuardar poi={poi} completo />
            <Link className="boton boton--secundario" to={`${ruta}/reportar`}>
              <Icono nombre="bandera" className="boton__icono" />
              {t.ficha.reportar}
            </Link>
            <Link className="boton boton--secundario" to={`${ruta}/resena`}>
              <Icono nombre="estrella" className="boton__icono" />
              {t.ficha.resenar}
            </Link>
          </div>
        </header>

        <section className="seccion" aria-labelledby="titulo-descripcion">
          <h2 id="titulo-descripcion">{t.ficha.descripcion}</h2>
          <p>{poi.descripcion || t.ficha.sinDescripcion}</p>
        </section>

        <Accesibilidad poi={poi} />
        <Barreras poi={poi} />
      </div>

      <aside className="ficha__lateral" aria-label={t.ficha.datosPracticos}>
        <section className="panel" aria-labelledby="titulo-practicos">
          <h2 id="titulo-practicos">{t.ficha.datosPracticos}</h2>
          <dl className="lista-datos">
            <div>
              <dt>{t.ficha.horario}</dt>
              <dd>
                {poi.horario_osm ? (
                  <>
                    {horarioLegible(poi.horario_osm)}
                    <br />
                    <span className="campo__ayuda">{t.ficha.horarioFuente}</span>
                  </>
                ) : (
                  t.ficha.sinHorario
                )}
              </dd>
            </div>
            <div>
              <dt>{t.ficha.costo}</dt>
              <dd>{textoCosto(t, poi.costo_rango)}</dd>
            </div>
            {poi.direccion && (
              <div>
                <dt>{t.ficha.direccion}</dt>
                <dd>{poi.direccion}</dd>
              </div>
            )}
          </dl>
        </section>

        <section className="panel" aria-labelledby="titulo-ubicacion">
          <h2 id="titulo-ubicacion">{t.ficha.comoLlegar}</h2>
          <Mapa puntos={puntos} compacto />
        </section>

        <section className="panel" aria-labelledby="titulo-fuentes">
          <h2 id="titulo-fuentes">{t.ficha.fuentes}</h2>
          {poi.fuentes.length === 0 ? (
            <p className="texto-suave">{t.ficha.sinFuentes}</p>
          ) : (
            <ul className="lista-simple">
              {poi.fuentes.map((fuente) => (
                <li key={fuente.id}>
                  {fuente.url ? (
                    <a href={fuente.url} target="_blank" rel="noreferrer">
                      {fuente.nombre}
                    </a>
                  ) : (
                    fuente.nombre
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
      </aside>
    </article>
  )
}
