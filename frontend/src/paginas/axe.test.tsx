import { screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { describe, expect, it } from 'vitest'
import { cambiarPreferencias, guardarPoi } from '../almacen/almacen'
import { POIS_DEMO } from '../demo/datos'
import { montar } from '../pruebas/utilidades'

// En jsdom axe no puede medir el contraste (no hay dibujo); el contraste se prueba en tokens.test.ts.
const opciones = { rules: { 'color-contrast': { enabled: false } } }

describe('axe sin violaciones en los flujos P0', () => {
  it('Descubrir', async () => {
    const { container } = montar('/')
    await screen.findByRole('list', { name: 'Lugares' })
    expect(await axe(container, opciones)).toHaveNoViolations()
  })

  it('Descubrir con mapa y filtros activos', async () => {
    const { container } = montar('/?vista=mapa&sin_escalones=true&categoria=museo')
    await screen.findByRole('list', { name: 'Lugares' })
    expect(await axe(container, opciones)).toHaveNoViolations()
  })

  it('Ficha de un lugar', async () => {
    const { container } = montar('/lugar/demo-cholula-convento')
    await screen.findByRole('heading', { level: 1, name: 'Exconvento de San Gabriel Arcángel' })
    expect(await axe(container, opciones)).toHaveNoViolations()
  })

  it('Mi mapa con lugares', async () => {
    guardarPoi(POIS_DEMO[0])
    guardarPoi(POIS_DEMO[8])
    const { container } = montar('/mi-mapa')
    await screen.findByRole('heading', { level: 1, name: 'Mi mapa' })
    expect(await axe(container, opciones)).toHaveNoViolations()
  })

  it('Planear con un itinerario', async () => {
    const { container, usuario } = montar('/planear')
    await usuario.click(screen.getByRole('checkbox', { name: 'Evitar escalones' }))
    await usuario.click(screen.getByRole('button', { name: /Crear mi plan/ }))
    await screen.findByRole('heading', { name: 'Tu plan' })
    expect(await axe(container, opciones)).toHaveNoViolations()
  })

  it('Reportar una barrera con errores', async () => {
    const { container, usuario } = montar('/lugar/demo-cholula-museo/reportar')
    await usuario.click(await screen.findByRole('button', { name: /Enviar reporte/ }))
    expect(await axe(container, opciones)).toHaveNoViolations()
  })

  it('Reseña por dimensiones con errores', async () => {
    const { container, usuario } = montar('/lugar/demo-cholula-museo/resena')
    await usuario.click(await screen.findByRole('button', { name: /Enviar calificación/ }))
    expect(await axe(container, opciones)).toHaveNoViolations()
  })

  it('Cuenta, Mi recorrido y lenguaje claro', async () => {
    cambiarPreferencias({ lenguajeClaro: true })
    const cuenta = montar('/cuenta')
    expect(await axe(cuenta.container, opciones)).toHaveNoViolations()
    cuenta.unmount()
    const recorrido = montar('/recorrido')
    expect(await axe(recorrido.container, opciones)).toHaveNoViolations()
  })
})
