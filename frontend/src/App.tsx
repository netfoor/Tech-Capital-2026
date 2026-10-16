import { Route, Routes } from 'react-router'
import { Tablero } from './admin/Tablero'
import { Marco } from './componentes/Marco'
import { Cuenta } from './paginas/Cuenta'
import { Descubrir } from './paginas/Descubrir'
import { Ficha } from './paginas/Ficha'
import { MiMapa } from './paginas/MiMapa'
import { MiRecorrido, NoEncontrado } from './paginas/MiRecorrido'
import { Planear } from './paginas/Planear'
import { Reportar } from './paginas/Reportar'
import { Resena } from './paginas/Resena'

export default function App() {
  return (
    <Routes>
      <Route element={<Marco />}>
        <Route index element={<Descubrir />} />
        <Route path="lugar/:poiId" element={<Ficha />} />
        <Route path="lugar/:poiId/reportar" element={<Reportar />} />
        <Route path="lugar/:poiId/resena" element={<Resena />} />
        <Route path="mi-mapa" element={<MiMapa />} />
        <Route path="planear" element={<Planear />} />
        <Route path="recorrido" element={<MiRecorrido />} />
        <Route path="cuenta" element={<Cuenta />} />
        <Route path="*" element={<NoEncontrado />} />
      </Route>
      <Route path="/admin/*" element={<Tablero />} />
    </Routes>
  )
}
