import { screen, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { guardarPoi, obtenerAlmacen, recargarAlmacen } from '../almacen/almacen'
import { POIS_DEMO } from '../demo/datos'
import { montar } from '../pruebas/utilidades'

describe('Guardar en mi mapa', () => {
  it('guarda desde la ficha sin cuenta y persiste en el dispositivo', async () => {
    const { usuario } = montar('/lugar/demo-puebla-amparo')
    await usuario.click(await screen.findByRole('button', { name: 'Guardar en mi mapa' }))
    expect(screen.getByRole('button', { name: /Guardado en mi mapa/ })).toBeInTheDocument()
    const crudo = JSON.parse(window.localStorage.getItem('pv360.guardados') ?? '{}')
    expect(Object.keys(crudo)).toEqual(['demo-puebla-amparo'])
  })

  it('Mi mapa agrupa por destino, con etiquetas propias y nota privada', async () => {
    guardarPoi(POIS_DEMO.find((poi) => poi.poi_id === 'demo-puebla-amparo')!)
    guardarPoi(POIS_DEMO.find((poi) => poi.poi_id === 'demo-cholula-museo')!)
    guardarPoi(POIS_DEMO.find((poi) => poi.poi_id === 'demo-cholula-zocalo')!)
    const { usuario } = montar('/mi-mapa')

    expect(await screen.findByRole('heading', { level: 2, name: /Cholula · 2 lugares/ })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: /Ciudad de Puebla · 1 lugar/ })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: '© OpenStreetMap contributors' })).toBeInTheDocument()

    await usuario.click(screen.getByText('Etiquetas y nota de Museo Amparo'))
    const editor = screen.getByText('Etiquetas y nota de Museo Amparo').closest('details')!
    await usuario.type(within(editor).getByLabelText('Nueva etiqueta'), 'arte')
    await usuario.click(within(editor).getByRole('button', { name: /Agregar/ }))
    await usuario.type(within(editor).getByLabelText(/Nota privada/), 'Ir temprano')
    await usuario.click(within(editor).getByRole('button', { name: 'Guardar nota' }))

    expect(obtenerAlmacen().guardados['demo-puebla-amparo'].etiquetas).toEqual(['arte'])
    expect(obtenerAlmacen().guardados['demo-puebla-amparo'].nota).toBe('Ir temprano')

    await usuario.click(screen.getByRole('button', { name: 'arte' }))
    expect(screen.queryByRole('heading', { level: 2, name: /Cholula/ })).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: /Ciudad de Puebla/ })).toBeInTheDocument()
  })

  it('sin almacenamiento disponible no falla y lo avisa', async () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('bloqueado')
    })
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('bloqueado')
    })
    recargarAlmacen()
    const { usuario } = montar('/lugar/demo-puebla-amparo')
    await usuario.click(await screen.findByRole('button', { name: 'Guardar en mi mapa' }))
    expect(screen.getByRole('button', { name: /Guardado en mi mapa/ })).toBeInTheDocument()
    expect(screen.getByText(/no permite guardar datos en este dispositivo/)).toBeInTheDocument()
  })
})
