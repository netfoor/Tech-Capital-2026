import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { montar } from '../pruebas/utilidades'

async function nombresDeLugares() {
  const lista = await screen.findByRole('list', { name: 'Lugares' })
  return within(lista)
    .getAllByRole('heading', { level: 3 })
    .map((titulo) => titulo.textContent)
}

describe('Descubrir: filtros', () => {
  it('muestra la lista como vista principal con todos los lugares', async () => {
    montar('/')
    const nombres = await nombresDeLugares()
    expect(nombres.length).toBe(15)
    expect(screen.getByRole('button', { name: /Lista/ })).toHaveAttribute('aria-pressed', 'true')
  })

  it('«Sin escalones» quita lugares con escalones, sin dato o con barrera reportada', async () => {
    const { usuario } = montar('/')
    await nombresDeLugares()
    await usuario.click(screen.getByRole('checkbox', { name: 'Sin escalones' }))
    const nombres = await nombresDeLugares()
    expect(nombres).toContain('Museo Regional de Cholula')
    expect(nombres).toContain('Catedral de Puebla')
    expect(nombres).not.toContain('Santuario de Nuestra Señora de los Remedios')
    expect(nombres).not.toContain('Mercado Municipal de Cholula')
    expect(nombres).not.toContain('Exconvento de San Gabriel Arcángel')
  })

  it('«Solo atributos verificados» deja fuera los datos sin verificar', async () => {
    const { usuario } = montar('/?sin_escalones=true')
    expect(await nombresDeLugares()).toContain('Catedral de Puebla')
    await usuario.click(screen.getByRole('checkbox', { name: /Solo atributos verificados/ }))
    const nombres = await nombresDeLugares()
    expect(nombres).not.toContain('Catedral de Puebla')
    expect(nombres).toContain('Museo Amparo')
  })

  it('combina interés, destino y costo, y lo refleja en la URL', async () => {
    const { usuario } = montar('/')
    await nombresDeLugares()
    await usuario.click(screen.getByRole('button', { name: 'Museo' }))
    expect(screen.getByRole('button', { name: 'Museo' })).toHaveAttribute('aria-pressed', 'true')
    await usuario.selectOptions(await screen.findByLabelText('Destino'), 'puebla')
    expect(await nombresDeLugares()).toEqual(['Museo Amparo'])
    await usuario.selectOptions(screen.getByLabelText('Costo máximo'), 'bajo')
    expect(await screen.findByText(/No encontramos lugares/)).toBeInTheDocument()
  })

  it('el baño accesible solo cuenta si el dato dice «sí»', async () => {
    const { usuario } = montar('/')
    await nombresDeLugares()
    await usuario.click(screen.getByRole('checkbox', { name: 'Baño accesible' }))
    const nombres = await nombresDeLugares()
    expect(nombres).toContain('Museo Amparo')
    expect(nombres).not.toContain('Zócalo de San Pedro Cholula')
  })

  it('el mapa no reemplaza a la lista y muestra la atribución', async () => {
    const { usuario } = montar('/')
    await nombresDeLugares()
    await usuario.click(screen.getByRole('button', { name: /Mapa/ }))
    expect(screen.getByRole('link', { name: '© OpenStreetMap contributors' })).toBeInTheDocument()
    expect(await nombresDeLugares()).toHaveLength(15)
  })
})
