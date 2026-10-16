import { Link, Route, Routes } from 'react-router'
import { EstadoApi } from './componentes/EstadoApi'

function Visitante() {
  return (
    <main id="contenido">
      <h1>Puebla Viva 360</h1>
      <p>Descubre, planea y vive recorridos inclusivos en Puebla.</p>
      <EstadoApi />
    </main>
  )
}

function Tablero() {
  return (
    <main id="contenido">
      <h1>Tablero institucional</h1>
      <p>Indicadores agregados para la Secretaría de Desarrollo Turístico.</p>
      <EstadoApi />
    </main>
  )
}

export default function App() {
  return (
    <>
      <a className="saltar" href="#contenido">
        Saltar al contenido
      </a>
      <nav aria-label="Principal">
        <Link to="/">Visitante</Link> · <Link to="/admin">Secretaría</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Visitante />} />
        <Route path="/admin/*" element={<Tablero />} />
      </Routes>
    </>
  )
}
