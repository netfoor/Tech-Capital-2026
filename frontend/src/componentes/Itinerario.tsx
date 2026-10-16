import { useId, useMemo, useState } from 'react'
import { Link } from 'react-router'
import type { Parada, POIResumen } from '../api/tipos'
import { guardarPlan } from '../almacen/almacen'
import { estanciaMin } from '../demo/motor'
import { textoCategoria } from '../dominio/formato'
import { agregarAlternativo, moverParada, quitarParada, totalParadas, type PlanEditable } from '../dominio/plan'
import { horaDesde } from '../dominio/tiempo'
import { nombreDestino, useDestinos } from '../hooks/datos'
import { useTextos } from '../i18n/textos'
import { Aviso } from './Avisos'
import { PastillaCobertura, PastillaSintetica } from './Estados'
import { Icono } from './Icono'
import { Mapa, type PuntoMapa } from './Mapa'
import { BotonGuardar } from './TarjetaPoi'

interface PropsParada {
  parada: Parada
  indice: number
  total: number
  horaInicio: string
  sugerido: boolean
  alMover: (delta: -1 | 1) => void
  alQuitar: () => void
}

function ParadaPlan({ parada, indice, total, horaInicio, sugerido, alMover, alQuitar }: PropsParada) {
  const t = useTextos()
  const destinos = useDestinos()
  const { poi } = parada
  return (
    <li className="parada">
      <span className="parada__hora" aria-hidden="true">
        {horaDesde(horaInicio, parada.llegada_min)}
      </span>
      <article className="parada__cuerpo">
        {parada.traslado_min > 0 && (
          <span className="parada__traslado">
            <Icono nombre="caminar" className="pastilla__icono" />
            {t.planear.traslado(parada.traslado_min)}
          </span>
        )}
        <h4 className="parada__titulo">
          <span className="visualmente-oculto">
            {t.planear.parada(parada.orden)}, {t.planear.llegada} {horaDesde(horaInicio, parada.llegada_min)}:{' '}
          </span>
          <Link to={`/lugar/${encodeURIComponent(poi.poi_id)}`}>{poi.nombre}</Link>
        </h4>
        <p className="tarjeta-poi__meta">
          {textoCategoria(t, poi.categoria)} · {nombreDestino(destinos, poi.destino_id)} · {t.planear.estancia}{' '}
          {t.general.minutos(parada.estancia_min)}
        </p>
        <div className="tarjeta-poi__estados">
          <PastillaCobertura cobertura={poi.cobertura_accesibilidad} />
          {sugerido && <span className="pastilla pastilla--sugerencia">{t.planear.sugerencia}</span>}
          {poi.is_synthetic && <PastillaSintetica />}
        </div>
        <p className="parada__porque">
          <strong>{t.planear.porque}:</strong> {parada.motivo}
        </p>
        {parada.advertencias.length > 0 && (
          <ul className="parada__advertencias" aria-label={t.planear.advertencias}>
            {parada.advertencias.map((advertencia) => (
              <li key={advertencia}>
                <Icono nombre="reportado" className="pastilla__icono" />
                {advertencia}
              </li>
            ))}
          </ul>
        )}
        <div className="parada__acciones">
          <button type="button" className="boton boton--secundario boton--pequeno boton--icono" disabled={indice === 0} onClick={() => alMover(-1)} aria-label={t.planear.subir(poi.nombre)}>
            <Icono nombre="arriba" className="boton__icono" />
          </button>
          <button type="button" className="boton boton--secundario boton--pequeno boton--icono" disabled={indice === total - 1} onClick={() => alMover(1)} aria-label={t.planear.bajar(poi.nombre)}>
            <Icono nombre="abajo" className="boton__icono" />
          </button>
          <button type="button" className="boton boton--secundario boton--pequeno" onClick={alQuitar}>
            <Icono nombre="cerrar" className="boton__icono" />
            {t.general.quitar}
            <span className="visualmente-oculto"> {poi.nombre}</span>
          </button>
          <BotonGuardar poi={poi} />
        </div>
      </article>
    </li>
  )
}

interface Props {
  plan: PlanEditable
  conocidos: Record<string, POIResumen>
  alCambiar: (plan: PlanEditable) => void
}

export function Itinerario({ plan, conocidos, alCambiar }: Props) {
  const t = useTextos()
  const destinos = useDestinos()
  const [nombre, setNombre] = useState(plan.nombre)
  const [guardado, setGuardado] = useState(false)
  const idNombre = useId()
  const total = totalParadas(plan)

  const puntos = useMemo<PuntoMapa[]>(() => {
    let numero = 0
    return plan.dias.flatMap((dia) =>
      dia.paradas.map((parada) => {
        numero += 1
        return {
          id: `${dia.dia}-${parada.poi.poi_id}`,
          nombre: parada.poi.nombre,
          detalle: `${t.planear.dia(dia.dia)} · ${horaDesde(plan.hora_inicio, parada.llegada_min)}`,
          lat: parada.poi.lat,
          lon: parada.poi.lon,
          ruta: `/lugar/${encodeURIComponent(parada.poi.poi_id)}`,
          numero,
        }
      }),
    )
  }, [plan, t])

  function cambiar(nuevo: PlanEditable) {
    setGuardado(false)
    alCambiar(nuevo)
  }

  const multidia = plan.dias.length > 1

  return (
    <section className="itinerario" aria-labelledby="titulo-plan">
      <h2 id="titulo-plan">{t.planear.tuPlan}</h2>
      {plan.explicacion && <p className="explicacion">{plan.explicacion}</p>}

      {total === 0 ? (
        <Aviso tono="alerta">
          <p>{plan.dias.length === 0 ? t.planear.sinParadas : t.planear.planVacio}</p>
        </Aviso>
      ) : (
        <>
          <Mapa puntos={puntos} trazo />
          {plan.dias.map((dia) => {
            const ultima = dia.paradas[dia.paradas.length - 1]
            return (
              <section key={dia.dia} className="dia" aria-labelledby={`dia-${dia.dia}`}>
                <h3 id={`dia-${dia.dia}`}>{multidia ? t.planear.dia(dia.dia) : t.planear.paradas}</h3>
                {plan.editados.includes(dia.dia) && (
                  <p className="campo__ayuda">
                    <Icono nombre="info" className="pastilla__icono" /> {t.planear.trasladoEstimado}
                  </p>
                )}
                <ol className="paradas">
                  {dia.paradas.map((parada, indice) => (
                    <ParadaPlan
                      key={parada.poi.poi_id}
                      parada={parada}
                      indice={indice}
                      total={dia.paradas.length}
                      horaInicio={plan.hora_inicio}
                      sugerido={plan.sugeridos.includes(parada.poi.poi_id)}
                      alMover={(delta) => cambiar(moverParada(plan, dia.dia, indice, delta))}
                      alQuitar={() => cambiar(quitarParada(plan, dia.dia, indice))}
                    />
                  ))}
                </ol>
                {ultima && (
                  <p className="texto-suave">
                    {t.planear.fin}: {horaDesde(plan.hora_inicio, ultima.llegada_min + ultima.estancia_min)}
                  </p>
                )}
              </section>
            )
          })}
        </>
      )}

      <section className="panel panel--alto" aria-labelledby="titulo-desconocidos">
        <h3 id="titulo-desconocidos" className="seccion__titulo">
          <Icono nombre="sinVerificar" className="nav__icono" />
          {t.planear.desconocidos}
        </h3>
        {plan.datos_desconocidos.length === 0 ? (
          <p>{t.planear.sinDesconocidos}</p>
        ) : (
          <ul>
            {plan.datos_desconocidos.map((dato) => (
              <li key={dato}>{dato}</li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="titulo-no-incluidos">
        <h3 id="titulo-no-incluidos">{t.planear.noIncluidos}</h3>
        {plan.no_incluidos.length === 0 ? (
          <p className="texto-suave">{t.planear.sinNoIncluidos}</p>
        ) : (
          <ul className="lista-motivos">
            {plan.no_incluidos.map((elemento) => (
              <li key={elemento.poi_id}>
                <strong>
                  {conocidos[elemento.poi_id] ? (
                    <Link to={`/lugar/${encodeURIComponent(elemento.poi_id)}`}>{conocidos[elemento.poi_id].nombre}</Link>
                  ) : (
                    elemento.poi_id
                  )}
                </strong>
                {elemento.motivo}
              </li>
            ))}
          </ul>
        )}
      </section>

      {plan.alternativos.length > 0 && (
        <section aria-labelledby="titulo-alternativos">
          <h3 id="titulo-alternativos">{t.planear.alternativosTitulo}</h3>
          <ul className="rejilla-poi">
            {plan.alternativos.map((poi) => (
              <li key={poi.poi_id}>
                <article className="tarjeta-poi alternativo">
                  <span className="pastilla pastilla--sugerencia" style={{ justifySelf: 'start', width: 'fit-content' }}>
                    {t.planear.sugerencia}
                  </span>
                  <h4 className="tarjeta-poi__titulo">
                    <Link to={`/lugar/${encodeURIComponent(poi.poi_id)}`}>{poi.nombre}</Link>
                  </h4>
                  <p className="tarjeta-poi__meta">
                    {textoCategoria(t, poi.categoria)} · {nombreDestino(destinos, poi.destino_id)}
                  </p>
                  <div className="tarjeta-poi__estados">
                    <PastillaCobertura cobertura={poi.cobertura_accesibilidad} />
                    {poi.is_synthetic && <PastillaSintetica />}
                  </div>
                  <div className="tarjeta-poi__pie">
                    <button
                      type="button"
                      className="boton boton--secundario boton--pequeno"
                      onClick={() => cambiar(agregarAlternativo(plan, poi, estanciaMin(poi), t.planear.sugerencia + '.'))}
                    >
                      <Icono nombre="mas" className="boton__icono" />
                      {t.planear.agregarAlternativo(poi.nombre)}
                    </button>
                  </div>
                </article>
              </li>
            ))}
          </ul>
        </section>
      )}

      {total > 0 && (
        <form
          className="panel fila-campo"
          onSubmit={(evento) => {
            evento.preventDefault()
            const nuevo = guardarPlan({ ...plan, nombre: nombre.trim() || plan.nombre })
            alCambiar({ ...plan, id: nuevo.id, nombre: nuevo.nombre })
            setGuardado(true)
          }}
        >
          <div className="campo">
            <label className="campo__etiqueta" htmlFor={idNombre}>
              {t.planear.nombrePlan}
            </label>
            <input id={idNombre} className="control" value={nombre} maxLength={60} onChange={(evento) => setNombre(evento.target.value)} />
          </div>
          <button type="submit" className="boton boton--principal">
            <Icono nombre="guardar" className="boton__icono" />
            {t.planear.guardarPlan}
          </button>
        </form>
      )}
      <p role="status" className="texto-suave">
        {guardado ? t.planear.planGuardado : ''}
      </p>
    </section>
  )
}
