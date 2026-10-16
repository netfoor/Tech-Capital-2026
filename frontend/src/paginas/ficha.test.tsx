import { screen, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { POIDetalle } from '../api/tipos'
import { montar, respuestaJson } from '../pruebas/utilidades'

function atributo(nombre: string) {
  const lista = screen.getByRole('heading', { name: 'Accesibilidad', level: 2 }).parentElement!
  const fila = within(lista)
    .getAllByRole('listitem')
    .find((elemento) => elemento.textContent?.startsWith(nombre))
  if (!fila) throw new Error(`No está el atributo ${nombre}`)
  return fila
}

describe('Ficha de un lugar', () => {
  it('sin dato dice «Sin verificar», nunca «accesible»', async () => {
    montar('/lugar/demo-cholula-mercado')
    expect(await screen.findByRole('heading', { level: 1, name: 'Mercado Municipal de Cholula' })).toBeInTheDocument()
    const fila = atributo('Baño accesible')
    expect(fila).toHaveTextContent('No tenemos este dato todavía')
    expect(fila).toHaveTextContent('Sin verificar')
    expect(screen.queryByText(/^(accesible|sí)$/i, { selector: '.atributo__valor' })).not.toBeInTheDocument()
    expect(screen.getByText('Accesibilidad sin verificar')).toBeInTheDocument()
  })

  it('muestra los 9 atributos con estado, origen y fecha', async () => {
    montar('/lugar/demo-cholula-museo')
    await screen.findByRole('heading', { level: 1, name: 'Museo Regional de Cholula' })
    const fila = atributo('Acceso sin escalones')
    expect(fila).toHaveTextContent('Sí')
    expect(fila).toHaveTextContent('Verificado')
    expect(fila).toHaveTextContent(/Aportado por el equipo verificador/)
    expect(fila).toHaveTextContent(/2026/)
    const lista = screen.getByRole('heading', { name: 'Accesibilidad', level: 2 }).parentElement!
    expect(within(lista).getAllByRole('listitem')).toHaveLength(9)
  })

  it('muestra barreras reportadas, horario con fuente y la etiqueta sintética', async () => {
    montar('/lugar/demo-cholula-convento')
    await screen.findByRole('heading', { level: 1, name: 'Exconvento de San Gabriel Arcángel' })
    expect(atributo('Acceso sin escalones')).toHaveTextContent('Reportado')
    expect(atributo('Rampa')).toHaveTextContent('En moderación')
    expect(screen.getByText('Rampa bloqueada')).toBeInTheDocument()
    expect(screen.getByText(/Fuente: OpenStreetMap/)).toBeInTheDocument()
    expect(screen.getAllByText('Dato sintético').length).toBeGreaterThan(0)
    expect(screen.getByRole('link', { name: /Reportar una barrera/ })).toHaveAttribute('href', '/lugar/demo-cholula-convento/reportar')
  })

  it('con datos reales usa el contrato: valores «si», «limitado» y números en texto', async () => {
    const real: POIDetalle = {
      poi_id: 'osm-n1',
      nombre: 'Lugar real',
      categoria: 'plaza',
      destino_id: 'atlixco',
      corredor_id: null,
      lat: 18.9,
      lon: -98.43,
      costo_rango: null,
      cobertura_accesibilidad: 'parcial',
      is_synthetic: false,
      accesibilidad: {
        acceso_sin_escalones: { valor: 'limitado', estado: 'verificado', origen: 'osm', confianza: 0.6, fecha: '2026-10-10' },
        pendiente_pct: { valor: '8', estado: 'sin_verificar', origen: 'osm', confianza: 0.5, fecha: '2026-10-10' },
        banio_accesible: { valor: null, estado: 'sin_verificar', origen: null, confianza: null, fecha: null },
      },
      descripcion: null,
      direccion: null,
      horario_osm: null,
      fuentes: [{ id: 'osm', nombre: 'OpenStreetMap', url: 'https://www.openstreetmap.org' }],
      barreras_reportadas: [],
    }
    vi.stubGlobal(
      'fetch',
      vi.fn((url: string) => Promise.resolve(url.includes('/destinos') ? respuestaJson({ items: [] }) : respuestaJson(real))),
    )
    montar('/lugar/osm-n1')
    await screen.findByRole('heading', { level: 1, name: 'Lugar real' })
    expect(atributo('Acceso sin escalones')).toHaveTextContent('Limitado')
    expect(atributo('Pendiente del acceso')).toHaveTextContent('8 %')
    expect(atributo('Baño accesible')).toHaveTextContent('Sin verificar')
    expect(screen.queryByRole('note', { name: 'DATOS SINTÉTICOS DE DEMOSTRACIÓN' })).not.toBeInTheDocument()
    expect(screen.getByText(/Sin horario registrado/)).toBeInTheDocument()
  })
})
