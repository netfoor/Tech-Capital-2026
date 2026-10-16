import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { montar } from './pruebas/utilidades'

describe('App', () => {
  it('muestra Descubrir en la raíz con la navegación principal', async () => {
    montar('/')
    expect(await screen.findByRole('heading', { level: 1, name: 'Descubre Puebla' })).toBeInTheDocument()
    const nav = screen.getByRole('navigation', { name: 'Principal' })
    for (const nombre of ['Descubrir', 'Mi mapa', 'Planear', 'Mi recorrido']) {
      expect(nav).toHaveTextContent(nombre)
    }
  })

  it('sin API muestra la banda de datos sintéticos', async () => {
    montar('/')
    expect(await screen.findByRole('note', { name: 'DATOS SINTÉTICOS DE DEMOSTRACIÓN' })).toBeInTheDocument()
  })

  it('Mi recorrido es un aviso honesto, sin pedir ubicación', async () => {
    montar('/recorrido')
    expect(screen.getByRole('heading', { level: 1, name: 'Mi recorrido' })).toBeInTheDocument()
    expect(screen.getByText('Esta sección todavía no está disponible.')).toBeInTheDocument()
  })

  it('conserva la entrada de /admin', () => {
    montar('/admin')
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Tablero institucional')
  })
})
