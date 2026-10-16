import { useId, useMemo, useRef, useState, type FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router'
import { listarPois, planearDesdeGuardados, recomendar } from '../api/cliente'
import type { POIResumen, RangoCosto, Restricciones } from '../api/tipos'
import { borrarPlan, useAlmacen } from '../almacen/almacen'
import { Aviso, Cargando } from '../componentes/Avisos'
import { Icono } from '../componentes/Icono'
import { Itinerario } from '../componentes/Itinerario'
import { ORDEN_COSTO } from '../dominio/accesibilidad'
import { CATEGORIAS, textoCategoria } from '../dominio/formato'
import { desdeItinerario, desdeMultidia, totalParadas, type PlanEditable } from '../dominio/plan'
import { fechaCorta } from '../dominio/tiempo'
import { useCarga } from '../hooks/datos'
import { useTextos } from '../i18n/textos'

type Modo = 'cero' | 'guardados'

interface Necesidades {
  sinEscalones: boolean
  banio: boolean
  descansos: string
  pendiente: string
}

function aRestricciones(necesidades: Necesidades): Restricciones | undefined {
  const restricciones: Restricciones = {}
  if (necesidades.sinEscalones) restricciones.sin_escalones = true
  if (necesidades.banio) restricciones.banio_accesible = true
  if (necesidades.descansos) restricciones.descansos_cada_min = Number(necesidades.descansos)
  if (necesidades.pendiente) restricciones.pendiente_max_pct = Number(necesidades.pendiente)
  return Object.keys(restricciones).length ? restricciones : undefined
}

function CamposNecesidades({ valor, alCambiar }: { valor: Necesidades; alCambiar: (valor: Necesidades) => void }) {
  const t = useTextos()
  const ids = { ayuda: useId(), descansos: useId(), pendiente: useId() }
  return (
    <fieldset className="grupo" aria-describedby={ids.ayuda}>
      <legend className="grupo__leyenda">{t.planear.necesidades}</legend>
      <p className="campo__ayuda" id={ids.ayuda}>
        <Icono nombre="candado" className="pastilla__icono" /> {t.planear.necesidadesAyuda}
      </p>
      <label className="casilla">
        <input type="checkbox" checked={valor.sinEscalones} onChange={(e) => alCambiar({ ...valor, sinEscalones: e.target.checked })} />
        <span className="casilla__texto">{t.planear.sinEscalones}</span>
      </label>
      <label className="casilla">
        <input type="checkbox" checked={valor.banio} onChange={(e) => alCambiar({ ...valor, banio: e.target.checked })} />
        <span className="casilla__texto">{t.planear.banioAccesible}</span>
      </label>
      <div className="rejilla-campos">
        <div className="campo">
          <label className="campo__etiqueta" htmlFor={ids.descansos}>
            {t.planear.descansos}
          </label>
          <select id={ids.descansos} className="control" value={valor.descansos} onChange={(e) => alCambiar({ ...valor, descansos: e.target.value })}>
            <option value="">{t.planear.sinDescansos}</option>
            {[30, 45, 60].map((minutos) => (
              <option key={minutos} value={minutos}>
                {t.planear.descansosCada(minutos)}
              </option>
            ))}
          </select>
        </div>
        <div className="campo">
          <label className="campo__etiqueta" htmlFor={ids.pendiente}>
            {t.planear.pendiente}
          </label>
          <select id={ids.pendiente} className="control" value={valor.pendiente} onChange={(e) => alCambiar({ ...valor, pendiente: e.target.value })}>
            <option value="">{t.planear.sinPendiente}</option>
            {[4, 6, 8, 12].map((pendiente) => (
              <option key={pendiente} value={pendiente}>
                {t.planear.pendienteMax(pendiente)}
              </option>
            ))}
          </select>
        </div>
      </div>
    </fieldset>
  )
}

function enRango(texto: string, minimo: number, maximo: number): number | null {
  const numero = Number(texto)
  return Number.isFinite(numero) && numero >= minimo && numero <= maximo ? numero : null
}

export function Planear() {
  const t = useTextos()
  const [parametros, setParametros] = useSearchParams()
  const modo: Modo = parametros.get('modo') === 'guardados' ? 'guardados' : 'cero'
  const { guardados, planes } = useAlmacen()
  const listaGuardados = useMemo(() => Object.values(guardados), [guardados])

  const [horas, setHoras] = useState('4')
  const [horaInicio, setHoraInicio] = useState('10:00')
  const [intereses, setIntereses] = useState<string[]>([])
  const [presupuesto, setPresupuesto] = useState<RangoCosto | ''>('')
  const [alternativos, setAlternativos] = useState(true)
  const [necesidades, setNecesidades] = useState<Necesidades>({ sinEscalones: false, banio: false, descansos: '', pendiente: '' })
  const [dias, setDias] = useState('2')
  const [horasDia, setHorasDia] = useState('5')
  const [seleccion, setSeleccion] = useState<string[] | null>(null)
  const elegidos = seleccion ?? listaGuardados.map((guardado) => guardado.poi.poi_id)

  const [errores, setErrores] = useState<Record<string, string>>({})
  const [calculando, setCalculando] = useState(false)
  const [fallo, setFallo] = useState(false)
  const [plan, setPlan] = useState<PlanEditable | null>(null)
  const [generacion, setGeneracion] = useState(0)
  const resultado = useRef<HTMLDivElement>(null)
  const refs = { horas: useRef<HTMLInputElement>(null), dias: useRef<HTMLInputElement>(null), horasDia: useRef<HTMLInputElement>(null), guardados: useRef<HTMLInputElement>(null) }
  const ids = {
    horas: useId(),
    horaInicio: useId(),
    presupuesto: useId(),
    dias: useId(),
    horasDia: useId(),
    errorHoras: useId(),
    errorDias: useId(),
    errorHorasDia: useId(),
    errorGuardados: useId(),
  }

  // Nombres de los lugares que aparecen en «no incluidos».
  const catalogo = useCarga(() => listarPois({ limit: 200 }), 'catalogo-plan')
  const conocidos = useMemo(() => {
    const mapa: Record<string, POIResumen> = {}
    catalogo.datos?.items.forEach((poi) => (mapa[poi.poi_id] = poi))
    listaGuardados.forEach((guardado) => (mapa[guardado.poi.poi_id] = guardado.poi))
    return mapa
  }, [catalogo.datos, listaGuardados])

  function cambiarModo(nuevo: Modo) {
    setErrores({})
    setParametros(nuevo === 'guardados' ? { modo: 'guardados' } : {}, { replace: true })
  }

  function mostrar(nuevo: PlanEditable) {
    setPlan(nuevo)
    setGeneracion((n) => n + 1)
    requestAnimationFrame(() => resultado.current?.focus())
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    const nuevos: Record<string, string> = {}
    let primero: HTMLInputElement | null = null
    if (modo === 'cero') {
      if (enRango(horas, 1, 12) === null) {
        nuevos.horas = t.planear.errorHoras
        primero = refs.horas.current
      }
    } else {
      if (elegidos.length === 0) {
        nuevos.guardados = t.planear.errorGuardados
        primero = refs.guardados.current
      }
      if (enRango(dias, 1, 7) === null) {
        nuevos.dias = t.planear.errorDias
        primero ??= refs.dias.current
      }
      if (enRango(horasDia, 1, 12) === null) {
        nuevos.horasDia = t.planear.errorHoras
        primero ??= refs.horasDia.current
      }
    }
    setErrores(nuevos)
    if (Object.keys(nuevos).length > 0) {
      primero?.focus()
      return
    }

    setCalculando(true)
    setFallo(false)
    try {
      const restricciones = aRestricciones(necesidades)
      if (modo === 'cero') {
        const itinerario = await recomendar({
          horas_disponibles: Number(horas),
          ...(intereses.length ? { intereses } : {}),
          ...(presupuesto ? { presupuesto } : {}),
          ...(restricciones ? { restricciones } : {}),
          incluir_alternativos: alternativos,
        })
        mostrar(desdeItinerario(itinerario, horaInicio, t.planear.nombrePorDefecto))
      } else {
        const multidia = await planearDesdeGuardados({
          poi_ids: elegidos,
          dias: Number(dias),
          horas_por_dia: Number(horasDia),
          ...(restricciones ? { restricciones } : {}),
        })
        const lugares = multidia.dias.reduce((suma, dia) => suma + dia.paradas.length, 0)
        mostrar(desdeMultidia(multidia, horaInicio, t.planear.nombrePorDefecto, t.planear.explicacionGuardados(multidia.dias.length, lugares)))
      }
    } catch {
      setFallo(true)
    } finally {
      setCalculando(false)
    }
  }

  const error = (clave: string, id: string) =>
    errores[clave] ? (
      <p className="campo__error" id={id}>
        <Icono nombre="reportado" className="pastilla__icono" />
        {errores[clave]}
      </p>
    ) : null

  return (
    <>
      <header className="cabecera-pagina">
        <h1>{t.planear.titulo}</h1>
        <p className="cabecera-pagina__intro">{t.planear.intro}</p>
      </header>

      <div className="planear">
        <div className="pila-grande">
          <form className="panel formulario" noValidate onSubmit={enviar} aria-label={t.planear.titulo}>
            <div className="segmentado" role="group" aria-label={t.planear.modo} style={{ justifySelf: 'start' }}>
              <button type="button" aria-pressed={modo === 'cero'} onClick={() => cambiarModo('cero')}>
                {t.planear.desdeCero}
              </button>
              <button type="button" aria-pressed={modo === 'guardados'} onClick={() => cambiarModo('guardados')}>
                {t.planear.desdeGuardados}
              </button>
            </div>

            {Object.keys(errores).length > 0 && (
              <div className="resumen-errores" role="alert">
                <h2>{t.reportar.resumenErrores}</h2>
                <ul>
                  {Object.values(errores).map((mensaje) => (
                    <li key={mensaje}>{mensaje}</li>
                  ))}
                </ul>
              </div>
            )}

            {modo === 'cero' ? (
              <>
                <div className="rejilla-campos">
                  <div className="campo">
                    <label className="campo__etiqueta" htmlFor={ids.horas}>
                      {t.planear.horas}
                    </label>
                    {error('horas', ids.errorHoras)}
                    <input
                      id={ids.horas}
                      ref={refs.horas}
                      className="control"
                      type="number"
                      inputMode="numeric"
                      min={1}
                      max={12}
                      value={horas}
                      aria-invalid={errores.horas ? true : undefined}
                      aria-describedby={errores.horas ? ids.errorHoras : undefined}
                      onChange={(e) => setHoras(e.target.value)}
                    />
                  </div>
                  <div className="campo">
                    <label className="campo__etiqueta" htmlFor={ids.horaInicio}>
                      {t.planear.horaInicio}
                    </label>
                    <input id={ids.horaInicio} className="control" type="time" value={horaInicio} onChange={(e) => setHoraInicio(e.target.value || '10:00')} />
                  </div>
                </div>

                <fieldset className="grupo">
                  <legend className="grupo__leyenda">{t.planear.intereses}</legend>
                  <ul className="chips">
                    {CATEGORIAS.map((categoria) => {
                      const activo = intereses.includes(categoria)
                      return (
                        <li key={categoria}>
                          <button
                            type="button"
                            className="chip"
                            aria-pressed={activo}
                            onClick={() => setIntereses(activo ? intereses.filter((i) => i !== categoria) : [...intereses, categoria])}
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
                  <label className="campo__etiqueta" htmlFor={ids.presupuesto}>
                    {t.planear.presupuesto}
                  </label>
                  <select id={ids.presupuesto} className="control" value={presupuesto} onChange={(e) => setPresupuesto(e.target.value as RangoCosto | '')}>
                    <option value="">{t.planear.cualquierPresupuesto}</option>
                    {ORDEN_COSTO.map((costo) => (
                      <option key={costo} value={costo}>
                        {t.costos[costo]}
                      </option>
                    ))}
                  </select>
                </div>
              </>
            ) : (
              <>
                <fieldset
                  className="grupo"
                  aria-describedby={errores.guardados ? ids.errorGuardados : undefined}
                >
                  <legend className="grupo__leyenda">{t.planear.elegirGuardados}</legend>
                  {error('guardados', ids.errorGuardados)}
                  {listaGuardados.length === 0 ? (
                    <Aviso tono="info">
                      <p>{t.planear.sinGuardados}</p>
                      <Link to="/">{t.miMapa.irADescubrir}</Link>
                    </Aviso>
                  ) : (
                    <div className="selector-guardados">
                      {listaGuardados.map((guardado, indice) => (
                        <label key={guardado.poi.poi_id} className="casilla">
                          <input
                            ref={indice === 0 ? refs.guardados : undefined}
                            type="checkbox"
                            checked={elegidos.includes(guardado.poi.poi_id)}
                            onChange={(e) =>
                              setSeleccion(
                                e.target.checked
                                  ? [...elegidos, guardado.poi.poi_id]
                                  : elegidos.filter((id) => id !== guardado.poi.poi_id),
                              )
                            }
                          />
                          <span className="casilla__texto">{guardado.poi.nombre}</span>
                        </label>
                      ))}
                    </div>
                  )}
                </fieldset>

                <div className="rejilla-campos">
                  <div className="campo">
                    <label className="campo__etiqueta" htmlFor={ids.dias}>
                      {t.planear.dias}
                    </label>
                    {error('dias', ids.errorDias)}
                    <input
                      id={ids.dias}
                      ref={refs.dias}
                      className="control"
                      type="number"
                      inputMode="numeric"
                      min={1}
                      max={7}
                      value={dias}
                      aria-invalid={errores.dias ? true : undefined}
                      aria-describedby={errores.dias ? ids.errorDias : undefined}
                      onChange={(e) => setDias(e.target.value)}
                    />
                  </div>
                  <div className="campo">
                    <label className="campo__etiqueta" htmlFor={ids.horasDia}>
                      {t.planear.horasPorDia}
                    </label>
                    {error('horasDia', ids.errorHorasDia)}
                    <input
                      id={ids.horasDia}
                      ref={refs.horasDia}
                      className="control"
                      type="number"
                      inputMode="numeric"
                      min={1}
                      max={12}
                      value={horasDia}
                      aria-invalid={errores.horasDia ? true : undefined}
                      aria-describedby={errores.horasDia ? ids.errorHorasDia : undefined}
                      onChange={(e) => setHorasDia(e.target.value)}
                    />
                  </div>
                  <div className="campo">
                    <label className="campo__etiqueta" htmlFor={ids.horaInicio}>
                      {t.planear.horaInicio}
                    </label>
                    <input id={ids.horaInicio} className="control" type="time" value={horaInicio} onChange={(e) => setHoraInicio(e.target.value || '10:00')} />
                  </div>
                </div>
              </>
            )}

            <CamposNecesidades valor={necesidades} alCambiar={setNecesidades} />

            {modo === 'cero' && (
              <label className="casilla">
                <input type="checkbox" checked={alternativos} onChange={(e) => setAlternativos(e.target.checked)} />
                <span className="casilla__texto">{t.planear.alternativos}</span>
              </label>
            )}

            {fallo && (
              <Aviso tono="error" rol="alert">
                <p>{t.planear.error}</p>
              </Aviso>
            )}

            <button type="submit" className="boton boton--principal" disabled={calculando}>
              <Icono nombre="planear" className="boton__icono" />
              {calculando ? t.planear.calculando : t.planear.pedirPlan}
            </button>
          </form>

          <section className="panel" aria-labelledby="titulo-mis-planes">
            <h2 id="titulo-mis-planes">{t.planear.misPlanes}</h2>
            {planes.length === 0 ? (
              <p className="texto-suave">{t.planear.sinPlanes}</p>
            ) : (
              <ul className="lista-simple">
                {planes.map((guardado) => (
                  <li key={guardado.id} style={{ justifyContent: 'space-between' }}>
                    <span>
                      <strong>{guardado.nombre}</strong>
                      <br />
                      <span className="campo__ayuda">
                        {fechaCorta(guardado.creado_en)} · {totalParadas(guardado)} {t.planear.paradas.toLowerCase()}
                      </span>
                    </span>
                    <span className="acciones">
                      <button type="button" className="boton boton--secundario boton--pequeno" onClick={() => mostrar(guardado)}>
                        {t.planear.abrir}
                        <span className="visualmente-oculto"> {guardado.nombre}</span>
                      </button>
                      <button
                        type="button"
                        className="boton boton--peligro boton--pequeno"
                        aria-label={t.planear.borrarPlan(guardado.nombre)}
                        onClick={() => borrarPlan(guardado.id)}
                      >
                        {t.planear.borrar}
                      </button>
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>

        <div ref={resultado} tabIndex={-1} style={{ outline: "none" }}>
          {calculando && <Cargando texto={t.planear.calculando} />}
          {plan && !calculando && <Itinerario key={generacion} plan={plan} conocidos={conocidos} alCambiar={setPlan} />}
        </div>
      </div>
    </>
  )
}
