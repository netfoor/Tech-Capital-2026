import { useState } from 'react'
import {
  descargarCsv,
  enviar,
  type Brechas,
  type CasoModeracion,
  type Experiencia as DatosExperiencia,
  type OfertaDemanda as DatosOferta,
  type Panorama as DatosPanorama,
} from './api'
import {
  BandaSintetica,
  BarrasH,
  Cargando,
  ErrorCarga,
  FichaMetodologica,
  Grafico,
  Kpi,
  Linea,
  Procedencia,
  TablaDatos,
} from './graficos'
import {
  ATRIBUTOS,
  DIMENSIONES,
  dosDec,
  entero,
  fecha,
  intervalo,
  pct,
  prop,
  TIPOS_BARRERA,
  uno,
} from './formato'
import { useDatos } from './useDatos'
import { useVista } from './vista'

type Props = { token: string; salir: () => void }

const SUPRIMIDO = 'Suprimido (n < k)'

function BotonCsv({ ruta, token, nombre }: { ruta: string; token: string; nombre: string }) {
  const [error, setError] = useState<string | null>(null)
  return (
    <>
      <button
        type="button"
        className="tb-boton-sec"
        onClick={() => descargarCsv(ruta, token, nombre).catch((e: Error) => setError(e.message))}
      >
        Exportar CSV con metadatos
      </button>
      {error ? <span role="alert">{error}</span> : null}
    </>
  )
}

function bloques<T extends { is_synthetic: boolean }>(filas: T[]) {
  return [false, true]
    .map((sintetico) => ({ sintetico, filas: filas.filter((f) => f.is_synthetic === sintetico) }))
    .filter((b) => b.filas.length)
}

function TituloBloque({ sintetico }: { sintetico: boolean }) {
  return sintetico ? (
    <BandaSintetica>conjunto separado; no se suma a los datos reales</BandaSintetica>
  ) : (
    <p className="tb-real">Datos reales</p>
  )
}

// ====================================================================== Oferta–demanda

export function OfertaDemanda({ token, salir }: Props) {
  const ruta = '/b2b/supply-demand'
  const { datos, error } = useDatos<DatosOferta>(ruta, token, salir)
  const vista = useVista()
  if (error) return <ErrorCarga mensaje={error} />
  if (!datos) return <Cargando que="la oferta y la demanda" />
  const ficha = (...ids: string[]) => datos.fichas.filter((f) => ids.includes(f.metric_id))
  const v = datos.ventana
  const ventana = `${v.desde} a ${v.hasta} (${v.meses} meses)`
  const porOcupacion = [...datos.destinos].sort((a, b) => (b.ocupacion_pct ?? 0) - (a.ocupacion_pct ?? 0))
  const anual = datos.hhi.serie_anual
  if (!datos.destinos.length)
    return <p role="status">Sin serie oficial cargada. Corre la semilla de datos para ver este módulo.</p>

  return (
    <div className="tb-modulo">
      <p className="tb-intro">
        Datos públicos reales del Observatorio Turístico de la Secretaría. Ventana: {ventana}. Este módulo no
        depende de usuarios de la app.
      </p>
      <dl className="tb-kpis">
        <Kpi
          etiqueta="Concentración de llegadas (HHI)"
          valor={entero(datos.hhi.ventana_12m)}
          detalle={`${datos.hhi.centros} centros; cubren ${pct(datos.hhi.cobertura_estado_pct)} de las llegadas del Estado`}
          procedencia="medido"
        />
        <Kpi
          etiqueta="Ocupación del Estado"
          valor={pct(datos.estado.ocupacion_pct)}
          detalle="ponderada por cuartos"
          procedencia="medido"
        />
        <Kpi
          etiqueta="Cuartos libres por día en el Estado"
          valor={entero(datos.estado.cuartos_libres_dia)}
          procedencia="medido"
        />
        <Kpi
          etiqueta="Candidatos a destino alternativo"
          valor={entero(datos.candidatos.length)}
          detalle="baja ocupación y oferta hotelera relevante"
        />
      </dl>

      <section className="tb-tarjeta" aria-labelledby="candidatos-titulo">
        <header className="tb-tarjeta-cabeza">
          <h3 id="candidatos-titulo">Destinos alternativos sugeridos</h3>
        </header>
        <ol className="tb-candidatos">
          {datos.candidatos.map((c) => (
            <li key={c.nombre}>
              <strong>{c.nombre}</strong>: {c.motivo}.{' '}
              {c.poi_catalogo.real ? `${entero(c.poi_catalogo.real)} lugares en el catálogo.` : 'Sin lugares reales en el catálogo todavía.'}
            </li>
          ))}
        </ol>
        <FichaMetodologica fichas={ficha('candidato_destino_alternativo')} fuentes={datos.fuentes} />
      </section>

      <Grafico
        titulo="Ocupación hotelera de los últimos 12 meses por destino"
        acciones={<BotonCsv ruta={ruta} token={token} nombre="oferta-demanda" />}
        grafico={
          <BarrasH
            titulo="Ocupación hotelera por destino"
            descripcion={`Ocupación ponderada de ${ventana}. La línea marca la ocupación del Estado. Los candidatos a destino alternativo llevan la marca «◆ candidato».`}
            barras={porOcupacion.map((d) => ({
              etiqueta: d.nombre,
              valor: d.ocupacion_pct,
              texto: `${pct(d.ocupacion_pct)} · ${entero(d.cuartos_libres_dia)} libres/día`,
              resaltada: d.candidato,
              marca: d.candidato ? '◆ candidato' : undefined,
            }))}
            maximo={100}
            referencia={
              datos.estado.ocupacion_pct != null
                ? { valor: datos.estado.ocupacion_pct, etiqueta: `Estado ${pct(datos.estado.ocupacion_pct)}` }
                : undefined
            }
          />
        }
        tabla={<TablaOferta datos={datos} />}
        ficha={
          <FichaMetodologica
            fichas={ficha('ocupacion_12m', 'cuartos_libres_dia_12m')}
            fuentes={datos.fuentes}
            n={`${datos.destinos.length} centros turísticos; meses con dato por destino en la tabla`}
          />
        }
      />

      <div className="tb-rejilla">
        <Grafico
          titulo="Concentración de la demanda por año (HHI)"
          resumen={<p>Escala de 0 a 10 000: más alto, más concentrado en pocos centros. * año parcial.</p>}
          grafico={
            <Linea
              titulo="Índice Herfindahl-Hirschman de llegadas por año"
              descripcion={anual
                .map((a) => `${a.anio}: ${entero(a.hhi)}${a.parcial ? ` (parcial, ${a.meses} meses)` : ''}`)
                .join('; ')}
              puntos={anual.map((a) => ({ x: String(a.anio), y: a.hhi, hueco: a.parcial }))}
            />
          }
          tabla={
            <TablaDatos
              titulo="HHI de llegadas por año"
              filas={anual}
              clave={(a) => String(a.anio)}
              columnas={[
                { titulo: 'Año', valor: (a) => a.anio },
                { titulo: 'HHI', valor: (a) => entero(a.hhi), numerica: true },
                { titulo: 'Meses', valor: (a) => a.meses, numerica: true },
                { titulo: 'Centros', valor: (a) => a.centros, numerica: true },
                { titulo: 'Año completo', valor: (a) => (a.parcial ? 'No' : 'Sí') },
              ]}
            />
          }
          ficha={<FichaMetodologica fichas={ficha('hhi_llegadas')} fuentes={datos.fuentes} />}
        />
        <Grafico
          titulo="Participación en las llegadas (12 meses)"
          grafico={
            <BarrasH
              titulo="Participación de cada destino en las llegadas"
              descripcion="Porcentaje de las llegadas de los centros turísticos que recibe cada destino."
              barras={datos.destinos.map((d) => ({
                etiqueta: d.nombre,
                valor: d.participacion_pct,
                texto: pct(d.participacion_pct),
              }))}
            />
          }
          tabla={
            <TablaDatos
              titulo="Participación en las llegadas"
              filas={datos.destinos}
              clave={(d) => d.centro_ot}
              columnas={[
                { titulo: 'Destino', valor: (d) => d.nombre },
                { titulo: 'Llegadas', valor: (d) => entero(d.llegadas), numerica: true },
                { titulo: 'Participación', valor: (d) => pct(d.participacion_pct), numerica: true },
              ]}
            />
          }
          ficha={<FichaMetodologica fichas={ficha('participacion_llegadas_12m')} fuentes={datos.fuentes} />}
        />
      </div>

      {vista === 'tecnica' ? (
        <section className="tb-tarjeta" aria-labelledby="tecnica-oferta">
          <header className="tb-tarjeta-cabeza">
            <h3 id="tecnica-oferta">Vista técnica: todos los indicadores por destino</h3>
          </header>
          <TablaOferta datos={datos} />
          <FichaMetodologica
            fichas={ficha('estadia_12m', 'crecimiento_llegadas_12m', 'afluencia_12m', 'poi_catalogo_destino')}
            fuentes={datos.fuentes}
          />
          <p className="tb-nota">
            Estado calculado desde la {datos.estado.origen}. Mediana de cuartos libres por día de los destinos:{' '}
            {entero(datos.mediana_cuartos_libres_dia)}. Calculado {fecha(datos.calculado_en)}.
          </p>
        </section>
      ) : null}
    </div>
  )
}

function TablaOferta({ datos }: { datos: DatosOferta }) {
  return (
    <TablaDatos
      titulo={`Indicadores por destino, ${datos.ventana.desde} a ${datos.ventana.hasta}`}
      filas={datos.destinos}
      clave={(d) => d.centro_ot}
      columnas={[
        { titulo: 'Destino', valor: (d) => d.nombre },
        { titulo: 'Ocupación', valor: (d) => pct(d.ocupacion_pct), numerica: true },
        { titulo: 'Cuartos libres/día', valor: (d) => entero(d.cuartos_libres_dia), numerica: true },
        { titulo: 'Estadía (noches)', valor: (d) => dosDec(d.estadia_noches), numerica: true },
        {
          titulo: 'Crecimiento de llegadas',
          valor: (d) => (d.crecimiento_llegadas_pct == null ? 'Sin evidencia suficiente' : pct(d.crecimiento_llegadas_pct)),
          numerica: true,
        },
        { titulo: 'Llegadas', valor: (d) => entero(d.llegadas), numerica: true },
        {
          titulo: 'Afluencia estimada',
          valor: (d) => (
            <>
              {entero(d.afluencia_estimada)} <Procedencia valor="derivado" />
            </>
          ),
          numerica: true,
        },
        { titulo: 'Meses con dato', valor: (d) => d.meses_con_dato, numerica: true },
        { titulo: 'Lugares en catálogo', valor: (d) => entero(d.poi_catalogo.real), numerica: true },
        { titulo: 'Candidato', valor: (d) => (d.candidato ? 'Sí' : 'No') },
      ]}
    />
  )
}

// ====================================================================== Inclusión

export function Inclusion({ token, salir }: Props) {
  const ruta = '/b2b/accessibility-gaps'
  const { datos, error } = useDatos<Brechas>(ruta, token, salir)
  if (error) return <ErrorCarga mensaje={error} />
  if (!datos) return <Cargando que="las brechas de accesibilidad" />
  const ficha = (...ids: string[]) => datos.fichas.filter((f) => ids.includes(f.metric_id))
  return (
    <div className="tb-modulo">
      <p className="tb-aviso" role="note">
        {datos.aviso}
      </p>
      {!datos.resumen.length ? <p role="status">Sin catálogo de lugares cargado.</p> : null}
      {bloques(datos.resumen).map(({ sintetico, filas }) => {
        const r = filas[0]
        const destinos = datos.por_destino.filter((d) => d.is_synthetic === sintetico)
        const atributos = datos.por_atributo.filter((a) => a.is_synthetic === sintetico)
        return (
          <div key={String(sintetico)} className="tb-bloque">
            <TituloBloque sintetico={sintetico} />
            <dl className="tb-kpis">
              <Kpi etiqueta="Lugares en el catálogo" valor={entero(r.poi)} />
              <Kpi etiqueta="Con algún dato de accesibilidad" valor={pct(r.con_informacion_pct)} procedencia="medido" />
              <Kpi etiqueta="Cobertura verificada" valor={pct(r.verificada_pct)} detalle="sin escalones y baño verificados" />
              <Kpi etiqueta="Sin ningún atributo verificado" valor={pct(r.sin_verificar_pct)} />
            </dl>
            <div className="tb-rejilla">
              <Grafico
                titulo="Lugares con información de accesibilidad por destino"
                acciones={<BotonCsv ruta={ruta} token={token} nombre="brechas-accesibilidad" />}
                grafico={
                  <BarrasH
                    titulo="Porcentaje de lugares con información de accesibilidad"
                    descripcion="Cobertura de información por destino; no es el nivel de accesibilidad."
                    maximo={100}
                    barras={[...destinos]
                      .sort((a, b) => a.con_informacion_pct - b.con_informacion_pct)
                      .map((d) => ({
                        etiqueta: d.nombre,
                        valor: d.con_informacion_pct,
                        texto: `${pct(d.con_informacion_pct)} (${entero(d.con_informacion)} de ${entero(d.poi)})`,
                      }))}
                  />
                }
                tabla={
                  <TablaDatos
                    titulo="Cobertura de información por destino"
                    filas={destinos}
                    clave={(d) => d.destino_id}
                    columnas={[
                      { titulo: 'Destino', valor: (d) => d.nombre },
                      { titulo: 'Lugares', valor: (d) => entero(d.poi), numerica: true },
                      { titulo: 'Con dato', valor: (d) => pct(d.con_informacion_pct), numerica: true },
                      { titulo: 'Verificada', valor: (d) => entero(d.verificada), numerica: true },
                      { titulo: 'Parcial', valor: (d) => entero(d.parcial), numerica: true },
                      { titulo: 'Sin verificar', valor: (d) => entero(d.sin_verificar), numerica: true },
                    ]}
                  />
                }
                ficha={<FichaMetodologica fichas={ficha('cobertura_info_accesibilidad')} fuentes={datos.fuentes} n={`${entero(r.poi)} lugares`} />}
              />
              <Grafico
                titulo="Cobertura por atributo"
                grafico={
                  <BarrasH
                    titulo="Porcentaje de lugares con dato por atributo"
                    descripcion="Para cada atributo, porcentaje de lugares con dato y porcentaje verificado."
                    maximo={100}
                    barras={atributos.map((a) => ({
                      etiqueta: ATRIBUTOS[a.atributo] ?? a.atributo,
                      valor: a.con_valor_pct,
                      texto: `${pct(a.con_valor_pct)} con dato · ${pct(a.verificado_pct)} verificado`,
                    }))}
                  />
                }
                tabla={
                  <TablaDatos
                    titulo="Estado de cada atributo"
                    filas={atributos}
                    clave={(a) => a.atributo}
                    columnas={[
                      { titulo: 'Atributo', valor: (a) => ATRIBUTOS[a.atributo] ?? a.atributo },
                      { titulo: 'Verificado', valor: (a) => entero(a.verificado), numerica: true },
                      { titulo: 'Reportado', valor: (a) => entero(a.reportado), numerica: true },
                      { titulo: 'En moderación', valor: (a) => entero(a.en_moderacion), numerica: true },
                      { titulo: 'Sin verificar', valor: (a) => entero(a.sin_verificar), numerica: true },
                      { titulo: 'Sin dato', valor: (a) => entero(a.sin_dato), numerica: true },
                    ]}
                  />
                }
                ficha={<FichaMetodologica fichas={ficha('cobertura_atributo')} fuentes={datos.fuentes} />}
              />
            </div>
          </div>
        )
      })}

      <section className="tb-tarjeta" aria-labelledby="barreras-titulo">
        <header className="tb-tarjeta-cabeza">
          <h3 id="barreras-titulo">Barreras reportadas por la comunidad</h3>
        </header>
        {!datos.barreras.length ? <p>Sin reportes de barrera todavía.</p> : null}
        {datos.barreras.map((b) => (
          <div key={String(b.is_synthetic)} className="tb-bloque">
            <TituloBloque sintetico={b.is_synthetic} />
            {b.suprimido ? (
              <p>{SUPRIMIDO}: menos de {datos.k_minimo} personas reportaron. Sin evidencia suficiente para publicar el conteo.</p>
            ) : (
              <>
                <dl className="tb-kpis">
                  <Kpi etiqueta="Reportes" valor={entero(b.casos)} />
                  <Kpi etiqueta="Aceptados" valor={entero(b.aceptados)} detalle={`tasa ${prop(b.tasa_aceptacion)}`} />
                  <Kpi etiqueta="En cola" valor={entero(b.abiertos)} />
                  <Kpi etiqueta="Tiempo mediano de moderación" valor={`${uno(b.tiempo_moderacion_mediano_h)} h`} />
                </dl>
                <TablaDatos
                  titulo="Reportes por tipo de barrera"
                  filas={b.por_tipo ?? []}
                  clave={(t) => t.tipo}
                  columnas={[
                    { titulo: 'Tipo', valor: (t) => TIPOS_BARRERA[t.tipo] ?? t.tipo },
                    { titulo: 'Reportes', valor: (t) => entero(t.casos), numerica: true },
                    { titulo: 'Aceptados', valor: (t) => entero(t.aceptados), numerica: true },
                  ]}
                />
              </>
            )}
          </div>
        ))}
        <FichaMetodologica fichas={ficha('barreras_reportadas', 'tiempo_moderacion_mediano_h')} fuentes={datos.fuentes} />
      </section>

      <section className="tb-tarjeta" aria-labelledby="prioridades-titulo">
        <header className="tb-tarjeta-cabeza">
          <h3 id="prioridades-titulo">Prioridades sugeridas</h3>
        </header>
        <p className="tb-nota">Generadas desde los datos; requieren validación de la Secretaría.</p>
        <ul className="tb-prioridades">
          {datos.prioridades.map((p, i) => (
            <li key={i}>
              {p.is_synthetic ? <span className="tb-etiqueta tb-sintetico">Sintético</span> : <span className="tb-etiqueta tb-medido">Real</span>}{' '}
              {p.sugerencia}
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

// ====================================================================== Panorama

export function Panorama({ token, salir }: Props) {
  const ruta = '/b2b/metrics?modulo=panorama'
  const { datos, error } = useDatos<DatosPanorama>(ruta, token, salir)
  if (error) return <ErrorCarga mensaje={error} />
  if (!datos) return <Cargando que="el panorama" />
  return (
    <div className="tb-modulo">
      <p className="tb-aviso" role="note">
        {datos.aviso} Se suprime todo grupo con menos de {datos.k_minimo} personas.
      </p>
      {!datos.hay_reales ? (
        <p className="tb-real">Datos reales: sin evidencia suficiente todavía (ninguna visita confirmada).</p>
      ) : null}
      {bloques(datos.grupos).map(({ sintetico, filas }) => (
        <div key={String(sintetico)} className="tb-bloque">
          <TituloBloque sintetico={sintetico} />
          <div className="tb-rejilla">
            <Grafico
              titulo="Visitas observadas por destino"
              acciones={<BotonCsv ruta={ruta} token={token} nombre="panorama" />}
              grafico={
                <BarrasH
                  titulo="Visitas confirmadas por destino"
                  descripcion="Visitas confirmadas en la muestra de la app; los grupos con menos de k personas se suprimen."
                  formato={entero}
                  barras={filas.map((g) => ({
                    etiqueta: g.nombre,
                    valor: g.visitas_observadas,
                    texto: g.suprimido ? SUPRIMIDO : `${entero(g.visitas_observadas)} visitas · ${entero(g.personas)} personas`,
                  }))}
                />
              }
              tabla={<TablaPanorama filas={filas} />}
              ficha={
                <FichaMetodologica
                  fichas={datos.fichas.filter((f) => ['visitas_observadas', 'visitantes_distintos'].includes(f.metric_id))}
                  fuentes={datos.fuentes}
                  n="personas distintas por grupo, en la tabla"
                />
              }
            />
            <Grafico
              titulo="Permanencia mediana por destino"
              grafico={
                <BarrasH
                  titulo="Permanencia mediana en minutos"
                  descripcion="Mediana de minutos de las visitas probables, con cuartiles 25 y 75."
                  formato={entero}
                  barras={filas.map((g) => ({
                    etiqueta: g.nombre,
                    valor: g.permanencia.mediana_min,
                    texto: g.permanencia.suprimido
                      ? SUPRIMIDO
                      : `${entero(g.permanencia.mediana_min)} min (${entero(g.permanencia.p25_min)}–${entero(g.permanencia.p75_min)})`,
                  }))}
                />
              }
              tabla={<TablaPanorama filas={filas} />}
              ficha={
                <FichaMetodologica
                  fichas={datos.fichas.filter((f) => ['permanencia_mediana_min', 'confianza_media_visitas'].includes(f.metric_id))}
                  fuentes={datos.fuentes}
                />
              }
            />
          </div>
        </div>
      ))}
    </div>
  )
}

function TablaPanorama({ filas }: { filas: DatosPanorama['grupos'] }) {
  return (
    <TablaDatos
      titulo="Panorama por destino"
      filas={filas}
      clave={(g) => g.destino_id}
      columnas={[
        { titulo: 'Destino', valor: (g) => g.nombre },
        { titulo: 'Personas', valor: (g) => (g.suprimido ? `< k` : entero(g.personas)), numerica: true },
        { titulo: 'Visitas', valor: (g) => (g.suprimido ? SUPRIMIDO : entero(g.visitas_observadas)), numerica: true },
        { titulo: 'Permanencia mediana (min)', valor: (g) => (g.permanencia.suprimido ? SUPRIMIDO : entero(g.permanencia.mediana_min)), numerica: true },
        { titulo: 'Confianza media', valor: (g) => dosDec(g.confianza_media), numerica: true },
        { titulo: 'Lugares visitados', valor: (g) => pct(g.cobertura_poi_pct), numerica: true },
        { titulo: 'Nota', valor: (g) => (g.supresion_complementaria ? 'Supresión complementaria' : '') },
      ]}
    />
  )
}

// ====================================================================== Experiencia

export function Experiencia({ token, salir }: Props) {
  const ruta = '/b2b/metrics?modulo=experiencia'
  const { datos, error } = useDatos<DatosExperiencia>(ruta, token, salir)
  const [destino, setDestino] = useState<string>('')
  if (error) return <ErrorCarga mensaje={error} />
  if (!datos) return <Cargando que="la experiencia" />
  const destinos = [...new Map(datos.grupos.filter((g) => g.destino_id).map((g) => [g.destino_id!, g.nombre])).entries()]
  return (
    <div className="tb-modulo">
      <p className="tb-aviso" role="note">
        {datos.aviso} Intervalos del 95 %. Se suprime todo grupo con menos de {datos.k_minimo} personas.
      </p>
      {!datos.hay_reales ? (
        <p className="tb-real">Datos reales: sin evidencia suficiente todavía (ninguna reseña).</p>
      ) : null}
      <label className="tb-campo">
        Destino{' '}
        <select value={destino} onChange={(e) => setDestino(e.target.value)}>
          <option value="">Todos los destinos</option>
          {destinos.map(([id, nombre]) => (
            <option key={id} value={id}>
              {nombre}
            </option>
          ))}
        </select>
      </label>
      {bloques(datos.grupos.filter((g) => (destino ? g.destino_id === destino : g.destino_id === null))).map(
        ({ sintetico, filas }) => (
          <div key={String(sintetico)} className="tb-bloque">
            <TituloBloque sintetico={sintetico} />
            <Grafico
              titulo="Satisfacción media por dimensión (1 a 5)"
              acciones={<BotonCsv ruta={ruta} token={token} nombre="experiencia" />}
              grafico={
                <BarrasH
                  titulo="Satisfacción media por dimensión"
                  descripcion="Media de 1 a 5 con intervalo bootstrap del 95 % y número de reseñas."
                  maximo={5}
                  formato={dosDec}
                  barras={filas.map((g) => ({
                    etiqueta: DIMENSIONES[g.dimension] ?? g.dimension,
                    valor: g.media,
                    resaltada: g.media != null && g.media < 3,
                    texto: g.suprimido
                      ? SUPRIMIDO
                      : `${dosDec(g.media)} (IC ${intervalo(g.media_ic95, dosDec)}) · n ${entero(g.n)}`,
                  }))}
                />
              }
              tabla={
                <TablaDatos
                  titulo="Satisfacción por dimensión"
                  filas={filas}
                  clave={(g) => g.dimension}
                  columnas={[
                    { titulo: 'Dimensión', valor: (g) => DIMENSIONES[g.dimension] ?? g.dimension },
                    { titulo: 'Media', valor: (g) => (g.suprimido ? SUPRIMIDO : dosDec(g.media)), numerica: true },
                    { titulo: 'IC 95 %', valor: (g) => intervalo(g.media_ic95, dosDec) },
                    { titulo: 'Calificación baja (≤ 2)', valor: (g) => prop(g.proporcion_baja), numerica: true },
                    { titulo: 'IC 95 % (Wilson)', valor: (g) => intervalo(g.proporcion_baja_ic95, (v) => prop(v)) },
                    { titulo: 'Reseñas (n)', valor: (g) => entero(g.n), numerica: true },
                  ]}
                />
              }
              ficha={<FichaMetodologica fichas={datos.fichas} fuentes={datos.fuentes} />}
            />
          </div>
        ),
      )}
    </div>
  )
}

// ====================================================================== Moderación

type Decision = { id: number; estado: string; atributo_actualizado: { atributo: string; valor: string; estado: string } | null }

export function Moderacion({ token, salir }: Props) {
  const [estado, setEstado] = useState<'abierto' | 'aceptado' | 'rechazado'>('abierto')
  const { datos, error, recargar } = useDatos<{ items: CasoModeracion[] }>(`/moderation?estado=${estado}`, token, salir)
  const [mensaje, setMensaje] = useState<string | null>(null)
  const [notas, setNotas] = useState<Record<number, string>>({})

  async function decidir(caso: CasoModeracion, decision: 'aceptar' | 'rechazar') {
    try {
      const r = await enviar<Decision>(`/moderation/${caso.id}/decision`, token, {
        decision,
        nota: notas[caso.id] || undefined,
      })
      const cambio = r.atributo_actualizado
        ? ` La ficha cambió: ${ATRIBUTOS[r.atributo_actualizado.atributo] ?? r.atributo_actualizado.atributo} = «${r.atributo_actualizado.valor}» (${r.atributo_actualizado.estado}). La siguiente recomendación ya lo considera.`
        : ''
      setMensaje(`Caso ${r.id} ${r.estado}.${cambio}`)
      recargar()
    } catch (e) {
      setMensaje(`No se pudo decidir el caso ${caso.id}: ${(e as Error).message}`)
    }
  }

  return (
    <div className="tb-modulo">
      <p className="tb-intro">
        Circuito cerrado: reporte de barrera → moderación → la ficha cambia → el módulo Inclusión muestra la brecha →
        la siguiente recomendación la considera.
      </p>
      <fieldset className="tb-segmentado">
        <legend>Casos</legend>
        {(['abierto', 'aceptado', 'rechazado'] as const).map((e) => (
          <label key={e}>
            <input type="radio" name="estado-caso" value={e} checked={estado === e} onChange={() => setEstado(e)} />
            {e === 'abierto' ? 'En cola' : e === 'aceptado' ? 'Aceptados' : 'Rechazados'}
          </label>
        ))}
      </fieldset>
      <div aria-live="polite">{mensaje ? <p className="tb-exito">{mensaje}</p> : null}</div>
      {error ? <ErrorCarga mensaje={error} /> : null}
      {!datos && !error ? <Cargando que="la cola de moderación" /> : null}
      {datos && !datos.items.length ? <p>No hay casos en este estado.</p> : null}
      <ul className="tb-cola">
        {datos?.items.map((c) => (
          <li key={c.id} className="tb-caso">
            <h3>
              Caso {c.id}: {TIPOS_BARRERA[c.tipo] ?? c.tipo}
            </h3>
            <p>
              Lugar <code>{c.poi_id}</code> · atributo {c.atributo ? (ATRIBUTOS[c.atributo] ?? c.atributo) : 'ninguno'} ·{' '}
              {fecha(c.creado_en)}
            </p>
            {c.descripcion ? <p className="tb-descripcion">{c.descripcion}</p> : null}
            {c.estado === 'abierto' ? (
              <div className="tb-acciones">
                <label className="tb-campo">
                  Nota (opcional){' '}
                  <input
                    type="text"
                    value={notas[c.id] ?? ''}
                    onChange={(e) => setNotas({ ...notas, [c.id]: e.target.value })}
                  />
                </label>
                <button type="button" className="tb-boton" onClick={() => decidir(c, 'aceptar')}>
                  Aceptar caso {c.id}
                </button>
                <button type="button" className="tb-boton-sec" onClick={() => decidir(c, 'rechazar')}>
                  Rechazar caso {c.id}
                </button>
              </div>
            ) : (
              <p>Estado: {c.estado}</p>
            )}
          </li>
        ))}
      </ul>
      <p className="tb-nota">Quien reporta nunca se muestra.</p>
    </div>
  )
}
