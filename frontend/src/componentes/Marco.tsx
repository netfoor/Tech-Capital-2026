import { useEffect, useRef } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router'
import { cambiarPreferencias, useAlmacen } from '../almacen/almacen'
import { useTextos } from '../i18n/textos'
import { AvisoAlmacenamiento, BandaSintetica } from './Avisos'
import { Icono, type NombreIcono } from './Icono'
import { Logo } from './Logo'

const NAVEGACION: { ruta: string; clave: 'descubrir' | 'miMapa' | 'planear' | 'recorrido'; icono: NombreIcono }[] = [
  { ruta: '/', clave: 'descubrir', icono: 'descubrir' },
  { ruta: '/mi-mapa', clave: 'miMapa', icono: 'miMapa' },
  { ruta: '/planear', clave: 'planear', icono: 'planear' },
  { ruta: '/recorrido', clave: 'recorrido', icono: 'recorrido' },
]

/** Marco de la PWA del visitante: banda sintética, encabezado, navegación, contenido y pie. */
export function Marco() {
  const t = useTextos()
  const { preferencias } = useAlmacen()
  const { pathname } = useLocation()
  const principal = useRef<HTMLElement>(null)
  const primeraVez = useRef(true)

  useEffect(() => {
    document.documentElement.dataset.lenguaje = preferencias.lenguajeClaro ? 'claro' : 'normal'
  }, [preferencias.lenguajeClaro])

  // Al cambiar de página, el foco va al contenido para que el lector de pantalla lo anuncie.
  useEffect(() => {
    if (primeraVez.current) {
      primeraVez.current = false
      return
    }
    principal.current?.focus()
    window.scrollTo?.(0, 0)
  }, [pathname])

  return (
    <div className="app">
      <a className="saltar" href="#contenido">
        {t.general.saltar}
      </a>
      <BandaSintetica />
      <header className="encabezado">
        <div className="contenedor encabezado__interior">
          <Link to="/" className="marca">
            <Logo className="marca__logo" />
            <span>
              Puebla Viva <span className="marca__360">360</span>
            </span>
          </Link>
          <nav className="nav" aria-label={t.nav.principal}>
            <ul className="nav__lista">
              {NAVEGACION.map((elemento) => (
                <li key={elemento.ruta}>
                  <NavLink to={elemento.ruta} end={elemento.ruta === '/'} className="nav__enlace">
                    <Icono nombre={elemento.icono} className="nav__icono" />
                    <span>{t.nav[elemento.clave]}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
          <button
            type="button"
            className="boton-lectura"
            aria-pressed={preferencias.lenguajeClaro}
            onClick={() => cambiarPreferencias({ lenguajeClaro: !preferencias.lenguajeClaro })}
            title={t.lectura.lenguajeClaroAyuda}
          >
            <span className="boton-lectura__aa" aria-hidden="true">
              Aa
            </span>
            <span className="boton-lectura__texto">{t.lectura.lenguajeClaro}</span>
          </button>
        </div>
      </header>
      <main id="contenido" className="contenido" ref={principal} tabIndex={-1}>
        <AvisoAlmacenamiento />
        <Outlet />
      </main>
      <footer className="pie">
        <div className="contenedor pie__interior">
          <p>{t.pie.privacidad}</p>
          <p>{t.pie.datos}</p>
          <p>
            <Link to="/cuenta">{t.nav.cuenta}</Link> · <Link to="/admin">{t.nav.secretaria}</Link>
          </p>
        </div>
      </footer>
    </div>
  )
}
