import { useCallback, useState, type FormEvent } from 'react'
import { Navigate, NavLink, Route, Routes } from 'react-router'
import { guardarSesion, iniciarSesion, sesionGuardada, type Sesion } from './api'
import { Experiencia, Inclusion, Moderacion, OfertaDemanda, Panorama } from './modulos'
import { ContextoVista, type Vista } from './vista'
import './tablero.css'

const ROLES_TABLERO = ['viewer', 'analista', 'admin']
const MODERADORES = ['analista', 'admin']

const MODULOS = [
  { ruta: 'oferta-demanda', nombre: 'Oferta–demanda', Componente: OfertaDemanda },
  { ruta: 'inclusion', nombre: 'Inclusión', Componente: Inclusion },
  { ruta: 'panorama', nombre: 'Panorama', Componente: Panorama },
  { ruta: 'experiencia', nombre: 'Experiencia', Componente: Experiencia },
]

function InicioSesion({ alEntrar }: { alEntrar: (s: Sesion) => void }) {
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  async function enviar(e: FormEvent) {
    e.preventDefault()
    setEnviando(true)
    setError(null)
    try {
      const sesion = await iniciarSesion(correo, contrasena)
      if (!ROLES_TABLERO.includes(sesion.usuario.rol)) {
        setError('Tu cuenta no tiene acceso al tablero institucional.')
        return
      }
      alEntrar(sesion)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main id="contenido" className="tb-entrada">
      <h1>Tablero institucional</h1>
      <p>Indicadores agregados para la Secretaría de Desarrollo Turístico de Puebla. Acceso con cuenta de analista.</p>
      <form onSubmit={enviar} className="tb-formulario" noValidate>
        <label>
          Correo
          <input type="email" autoComplete="username" required value={correo} onChange={(e) => setCorreo(e.target.value)} />
        </label>
        <label>
          Contraseña
          <input
            type="password"
            autoComplete="current-password"
            required
            value={contrasena}
            onChange={(e) => setContrasena(e.target.value)}
          />
        </label>
        {error ? (
          <p role="alert" className="tb-error">
            {error}
          </p>
        ) : null}
        <button type="submit" className="tb-boton" disabled={enviando}>
          {enviando ? 'Entrando…' : 'Entrar'}
        </button>
      </form>
    </main>
  )
}

export function Tablero() {
  const [sesion, setSesion] = useState<Sesion | null>(() => sesionGuardada())
  const [vista, setVista] = useState<Vista>('ejecutiva')

  const entrar = (s: Sesion) => {
    guardarSesion(s)
    setSesion(s)
  }
  const salir = useCallback(() => {
    guardarSesion(null)
    setSesion(null)
  }, [])

  if (!sesion) return <InicioSesion alEntrar={entrar} />
  const modera = MODERADORES.includes(sesion.usuario.rol)

  return (
    <ContextoVista.Provider value={vista}>
      <div className="tb">
        <header className="tb-cabeza">
          <div>
            <p className="tb-marca">Puebla Viva 360 · Secretaría de Desarrollo Turístico</p>
            <h1>Tablero institucional</h1>
          </div>
          <div className="tb-cabeza-acciones">
            <fieldset className="tb-segmentado">
              <legend>Vista</legend>
              {(['ejecutiva', 'tecnica'] as const).map((v) => (
                <label key={v}>
                  <input type="radio" name="vista" value={v} checked={vista === v} onChange={() => setVista(v)} />
                  {v === 'ejecutiva' ? 'Ejecutiva' : 'Técnica'}
                </label>
              ))}
            </fieldset>
            <p className="tb-usuario">
              {sesion.usuario.nombre_visible ?? sesion.usuario.correo} · {sesion.usuario.rol}
            </p>
            <button type="button" className="tb-boton-sec" onClick={salir}>
              Cerrar sesión
            </button>
          </div>
        </header>
        <nav aria-label="Módulos del tablero" className="tb-pestanas">
          {MODULOS.map((m) => (
            <NavLink key={m.ruta} to={`/admin/${m.ruta}`}>
              {m.nombre}
            </NavLink>
          ))}
          {modera ? <NavLink to="/admin/moderacion">Moderación</NavLink> : null}
        </nav>
        <main id="contenido" className="tb-contenido">
          <Routes>
            <Route index element={<Navigate to="oferta-demanda" replace />} />
            {MODULOS.map(({ ruta, nombre, Componente }) => (
              <Route
                key={ruta}
                path={ruta}
                element={
                  <>
                    <h2>{nombre}</h2>
                    <Componente token={sesion.token} salir={salir} />
                  </>
                }
              />
            ))}
            {modera ? (
              <Route
                path="moderacion"
                element={
                  <>
                    <h2>Moderación de reportes de barrera</h2>
                    <Moderacion token={sesion.token} salir={salir} />
                  </>
                }
              />
            ) : null}
            <Route path="*" element={<Navigate to="oferta-demanda" replace />} />
          </Routes>
        </main>
        <footer className="tb-pie">
          La Secretaría ve agregados, nunca personas. Cada cifra tiene ficha, fuente y fecha de cálculo.
        </footer>
      </div>
    </ContextoVista.Provider>
  )
}

export default Tablero
