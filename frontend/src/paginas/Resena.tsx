import { useId, useRef, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router'
import { enviarResena, obtenerPoi } from '../api/cliente'
import { DIMENSIONES_RESENA, type DimensionesResena, type DimensionResena, type ResultadoEnvio } from '../api/tipos'
import { Calificacion } from '../componentes/Calificacion'
import { Icono } from '../componentes/Icono'
import { ResultadoLocal } from '../componentes/ResultadoEnvio'
import { useCarga } from '../hooks/datos'
import { useTextos } from '../i18n/textos'

type Valores = Partial<Record<DimensionResena, number>>

const OPCIONALES = DIMENSIONES_RESENA.filter((dimension) => dimension !== 'global')

export function Resena() {
  const t = useTextos()
  const { poiId = '' } = useParams()
  const carga = useCarga(() => obtenerPoi(poiId), poiId)
  const [valores, setValores] = useState<Valores>({})
  const [texto, setTexto] = useState('')
  const [faltaGlobal, setFaltaGlobal] = useState(false)
  const [enviando, setEnviando] = useState(false)
  const [resultado, setResultado] = useState<ResultadoEnvio | null>(null)
  const [fallo, setFallo] = useState(false)
  const primeroGlobal = useRef<HTMLInputElement>(null)
  const ids = { texto: useId(), ayuda: useId(), opcionales: useId() }
  const ruta = `/lugar/${encodeURIComponent(poiId)}`

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    if (!valores.global) {
      setFaltaGlobal(true)
      primeroGlobal.current?.focus()
      return
    }
    setEnviando(true)
    setFallo(false)
    try {
      const respuesta = await enviarResena({
        poi_id: poiId,
        dimensiones: valores as DimensionesResena,
        ...(texto.trim() ? { texto: texto.trim().slice(0, 1000) } : {}),
      })
      setResultado(respuesta)
    } catch {
      setFallo(true)
    } finally {
      setEnviando(false)
    }
  }

  const nombre = carga.datos?.nombre

  if (resultado) {
    return (
      <ResultadoLocal
        titulo={t.resena.titulo}
        resultado={resultado}
        textos={{ servidor: t.resena.gracias, demo: t.resena.graciasLocal, sinSesion: t.resena.sinSesion }}
        rutaFicha={ruta}
      />
    )
  }

  const cambiar = (dimension: DimensionResena) => (valor: number) => {
    setValores((previos) => ({ ...previos, [dimension]: valor }))
    if (dimension === 'global') setFaltaGlobal(false)
  }

  return (
    <div style={{ maxWidth: '44rem' }}>
      <Link to={ruta} className="ruta-atras">
        <Icono nombre="atras" className="nav__icono" />
        {nombre ?? t.general.volver}
      </Link>
      <header className="cabecera-pagina">
        <h1>{t.resena.titulo}</h1>
        {nombre && <p className="tarjeta-poi__meta">{nombre}</p>}
        <p className="cabecera-pagina__intro">{t.resena.intro}</p>
      </header>

      <form className="formulario" noValidate onSubmit={enviar}>
        {faltaGlobal && (
          <div className="resumen-errores" role="alert">
            <h2>{t.resena.resumenErrores}</h2>
            <ul>
              <li>{t.resena.dimensiones.global}</li>
            </ul>
          </div>
        )}

        <Calificacion
          ref={primeroGlobal}
          nombre="global"
          leyenda={`${t.resena.dimensiones.global} ${t.resena.obligatoria}`}
          valor={valores.global ?? null}
          error={faltaGlobal ? t.resena.falta(t.resena.dimensiones.global) : undefined}
          alCambiar={cambiar('global')}
        />

        <h2 id={ids.opcionales} className="campo__etiqueta" style={{ fontFamily: 'var(--fuente-texto)', marginBottom: 0 }}>
          {t.resena.opcionales}
        </h2>
        {OPCIONALES.map((dimension) => (
          <Calificacion
            key={dimension}
            nombre={dimension}
            leyenda={t.resena.dimensiones[dimension]}
            valor={valores[dimension] ?? null}
            alCambiar={cambiar(dimension)}
          />
        ))}

        <div className="campo">
          <label className="campo__etiqueta" htmlFor={ids.texto}>
            {t.resena.texto}
          </label>
          <p className="campo__ayuda" id={ids.ayuda}>
            {t.resena.textoAyuda}
          </p>
          <textarea
            id={ids.texto}
            className="control"
            value={texto}
            maxLength={1000}
            aria-describedby={ids.ayuda}
            onChange={(evento) => setTexto(evento.target.value)}
          />
        </div>

        {fallo && (
          <div className="aviso aviso--error" role="alert">
            <p>{t.resena.error}</p>
          </div>
        )}

        <div className="acciones">
          <button type="submit" className="boton boton--principal" disabled={enviando}>
            <Icono nombre="estrella" className="boton__icono" />
            {enviando ? t.resena.enviando : t.resena.enviar}
          </button>
          <Link className="boton boton--secundario" to={ruta}>
            {t.general.cancelar}
          </Link>
        </div>
      </form>
    </div>
  )
}
