import { useId, useRef, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router'
import { obtenerPoi, reportarBarrera } from '../api/cliente'
import { TIPOS_BARRERA, type ResultadoEnvio, type TipoBarrera } from '../api/tipos'
import { Aviso } from '../componentes/Avisos'
import { Icono } from '../componentes/Icono'
import { ResultadoLocal } from '../componentes/ResultadoEnvio'
import { useCarga } from '../hooks/datos'
import { useTextos } from '../i18n/textos'

const MAXIMO = 500
const MAXIMO_FOTO = 5 * 1024 * 1024
const FORMATOS_FOTO = ['image/jpeg', 'image/png', 'image/webp']

export function Reportar() {
  const t = useTextos()
  const { poiId = '' } = useParams()
  const carga = useCarga(() => obtenerPoi(poiId), poiId)
  const [tipo, setTipo] = useState<TipoBarrera | ''>('')
  const [descripcion, setDescripcion] = useState('')
  const [errores, setErrores] = useState<{ tipo?: string; descripcion?: string; foto?: string }>({})
  const [foto, setFoto] = useState<{ nombre: string; datos: string } | null>(null)
  const [enviando, setEnviando] = useState(false)
  const [resultado, setResultado] = useState<ResultadoEnvio | null>(null)
  const [fallo, setFallo] = useState(false)
  const primerTipo = useRef<HTMLInputElement>(null)
  const descripcionRef = useRef<HTMLTextAreaElement>(null)
  const fotoRef = useRef<HTMLInputElement>(null)
  const ids = {
    errorTipo: useId(),
    descripcion: useId(),
    ayuda: useId(),
    errorDescripcion: useId(),
    contador: useId(),
    foto: useId(),
    ayudaFoto: useId(),
    errorFoto: useId(),
  }
  const ruta = `/lugar/${encodeURIComponent(poiId)}`

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    const nuevos: typeof errores = {}
    if (!tipo) nuevos.tipo = t.reportar.errorTipo
    if (descripcion.length > MAXIMO) nuevos.descripcion = t.reportar.errorLargo
    setErrores((previos) => ({ ...nuevos, foto: previos.foto }))
    if (nuevos.tipo || nuevos.descripcion) {
      ;(nuevos.tipo ? primerTipo.current : descripcionRef.current)?.focus()
      return
    }
    setEnviando(true)
    setFallo(false)
    try {
      const respuesta = await reportarBarrera({
        poi_id: poiId,
        tipo: tipo as TipoBarrera,
        ...(descripcion.trim() ? { descripcion: descripcion.trim() } : {}),
        ...(foto ? { foto: foto.datos } : {}),
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
        titulo={t.reportar.titulo}
        resultado={resultado}
        textos={{ servidor: t.reportar.gracias, demo: t.reportar.graciasLocal, sinSesion: t.reportar.sinSesion }}
        rutaFicha={ruta}
      />
    )
  }

  async function elegirFoto(archivo: File | undefined) {
    setErrores((previos) => ({ ...previos, foto: undefined }))
    if (!archivo) {
      setFoto(null)
      return
    }
    if (!FORMATOS_FOTO.includes(archivo.type) || archivo.size > MAXIMO_FOTO) {
      setFoto(null)
      setErrores((previos) => ({ ...previos, foto: t.reportar.errorFoto }))
      if (fotoRef.current) fotoRef.current.value = ''
      return
    }
    const datos = await new Promise<string>((resolver, rechazar) => {
      const lector = new FileReader()
      lector.onload = () => resolver(String(lector.result))
      lector.onerror = () => rechazar(lector.error)
      lector.readAsDataURL(archivo)
    })
    setFoto({ nombre: archivo.name, datos })
  }

  const hayErrores = Boolean(errores.tipo || errores.descripcion || errores.foto)

  return (
    <div style={{ maxWidth: '40rem' }}>
      <Link to={ruta} className="ruta-atras">
        <Icono nombre="atras" className="nav__icono" />
        {nombre ?? t.general.volver}
      </Link>
      <header className="cabecera-pagina">
        <h1>{t.reportar.titulo}</h1>
        {nombre && <p className="tarjeta-poi__meta">{nombre}</p>}
        <p className="cabecera-pagina__intro">{t.reportar.intro}</p>
      </header>

      <form className="formulario panel" noValidate onSubmit={enviar}>
        {hayErrores && (
          <div className="resumen-errores" role="alert">
            <h2>{t.reportar.resumenErrores}</h2>
            <ul>
              {errores.tipo && <li>{errores.tipo}</li>}
              {errores.descripcion && <li>{errores.descripcion}</li>}
              {errores.foto && <li>{errores.foto}</li>}
            </ul>
          </div>
        )}

        <fieldset
          className="grupo"
          aria-describedby={errores.tipo ? ids.errorTipo : undefined}
          aria-invalid={errores.tipo ? true : undefined}
        >
          <legend className="grupo__leyenda">{t.reportar.tipo}</legend>
          {errores.tipo && (
            <p className="campo__error" id={ids.errorTipo}>
              <Icono nombre="reportado" className="pastilla__icono" />
              {errores.tipo}
            </p>
          )}
          {TIPOS_BARRERA.map((opcion, indice) => (
            <label key={opcion} className="casilla">
              <input
                ref={indice === 0 ? primerTipo : undefined}
                type="radio"
                name="tipo"
                value={opcion}
                checked={tipo === opcion}
                required
                onChange={() => {
                  setTipo(opcion)
                  setErrores((previos) => ({ ...previos, tipo: undefined }))
                }}
              />
              <span className="casilla__texto">{t.barreras[opcion]}</span>
            </label>
          ))}
        </fieldset>

        <div className="campo">
          <label className="campo__etiqueta" htmlFor={ids.descripcion}>
            {t.reportar.descripcion}
          </label>
          <p className="campo__ayuda" id={ids.ayuda}>
            {t.reportar.descripcionAyuda}
          </p>
          {errores.descripcion && (
            <p className="campo__error" id={ids.errorDescripcion}>
              <Icono nombre="reportado" className="pastilla__icono" />
              {errores.descripcion}
            </p>
          )}
          <textarea
            id={ids.descripcion}
            ref={descripcionRef}
            className="control"
            value={descripcion}
            aria-invalid={errores.descripcion ? true : undefined}
            aria-describedby={[ids.ayuda, errores.descripcion ? ids.errorDescripcion : '', ids.contador].filter(Boolean).join(' ')}
            onChange={(evento) => setDescripcion(evento.target.value)}
          />
          <p className="campo__ayuda" id={ids.contador}>
            {t.reportar.caracteres(descripcion.length, MAXIMO)}
          </p>
        </div>

        <div className="campo">
          <label className="campo__etiqueta" htmlFor={ids.foto}>
            {t.reportar.foto}
          </label>
          <p className="campo__ayuda" id={ids.ayudaFoto}>
            {t.reportar.fotoAyuda}
          </p>
          {errores.foto && (
            <p className="campo__error" id={ids.errorFoto}>
              <Icono nombre="reportado" className="pastilla__icono" />
              {errores.foto}
            </p>
          )}
          <input
            id={ids.foto}
            ref={fotoRef}
            className="control"
            type="file"
            accept={FORMATOS_FOTO.join(',')}
            aria-invalid={errores.foto ? true : undefined}
            aria-describedby={[ids.ayudaFoto, errores.foto ? ids.errorFoto : ''].filter(Boolean).join(' ')}
            onChange={(evento) => void elegirFoto(evento.target.files?.[0])}
          />
          {foto && (
            <p className="campo__ayuda" role="status">
              {t.reportar.fotoLista(foto.nombre)}{' '}
              <button
                type="button"
                className="boton boton--discreto boton--pequeno"
                onClick={() => {
                  setFoto(null)
                  if (fotoRef.current) fotoRef.current.value = ''
                }}
              >
                {t.reportar.quitarFoto}
              </button>
            </p>
          )}
        </div>

        {fallo && (
          <Aviso tono="error" rol="alert">
            <p>{t.reportar.error}</p>
          </Aviso>
        )}

        <div className="acciones">
          <button type="submit" className="boton boton--principal" disabled={enviando}>
            <Icono nombre="bandera" className="boton__icono" />
            {enviando ? t.reportar.enviando : t.reportar.enviar}
          </button>
          <Link className="boton boton--secundario" to={ruta}>
            {t.general.cancelar}
          </Link>
        </div>
      </form>
    </div>
  )
}
