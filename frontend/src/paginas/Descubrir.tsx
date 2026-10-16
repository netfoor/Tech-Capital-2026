import { useEffect, useId, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router'
import { listarPois } from '../api/cliente'
import type { FiltrosPOI, RangoCosto } from '../api/tipos'
import { useAlmacen } from '../almacen/almacen'
import { Cargando, ErrorCarga } from '../componentes/Avisos'
import { Icono } from '../componentes/Icono'
import { Mapa, type PuntoMapa } from '../componentes/Mapa'
import { TarjetaPoi } from '../componentes/TarjetaPoi'
import { ORDEN_COSTO } from '../dominio/accesibilidad'
import { CATEGORIAS, textoCategoria } from '../dominio/formato'
import { nombreDestino, useCarga, useDestinos } from '../hooks/datos'
import { useTextos } from '../i18n/textos'



const BOOLEANOS = ['sin_escalones', 'banio_accesible', 'solo_verificados'] as const

function leerFiltros(parametros: URLSearchParams): FiltrosPOI {
  const filtros: FiltrosPOI = {}
  const q = parametros.get('q')
  if (q) filtros.q = q
  const categoria = parametros.get('categoria')
  if (categoria) filtros.categoria = categoria
  const destino = parametros.get('destino_id')
  if (destino) filtros.destino_id = destino
  const costo = parametros.get('costo_max')
  if (costo && ORDEN_COSTO.includes(costo as RangoCosto)) filtros.costo_max = costo as RangoCosto
  for (const clave of BOOLEANOS) if (parametros.get(clave) === 'true') filtros[clave] = true
  return filtros
}

function cuantosActivos(filtros: FiltrosPOI): number {
  return Object.entries(filtros).filter(([clave, valor]) => clave !== 'q' && valor !== undefined && valor !== false).length
}

function anchoAmplio(): boolean {
  return window.matchMedia?.('(min-width: 60rem)').matches ?? true
}

export function Descubrir() {
  const t = useTextos()
  const [parametros, setParametros] = useSearchParams()
  const filtros = useMemo(() => leerFiltros(parametros), [parametros])
  const vista = parametros.get('vista') === 'mapa' ? 'mapa' : 'lista'
  const destinos = useDestinos()
  const { guardados } = useAlmacen()
  const [busqueda, setBusqueda] = useState(filtros.q ?? '')
  const [abierto] = useState(anchoAmplio)
  const ids = { buscar: useId(), ayuda: useId(), destino: useId(), costo: useId() }

  const clave = JSON.stringify(filtros)
  const carga = useCarga(() => listarPois({ ...filtros, limit: 100 }), clave)

  function cambiar(cambios: Record<string, string | boolean | undefined>) {
    setParametros(
      (previos) => {
        const siguientes = new URLSearchParams(previos)
        for (const [nombre, valor] of Object.entries(cambios)) {
          if (valor === undefined || valor === '' || valor === false) siguientes.delete(nombre)
          else siguientes.set(nombre, String(valor))
        }
        return siguientes
      },
      { replace: true },
    )
  }

  useEffect(() => {
    const temporizador = setTimeout(() => {
      if ((filtros.q ?? '') !== busqueda.trim()) cambiar({ q: busqueda.trim() })
    }, 250)
    return () => clearTimeout(temporizador)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busqueda])

  const items = carga.datos?.items
  const puntos = useMemo<PuntoMapa[]>(
    () =>
      (items ?? []).map((poi) => ({
        id: poi.poi_id,
        nombre: poi.nombre,
        detalle: `${textoCategoria(t, poi.categoria)} · ${t.cobertura[poi.cobertura_accesibilidad] ?? ''}`,
        lat: poi.lat,
        lon: poi.lon,
        ruta: `/lugar/${encodeURIComponent(poi.poi_id)}`,
        resaltado: Boolean(guardados[poi.poi_id]),
      })),
    [items, t, guardados],
  )

  const activos = cuantosActivos(filtros)
  const listaDestinos = Object.values(destinos)

  return (
    <>
      <header className="cabecera-pagina">
        <h1>{t.descubrir.titulo}</h1>
        <p className="cabecera-pagina__intro">{t.descubrir.intro}</p>
      </header>

      <div className="descubrir">
        <details className="panel filtros" open={abierto}>
          <summary className="filtros__resumen">
            <Icono nombre="lista" className="nav__icono" />
            {t.descubrir.filtros}
            {activos > 0 && <span className="filtros__contador">{activos}</span>}
          </summary>
          <form className="filtros__cuerpo" role="search" onSubmit={(evento) => evento.preventDefault()}>
            <div className="campo">
              <label className="campo__etiqueta" htmlFor={ids.buscar}>
                {t.descubrir.buscar}
              </label>
              <input
                id={ids.buscar}
                className="control"
                type="search"
                value={busqueda}
                aria-describedby={ids.ayuda}
                onChange={(evento) => setBusqueda(evento.target.value)}
              />
              <p className="campo__ayuda" id={ids.ayuda}>
                {t.descubrir.buscarAyuda}
              </p>
            </div>

            <fieldset className="grupo">
              <legend className="grupo__leyenda">{t.descubrir.intereses}</legend>
              <ul className="chips">
                {CATEGORIAS.map((categoria) => {
                  const activo = filtros.categoria === categoria
                  return (
                    <li key={categoria}>
                      <button
                        type="button"
                        className="chip"
                        aria-pressed={activo}
                        onClick={() => cambiar({ categoria: activo ? undefined : categoria })}
                      >
                        {activo && <Icono nombre="verificado" className="chip__marca" />}
                        {textoCategoria(t, categoria)}
                      </button>
                    </li>
                  )
                })}
              </ul>
            </fieldset>

            <div className="campo">
              <label className="campo__etiqueta" htmlFor={ids.destino}>
                {t.descubrir.destino}
              </label>
              <select
                id={ids.destino}
                className="control"
                value={filtros.destino_id ?? ''}
                onChange={(evento) => cambiar({ destino_id: evento.target.value })}
              >
                <option value="">{t.descubrir.todosDestinos}</option>
                {listaDestinos.map((destino) => (
                  <option key={destino.destino_id} value={destino.destino_id}>
                    {destino.nombre}
                  </option>
                ))}
              </select>
            </div>

            <div className="campo">
              <label className="campo__etiqueta" htmlFor={ids.costo}>
                {t.descubrir.costo}
              </label>
              <select
                id={ids.costo}
                className="control"
                value={filtros.costo_max ?? ''}
                onChange={(evento) => cambiar({ costo_max: evento.target.value })}
              >
                <option value="">{t.descubrir.cualquierCosto}</option>
                {ORDEN_COSTO.map((costo) => (
                  <option key={costo} value={costo}>
                    {t.costos[costo]}
                  </option>
                ))}
              </select>
            </div>

            <fieldset className="grupo">
              <legend className="grupo__leyenda">{t.descubrir.accesibilidad}</legend>
              <label className="casilla">
                <input
                  type="checkbox"
                  checked={Boolean(filtros.sin_escalones)}
                  onChange={(evento) => cambiar({ sin_escalones: evento.target.checked })}
                />
                <span className="casilla__texto">{t.descubrir.sinEscalones}</span>
              </label>
              <label className="casilla">
                <input
                  type="checkbox"
                  checked={Boolean(filtros.banio_accesible)}
                  onChange={(evento) => cambiar({ banio_accesible: evento.target.checked })}
                />
                <span className="casilla__texto">{t.descubrir.banioAccesible}</span>
              </label>
              <label className="casilla">
                <input
                  type="checkbox"
                  checked={Boolean(filtros.solo_verificados)}
                  onChange={(evento) => cambiar({ solo_verificados: evento.target.checked })}
                />
                <span className="casilla__texto">
                  {t.descubrir.soloVerificados}
                  <span className="casilla__ayuda">{t.descubrir.soloVerificadosAyuda}</span>
                </span>
              </label>
            </fieldset>

            {(activos > 0 || filtros.q) && (
              <button
                type="button"
                className="boton boton--secundario"
                onClick={() => {
                  setBusqueda('')
                  setParametros(vista === 'mapa' ? { vista: 'mapa' } : {}, { replace: true })
                }}
              >
                {t.descubrir.limpiar}
              </button>
            )}
          </form>
        </details>

        <section aria-labelledby="titulo-resultados">
          <div className="barra-resultados">
            <h2 id="titulo-resultados">
              {t.descubrir.tituloResultados}{' '}
              {carga.datos && <span className="conteo">· {t.descubrir.resultados(carga.datos.total)}</span>}
            </h2>
            <div className="segmentado" role="group" aria-label={t.descubrir.vista}>
              <button type="button" aria-pressed={vista === 'lista'} onClick={() => cambiar({ vista: undefined })}>
                <Icono nombre="lista" className="pastilla__icono" />
                {t.descubrir.lista}
              </button>
              <button type="button" aria-pressed={vista === 'mapa'} onClick={() => cambiar({ vista: 'mapa' })}>
                <Icono nombre="miMapa" className="pastilla__icono" />
                {t.descubrir.mapa}
              </button>
            </div>
          </div>

          <p className="visualmente-oculto" role="status">
            {carga.datos ? t.descubrir.resultados(carga.datos.total) : ''}
          </p>

          {carga.cargando && !carga.datos && <Cargando />}
          {carga.error && <ErrorCarga alReintentar={carga.reintentar} />}
          {carga.datos && carga.datos.items.length === 0 && (
            <div className="vacio">
              <p>{t.descubrir.sinResultados}</p>
            </div>
          )}
          {carga.datos && carga.datos.items.length > 0 && vista === 'mapa' && (
            <div className="seccion">
              <Mapa puntos={puntos} />
            </div>
          )}
          {carga.datos && carga.datos.items.length > 0 && (
            <ul className="rejilla-poi" aria-label={t.descubrir.tituloResultados}>
              {carga.datos.items.map((poi) => (
                <li key={poi.poi_id}>
                  <TarjetaPoi poi={poi} destino={nombreDestino(destinos, poi.destino_id)} />
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </>
  )
}
