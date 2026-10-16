import { useId, useRef, useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'
import { ErrorApi, iniciarSesion, registrar } from '../api/cliente'
import { cerrarSesion, useAlmacen } from '../almacen/almacen'
import { Aviso } from '../componentes/Avisos'
import { Icono } from '../componentes/Icono'
import { useTextos } from '../i18n/textos'

type Modo = 'entrar' | 'crear'

/** Cuenta opcional: solo hace falta para enviar reseñas y reportes de barreras. */
export function Cuenta() {
  const t = useTextos()
  const { sesion } = useAlmacen()
  const [parametros] = useSearchParams()
  const navegar = useNavigate()
  const volver = parametros.get('volver')
  const destinoSeguro = volver && volver.startsWith('/') && !volver.startsWith('//') ? volver : null

  const [modo, setModo] = useState<Modo>('entrar')
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [nombre, setNombre] = useState('')
  const [errores, setErrores] = useState<{ correo?: string; contrasena?: string }>({})
  const [fallo, setFallo] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)
  const refs = { correo: useRef<HTMLInputElement>(null), contrasena: useRef<HTMLInputElement>(null) }
  const ids = {
    correo: useId(),
    contrasena: useId(),
    nombre: useId(),
    errorCorreo: useId(),
    errorContrasena: useId(),
    ayudaContrasena: useId(),
    ayudaNombre: useId(),
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    const nuevos: typeof errores = {}
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo.trim())) nuevos.correo = t.cuenta.errorCorreo
    if (contrasena.length < 8) nuevos.contrasena = t.cuenta.errorContrasena
    setErrores(nuevos)
    if (nuevos.correo || nuevos.contrasena) {
      ;(nuevos.correo ? refs.correo.current : refs.contrasena.current)?.focus()
      return
    }
    setEnviando(true)
    setFallo(null)
    try {
      if (modo === 'entrar') await iniciarSesion({ correo: correo.trim(), contrasena })
      else await registrar({ correo: correo.trim(), contrasena, ...(nombre.trim() ? { nombre_visible: nombre.trim() } : {}) })
      if (destinoSeguro) navegar(destinoSeguro)
    } catch (error) {
      if (error instanceof ErrorApi && error.estado === 401) setFallo(t.cuenta.errorCredenciales)
      else if (error instanceof ErrorApi && error.estado === 409) setFallo(t.cuenta.errorExiste)
      else setFallo(t.cuenta.errorServicio)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div style={{ maxWidth: '32rem' }}>
      <header className="cabecera-pagina">
        <h1>{t.cuenta.titulo}</h1>
        <p className="cabecera-pagina__intro">{t.cuenta.intro}</p>
      </header>

      {sesion ? (
        <div className="panel pila">
          <Aviso tono="exito" rol="status">
            <p>{t.cuenta.sesionActiva(sesion.usuario.correo)}</p>
          </Aviso>
          <p className="texto-suave">{t.cuenta.privacidad}</p>
          <div className="acciones">
            {destinoSeguro && (
              <Link className="boton boton--principal" to={destinoSeguro}>
                {t.cuenta.continuar}
              </Link>
            )}
            <button type="button" className="boton boton--secundario" onClick={cerrarSesion}>
              {t.cuenta.salir}
            </button>
          </div>
        </div>
      ) : (
        <form className="panel formulario" noValidate onSubmit={enviar}>
          <div className="segmentado" role="group" aria-label={t.cuenta.modo} style={{ justifySelf: 'start' }}>
            <button type="button" aria-pressed={modo === 'entrar'} onClick={() => setModo('entrar')}>
              {t.cuenta.entrar}
            </button>
            <button type="button" aria-pressed={modo === 'crear'} onClick={() => setModo('crear')}>
              {t.cuenta.crear}
            </button>
          </div>

          <div className="campo">
            <label className="campo__etiqueta" htmlFor={ids.correo}>
              {t.cuenta.correo}
            </label>
            {errores.correo && (
              <p className="campo__error" id={ids.errorCorreo}>
                <Icono nombre="reportado" className="pastilla__icono" />
                {errores.correo}
              </p>
            )}
            <input
              id={ids.correo}
              ref={refs.correo}
              className="control"
              type="email"
              autoComplete="email"
              value={correo}
              aria-invalid={errores.correo ? true : undefined}
              aria-describedby={errores.correo ? ids.errorCorreo : undefined}
              onChange={(e) => setCorreo(e.target.value)}
            />
          </div>

          <div className="campo">
            <label className="campo__etiqueta" htmlFor={ids.contrasena}>
              {t.cuenta.contrasena}
            </label>
            <p className="campo__ayuda" id={ids.ayudaContrasena}>
              {t.cuenta.contrasenaAyuda}
            </p>
            {errores.contrasena && (
              <p className="campo__error" id={ids.errorContrasena}>
                <Icono nombre="reportado" className="pastilla__icono" />
                {errores.contrasena}
              </p>
            )}
            <input
              id={ids.contrasena}
              ref={refs.contrasena}
              className="control"
              type="password"
              autoComplete={modo === 'entrar' ? 'current-password' : 'new-password'}
              value={contrasena}
              aria-invalid={errores.contrasena ? true : undefined}
              aria-describedby={[ids.ayudaContrasena, errores.contrasena ? ids.errorContrasena : ''].filter(Boolean).join(' ')}
              onChange={(e) => setContrasena(e.target.value)}
            />
          </div>

          {modo === 'crear' && (
            <div className="campo">
              <label className="campo__etiqueta" htmlFor={ids.nombre}>
                {t.cuenta.nombre}
              </label>
              <p className="campo__ayuda" id={ids.ayudaNombre}>
                {t.cuenta.nombreAyuda}
              </p>
              <input
                id={ids.nombre}
                className="control"
                autoComplete="nickname"
                maxLength={60}
                value={nombre}
                aria-describedby={ids.ayudaNombre}
                onChange={(e) => setNombre(e.target.value)}
              />
            </div>
          )}

          {fallo && (
            <Aviso tono="error" rol="alert">
              <p>{fallo}</p>
            </Aviso>
          )}

          <button type="submit" className="boton boton--principal" disabled={enviando}>
            {modo === 'entrar' ? t.cuenta.entrar : t.cuenta.crear}
          </button>
          <p className="campo__ayuda">{t.cuenta.privacidad}</p>
        </form>
      )}
    </div>
  )
}
