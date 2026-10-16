import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { iniciarSesionLocal } from '../almacen/almacen'
import { montar, respuestaJson } from '../pruebas/utilidades'

describe('Reportar una barrera', () => {
  it('sin tipo muestra un error comprensible y lleva el foco al campo', async () => {
    const { usuario } = montar('/lugar/demo-cholula-museo/reportar')
    await usuario.click(await screen.findByRole('button', { name: /Enviar reporte/ }))
    expect(screen.getByRole('alert')).toHaveTextContent('Elige el tipo de barrera para poder enviar el reporte.')
    expect(screen.getByRole('radio', { name: 'Escalones' })).toHaveFocus()
  })

  it('rechaza una descripción demasiado larga', async () => {
    const { usuario } = montar('/lugar/demo-cholula-museo/reportar')
    await usuario.click(await screen.findByRole('radio', { name: 'Escalones' }))
    const campo = screen.getByLabelText('Descripción (opcional)')
    await usuario.click(campo)
    await usuario.paste('x'.repeat(501))
    await usuario.click(screen.getByRole('button', { name: /Enviar reporte/ }))
    expect(screen.getByRole('alert')).toHaveTextContent('500 caracteres o menos')
    expect(campo).toHaveAttribute('aria-invalid', 'true')
  })

  it('en modo de demostración dice que el reporte quedó solo en el dispositivo', async () => {
    const { usuario } = montar('/lugar/demo-cholula-museo/reportar')
    await usuario.click(await screen.findByRole('radio', { name: 'Rampa bloqueada' }))
    await usuario.click(screen.getByRole('button', { name: /Enviar reporte/ }))
    expect(await screen.findByText(/se guardó solo en este dispositivo/)).toBeInTheDocument()
    expect(JSON.parse(window.localStorage.getItem('pv360.envios') ?? '[]')).toHaveLength(1)
  })

  it('con la API real y sesión envía el contrato exacto', async () => {
    iniciarSesionLocal({ token: 'tkn', usuario: { id: 'u1', correo: 'ana@ejemplo.mx', rol: 'visitante', nombre_visible: null } })
    const fetchFalso = vi.fn((url: string, opciones?: RequestInit) => {
      if (url.endsWith('/reports/barrier')) return Promise.resolve(respuestaJson({ report_id: 1, moderation_case_id: 1, estado: 'en_moderacion' }, 201))
      if (url.includes('/pois/')) return Promise.resolve(respuestaJson({ poi_id: 'osm-1', nombre: 'Museo', is_synthetic: false }))
      void opciones
      return Promise.resolve(respuestaJson({ items: [] }))
    })
    vi.stubGlobal('fetch', fetchFalso)
    const { usuario } = montar('/lugar/osm-1/reportar')
    await usuario.click(await screen.findByRole('radio', { name: 'Escalones' }))
    await usuario.type(screen.getByLabelText('Descripción (opcional)'), 'Tres escalones en la entrada')
    await usuario.click(screen.getByRole('button', { name: /Enviar reporte/ }))
    expect(await screen.findByText(/Recibimos tu reporte/)).toBeInTheDocument()
    const llamada = fetchFalso.mock.calls.find(([url]) => String(url).endsWith('/reports/barrier'))!
    expect(JSON.parse(String(llamada[1]?.body))).toEqual({ poi_id: 'osm-1', tipo: 'escalones', descripcion: 'Tres escalones en la entrada' })
    expect((llamada[1]?.headers as Record<string, string>).Authorization).toBe('Bearer tkn')
  })

  it('con la API real y sin sesión lo guarda en el dispositivo y ofrece crear cuenta', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(respuestaJson({ poi_id: 'osm-1', nombre: 'Museo', is_synthetic: false }))))
    const { usuario } = montar('/lugar/osm-1/reportar')
    await usuario.click(await screen.findByRole('radio', { name: 'Superficie en mal estado' }))
    await usuario.click(screen.getByRole('button', { name: /Enviar reporte/ }))
    expect(await screen.findByText(/necesitas una cuenta/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Iniciar sesión o crear cuenta' })).toBeInTheDocument()
  })
})

describe('Reseña por dimensiones', () => {
  it('solo la experiencia global es obligatoria', async () => {
    const { usuario } = montar('/lugar/demo-cholula-museo/resena')
    await usuario.click(await screen.findByRole('button', { name: /Enviar calificación/ }))
    expect(screen.getByRole('alert')).toHaveTextContent('Experiencia en general')
    const global = screen.getByRole('group', { name: /Experiencia en general/ })
    expect(global).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getAllByRole('radio', { name: /muy malo/ })[0]).toHaveFocus()

    await usuario.click(screen.getAllByRole('radio', { name: /bueno/ })[0])
    await usuario.click(screen.getByRole('button', { name: /Enviar calificación/ }))
    expect(await screen.findByText(/tu calificación se guardó solo en este dispositivo/)).toBeInTheDocument()
    const [envio] = JSON.parse(window.localStorage.getItem('pv360.envios') ?? '[]')
    expect(envio.datos).toEqual({ poi_id: 'demo-cholula-museo', dimensiones: { global: 4 } })
  })

  it('cada dimensión ofrece de 1 a 5 con su significado', async () => {
    montar('/lugar/demo-cholula-museo/resena')
    const grupo = await screen.findByRole('group', { name: 'Limpieza' })
    expect(grupo.querySelectorAll('input[type="radio"]')).toHaveLength(5)
    expect(grupo).toHaveTextContent('5, excelente')
  })
})
