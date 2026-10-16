import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { guardarPoi, obtenerAlmacen } from '../almacen/almacen'
import { POIS_DEMO } from '../demo/datos'
import { montar } from '../pruebas/utilidades'

describe('Planear', () => {
  it('desde cero: plan explicable, con lo que no sabemos y lo que no incluimos', async () => {
    const { usuario } = montar('/planear')
    await usuario.click(screen.getByRole('checkbox', { name: 'Evitar escalones' }))
    await usuario.selectOptions(screen.getByLabelText('Descansos'), '30')
    await usuario.selectOptions(screen.getByLabelText('Presupuesto'), 'bajo')
    await usuario.click(screen.getByRole('button', { name: /Crear mi plan/ }))

    const plan = await screen.findByRole('region', { name: 'Tu plan' })
    const paradas = within(plan).getAllByRole('listitem').filter((elemento) => elemento.classList.contains('parada'))
    expect(paradas.length).toBeGreaterThan(0)
    expect(within(plan).getAllByText(/Te lo recomendamos porque/).length).toBe(paradas.length)
    expect(within(plan).getByRole('heading', { name: 'Datos que no sabemos' })).toBeInTheDocument()
    expect(within(plan).getAllByText('Tiene escalones en el acceso.').length).toBeGreaterThan(0)
    expect(within(plan).getAllByText('Sugerencia').length).toBeGreaterThan(0)
  })

  it('valida las horas con un mensaje claro', async () => {
    const { usuario } = montar('/planear')
    const horas = screen.getByLabelText('Horas disponibles')
    await usuario.clear(horas)
    await usuario.type(horas, '30')
    await usuario.click(screen.getByRole('button', { name: /Crear mi plan/ }))
    expect(screen.getByRole('alert')).toHaveTextContent('Escribe un número de horas entre 1 y 12.')
    expect(horas).toHaveFocus()
  })

  it('desde mis guardados: por días, editable y guardable', async () => {
    for (const id of ['demo-cholula-museo', 'demo-cholula-zocalo', 'demo-cholula-piramide', 'demo-puebla-amparo', 'demo-puebla-catedral']) {
      guardarPoi(POIS_DEMO.find((poi) => poi.poi_id === id)!)
    }
    const { usuario } = montar('/planear?modo=guardados')
    expect(screen.getByRole('button', { name: 'Desde mis guardados' })).toHaveAttribute('aria-pressed', 'true')
    await usuario.click(screen.getByRole('button', { name: /Crear mi plan/ }))

    const plan = await screen.findByRole('region', { name: 'Tu plan' })
    expect(within(plan).getByRole('heading', { name: 'Día 1' })).toBeInTheDocument()

    const bajar = within(plan).getAllByRole('button', { name: /^Bajar / })[0]
    const nombre = bajar.getAttribute('aria-label')!.replace('Bajar ', '')
    await usuario.click(bajar)
    expect(within(plan).getByText('Traslado estimado tras tu edición')).toBeInTheDocument()
    expect(within(plan).getAllByRole('button', { name: `Subir ${nombre}` })[0]).toBeEnabled()

    await usuario.click(within(plan).getByRole('button', { name: 'Guardar plan' }))
    expect(within(plan).getByText('Plan guardado en este dispositivo.')).toBeInTheDocument()
    expect(obtenerAlmacen().planes).toHaveLength(1)
    expect(screen.getByRole('heading', { name: 'Mis planes' }).parentElement).toHaveTextContent('Mi plan en Puebla')
  })
})
