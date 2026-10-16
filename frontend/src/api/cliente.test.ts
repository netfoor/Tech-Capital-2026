import { describe, expect, it, vi } from 'vitest'
import { respuestaJson } from '../pruebas/utilidades'
import { listarDestinos, listarPois, obtenerPoi } from './cliente'
import { obtenerModo } from './modo'

describe('cliente de la API', () => {
  it('lee /destinos con la forma {items}', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(respuestaJson({ items: [{ destino_id: 'atlixco', nombre: 'Atlixco', pueblo_magico: true, lat: 1, lon: 2, zona: null }] }))))
    expect((await listarDestinos()).map((destino) => destino.destino_id)).toEqual(['atlixco'])
    expect(obtenerModo().origen).toBe('api')
  })

  it('manda los filtros como parámetros y omite los vacíos', async () => {
    const fetchFalso = vi.fn(() => Promise.resolve(respuestaJson({ items: [], total: 0 })))
    vi.stubGlobal('fetch', fetchFalso)
    await listarPois({ q: '', sin_escalones: true, solo_verificados: false, costo_max: 'bajo', limit: 50 })
    expect(fetchFalso).toHaveBeenCalledWith('/api/pois?sin_escalones=true&costo_max=bajo&limit=50', expect.anything())
  })

  it('si la ruta no existe todavía («Not Found»), cambia al modo de demostración', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(respuestaJson({ detail: 'Not Found' }, 404))))
    const lista = await listarPois()
    expect(lista.items.every((poi) => poi.is_synthetic)).toBe(true)
    expect(obtenerModo()).toEqual({ origen: 'demo', vioSinteticos: true })
  })

  it('un lugar inexistente en la API real devuelve null sin activar la demostración', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(respuestaJson({ detail: 'Lugar no encontrado' }, 404))))
    expect(await obtenerPoi('osm-x')).toBeNull()
    expect(obtenerModo().origen).not.toBe('demo')
  })

  it('si la API da error 5xx o no hay red, usa la demostración', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(new Response('', { status: 502 }))))
    expect((await listarPois()).total).toBeGreaterThan(0)
    expect(obtenerModo().origen).toBe('demo')
  })
})
