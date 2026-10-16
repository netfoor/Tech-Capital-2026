import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import App from '../App'

/** Monta la app completa en una ruta, como la vería el visitante. */
export function montar(ruta = '/') {
  const usuario = userEvent.setup()
  const resultado = render(
    <MemoryRouter initialEntries={[ruta]}>
      <App />
    </MemoryRouter>,
  )
  return { usuario, ...resultado }
}

/** Respuesta JSON simulada de la API. */
export function respuestaJson(cuerpo: unknown, estado = 200): Response {
  return new Response(JSON.stringify(cuerpo), { status: estado, headers: { 'content-type': 'application/json' } })
}
