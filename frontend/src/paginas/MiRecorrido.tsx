import { Link } from 'react-router'
import { Aviso } from '../componentes/Avisos'
import { Icono } from '../componentes/Icono'
import { useTextos } from '../i18n/textos'

/** Placeholder honesto: el recorrido con GPS y la bitácora son de la spec 017. */
export function MiRecorrido() {
  const t = useTextos()
  return (
    <div style={{ maxWidth: '44rem' }}>
      <header className="cabecera-pagina">
        <h1>{t.recorrido.titulo}</h1>
        <p className="cabecera-pagina__intro">{t.recorrido.intro}</p>
      </header>
      <Aviso tono="info">
        <p>
          <strong>{t.recorrido.estado}</strong>
        </p>
      </Aviso>
      <section className="panel seccion" aria-labelledby="titulo-promesa">
        <h2 id="titulo-promesa">{t.recorrido.promesa}</h2>
        <ul className="promesa">
          {t.recorrido.puntos.map((punto) => (
            <li key={punto}>
              <Icono nombre="verificado" />
              <span>{punto}</span>
            </li>
          ))}
        </ul>
      </section>
      <p>{t.recorrido.mientras}</p>
      <Link className="boton boton--principal" to="/planear">
        <Icono nombre="planear" className="boton__icono" />
        {t.nav.planear}
      </Link>
    </div>
  )
}

export function NoEncontrado() {
  const t = useTextos()
  return (
    <div className="vacio">
      <h1>{t.error404.titulo}</h1>
      <p>{t.error404.texto}</p>
      <Link className="boton boton--principal" to="/">
        {t.ficha.irADescubrir}
      </Link>
    </div>
  )
}
