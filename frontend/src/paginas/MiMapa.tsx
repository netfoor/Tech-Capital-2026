import { useId, useMemo, useState, type FormEvent } from 'react'
import { Link } from 'react-router'
import { anotar, etiquetar, quitarEtiqueta, useAlmacen, type Guardado } from '../almacen/almacen'
import { Icono } from '../componentes/Icono'
import { Mapa, type PuntoMapa } from '../componentes/Mapa'
import { TarjetaPoi } from '../componentes/TarjetaPoi'
import { textoCategoria } from '../dominio/formato'
import { nombreDestino, useDestinos } from '../hooks/datos'
import { useTextos } from '../i18n/textos'

function EditorGuardado({ guardado }: { guardado: Guardado }) {
  const t = useTextos()
  const [nueva, setNueva] = useState('')
  const [nota, setNota] = useState(guardado.nota)
  const [avisoNota, setAvisoNota] = useState(false)
  const ids = { etiqueta: useId(), ayudaEtiqueta: useId(), nota: useId(), ayudaNota: useId() }
  const { poi } = guardado

  function agregar(evento: FormEvent) {
    evento.preventDefault()
    if (!nueva.trim()) return
    etiquetar(poi.poi_id, nueva)
    setNueva('')
  }

  return (
    <details className="editor-guardado">
      <summary>{t.miMapa.editar(poi.nombre)}</summary>
      <div className="pila">
        <form onSubmit={agregar} className="fila-campo">
          <div className="campo">
            <label className="campo__etiqueta" htmlFor={ids.etiqueta}>
              {t.miMapa.nuevaEtiqueta}
            </label>
            <input
              id={ids.etiqueta}
              className="control"
              value={nueva}
              maxLength={30}
              aria-describedby={ids.ayudaEtiqueta}
              onChange={(evento) => setNueva(evento.target.value)}
            />
          </div>
          <button type="submit" className="boton boton--secundario">
            <Icono nombre="mas" className="boton__icono" />
            {t.miMapa.agregarEtiqueta}
          </button>
        </form>
        <p className="campo__ayuda" id={ids.ayudaEtiqueta}>
          {t.miMapa.nuevaEtiquetaAyuda}
        </p>

        <form
          className="campo"
          onSubmit={(evento) => {
            evento.preventDefault()
            anotar(poi.poi_id, nota)
            setAvisoNota(true)
          }}
        >
          <label className="campo__etiqueta" htmlFor={ids.nota}>
            <Icono nombre="candado" className="pastilla__icono" /> {t.miMapa.nota}
          </label>
          <p className="campo__ayuda" id={ids.ayudaNota}>
            {t.miMapa.notaAyuda}
          </p>
          <textarea
            id={ids.nota}
            className="control"
            value={nota}
            maxLength={1000}
            aria-describedby={ids.ayudaNota}
            onChange={(evento) => {
              setNota(evento.target.value)
              setAvisoNota(false)
            }}
          />
          <div className="acciones">
            <button type="submit" className="boton boton--secundario">
              {t.miMapa.guardarNota}
            </button>
            <span role="status" className="texto-suave" style={{ alignSelf: 'center' }}>
              {avisoNota ? t.miMapa.notaGuardada : ''}
            </span>
          </div>
        </form>
      </div>
    </details>
  )
}

function ElementoGuardado({ guardado, destino }: { guardado: Guardado; destino: string }) {
  const t = useTextos()
  return (
    <li className="guardado">
      <TarjetaPoi poi={guardado.poi} destino={destino} />
      {guardado.etiquetas.length > 0 && (
        <ul className="guardado__etiquetas" aria-label={t.miMapa.etiquetas}>
          {guardado.etiquetas.map((etiqueta) => (
            <li key={etiqueta} className="etiqueta-quitable">
              {etiqueta}
              <button type="button" aria-label={t.miMapa.quitarEtiqueta(etiqueta)} onClick={() => quitarEtiqueta(guardado.poi.poi_id, etiqueta)}>
                <Icono nombre="cerrar" className="pastilla__icono" />
              </button>
            </li>
          ))}
        </ul>
      )}
      {guardado.nota && (
        <p className="texto-suave" style={{ margin: 0 }}>
          <Icono nombre="candado" className="pastilla__icono" /> {guardado.nota}
        </p>
      )}
      <EditorGuardado guardado={guardado} />
    </li>
  )
}

export function MiMapa() {
  const t = useTextos()
  const { guardados, etiquetas } = useAlmacen()
  const destinos = useDestinos()
  const [filtro, setFiltro] = useState<string | null>(null)

  const lista = useMemo(
    () =>
      Object.values(guardados)
        .filter((guardado) => !filtro || guardado.etiquetas.includes(filtro))
        .sort((a, b) => a.poi.nombre.localeCompare(b.poi.nombre, 'es')),
    [guardados, filtro],
  )

  const grupos = useMemo(() => {
    const mapa = new Map<string, Guardado[]>()
    for (const guardado of lista) {
      const grupo = mapa.get(guardado.poi.destino_id) ?? []
      grupo.push(guardado)
      mapa.set(guardado.poi.destino_id, grupo)
    }
    return [...mapa.entries()].sort((a, b) => b[1].length - a[1].length)
  }, [lista])

  const puntos = useMemo<PuntoMapa[]>(
    () =>
      lista.map((guardado) => ({
        id: guardado.poi.poi_id,
        nombre: guardado.poi.nombre,
        detalle: textoCategoria(t, guardado.poi.categoria),
        lat: guardado.poi.lat,
        lon: guardado.poi.lon,
        ruta: `/lugar/${encodeURIComponent(guardado.poi.poi_id)}`,
        resaltado: true,
      })),
    [lista, t],
  )

  const total = Object.keys(guardados).length
  const etiquetasEnUso = etiquetas.filter((etiqueta) => Object.values(guardados).some((g) => g.etiquetas.includes(etiqueta)))

  return (
    <>
      <header className="cabecera-pagina">
        <h1>{t.miMapa.titulo}</h1>
        <p className="cabecera-pagina__intro">{t.miMapa.intro}</p>
      </header>

      {total === 0 ? (
        <div className="vacio">
          <p>{t.miMapa.vacio}</p>
          <Link className="boton boton--principal" to="/">
            <Icono nombre="descubrir" className="boton__icono" />
            {t.miMapa.irADescubrir}
          </Link>
        </div>
      ) : (
        <>
          <div className="barra-resultados">
            {etiquetasEnUso.length > 0 ? (
              <div role="group" aria-label={t.miMapa.filtrarEtiqueta}>
                <ul className="chips">
                  <li>
                    <button type="button" className="chip" aria-pressed={filtro === null} onClick={() => setFiltro(null)}>
                      {t.miMapa.todas}
                    </button>
                  </li>
                  {etiquetasEnUso.map((etiqueta) => (
                    <li key={etiqueta}>
                      <button
                        type="button"
                        className="chip"
                        aria-pressed={filtro === etiqueta}
                        onClick={() => setFiltro(filtro === etiqueta ? null : etiqueta)}
                      >
                        {etiqueta}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <span />
            )}
            <Link className="boton boton--principal" to="/planear?modo=guardados">
              <Icono nombre="planear" className="boton__icono" />
              {t.miMapa.planear}
            </Link>
          </div>

          <div className="mi-mapa">
            <div>
              {grupos.map(([destinoId, grupo]) => (
                <section key={destinoId} className="grupo-destino" aria-labelledby={`grupo-${destinoId}`}>
                  <h2 id={`grupo-${destinoId}`} className="grupo-destino__titulo">
                    {nombreDestino(destinos, destinoId)} <span className="conteo">· {t.miMapa.lugares(grupo.length)}</span>
                  </h2>
                  <ul className="rejilla-poi">
                    {grupo.map((guardado) => (
                      <ElementoGuardado key={guardado.poi.poi_id} guardado={guardado} destino={nombreDestino(destinos, destinoId)} />
                    ))}
                  </ul>
                </section>
              ))}
            </div>
            <div className="mi-mapa__mapa">
              <Mapa puntos={puntos} />
            </div>
          </div>
        </>
      )}
    </>
  )
}
