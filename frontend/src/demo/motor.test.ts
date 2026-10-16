import { describe, expect, it } from 'vitest'
import type { Restricciones } from '../api/tipos'
import { aNumero, banioAccesible, evaluarRestricciones, sinEscalones } from '../dominio/accesibilidad'
import { POIS_DEMO } from './datos'
import { listarPois, planearDesdeGuardados, recomendar } from './motor'

const COMBINACIONES: Restricciones[] = [
  { sin_escalones: true },
  { banio_accesible: true },
  { pendiente_max_pct: 4 },
  { sin_escalones: true, banio_accesible: true },
  { sin_escalones: true, descansos_cada_min: 30, pendiente_max_pct: 6 },
]

describe('datos de demostración', () => {
  it('todos están marcados como sintéticos y traen los 9 atributos', () => {
    for (const poi of POIS_DEMO) {
      expect(poi.is_synthetic).toBe(true)
      expect(Object.keys(poi.accesibilidad)).toHaveLength(9)
    }
  })
})

describe('recomendación local', () => {
  it.each(COMBINACIONES)('nunca viola una restricción indispensable (%o)', (restricciones) => {
    for (const horas of [2, 4, 8]) {
      const plan = recomendar({ horas_disponibles: horas, restricciones, incluir_alternativos: true })
      for (const poi of [...plan.paradas.map((parada) => parada.poi), ...plan.alternativos]) {
        if (restricciones.sin_escalones) expect(sinEscalones(poi)).toBe(true)
        if (restricciones.banio_accesible) expect(banioAccesible(poi)).toBe(true)
        if (restricciones.pendiente_max_pct !== undefined) {
          expect(aNumero(poi.accesibilidad.pendiente_pct?.valor ?? null)).not.toBeNull()
          expect(aNumero(poi.accesibilidad.pendiente_pct!.valor)!).toBeLessThanOrEqual(restricciones.pendiente_max_pct)
        }
        expect(evaluarRestricciones(poi, restricciones).cumple).toBe(true)
      }
      const usados = plan.paradas.reduce((suma, parada) => suma + parada.traslado_min + parada.estancia_min, 0)
      expect(usados).toBeLessThanOrEqual(horas * 60)
    }
  })

  it('escena de la demo: 4 h sin escalones, descansos y costo bajo', () => {
    const plan = recomendar({
      horas_disponibles: 4,
      presupuesto: 'bajo',
      restricciones: { sin_escalones: true, descansos_cada_min: 30 },
      incluir_alternativos: true,
    })
    expect(plan.paradas.length).toBeGreaterThan(0)
    expect(plan.explicacion).toMatch(/necesidades de acceso/)
    for (const parada of plan.paradas) expect(parada.motivo).not.toBe('')
    const motivos = Object.fromEntries(plan.no_incluidos.map((elemento) => [elemento.poi_id, elemento.motivo]))
    expect(motivos['demo-cholula-santuario']).toBe('Tiene escalones en el acceso.')
    expect(motivos['demo-cholula-convento']).toBe('Hay una barrera de escalones reportada.')
    expect(motivos['demo-cholula-mercado']).toBe('No sabemos si tiene acceso sin escalones.')
    expect(plan.alternativos.every((poi) => poi.destino_id !== plan.paradas[0].poi.destino_id)).toBe(true)
  })

  it('un lugar sin dato nunca cuenta como accesible', () => {
    const mercado = POIS_DEMO.find((poi) => poi.poi_id === 'demo-cholula-mercado')!
    expect(sinEscalones(mercado)).toBe(false)
    expect(banioAccesible(mercado)).toBe(false)
  })

  it('«limitado» no cumple una necesidad indispensable', () => {
    const poi = { ...POIS_DEMO[0], accesibilidad: { ...POIS_DEMO[0].accesibilidad, acceso_sin_escalones: { valor: 'limitado', estado: 'verificado' as const, origen: 'osm', confianza: 0.9, fecha: '2026-10-01' } } }
    expect(evaluarRestricciones(poi, { sin_escalones: true }).cumple).toBe(false)
  })
})

describe('plan desde guardados', () => {
  it('reparte por días, respeta el tiempo y explica lo que no entra', () => {
    const ids = POIS_DEMO.slice(0, 9).map((poi) => poi.poi_id)
    const plan = planearDesdeGuardados({ poi_ids: ids, dias: 2, horas_por_dia: 4, restricciones: { sin_escalones: true } })
    expect(plan.dias.length).toBeGreaterThan(0)
    expect(plan.dias.length).toBeLessThanOrEqual(2)
    for (const dia of plan.dias) {
      const usados = dia.paradas.reduce((suma, parada) => suma + parada.traslado_min + parada.estancia_min, 0)
      expect(usados).toBeLessThanOrEqual(4 * 60)
      for (const parada of dia.paradas) expect(sinEscalones(parada.poi)).toBe(true)
    }
    const incluidos = plan.dias.flatMap((dia) => dia.paradas.map((parada) => parada.poi.poi_id))
    for (const id of ids) {
      expect(incluidos.includes(id) || plan.no_incluidos.some((elemento) => elemento.poi_id === id)).toBe(true)
    }
    expect(plan.alternativos.length).toBeLessThanOrEqual(2)
    for (const alternativo of plan.alternativos) expect(ids).not.toContain(alternativo.poi_id)
  })
})

describe('filtros locales', () => {
  it('solo verificados exige el estado verificado', () => {
    const todos = listarPois({ sin_escalones: true }).items
    const verificados = listarPois({ sin_escalones: true, solo_verificados: true }).items
    expect(verificados.length).toBeLessThan(todos.length)
    for (const poi of verificados) expect(poi.accesibilidad.acceso_sin_escalones?.estado).toBe('verificado')
  })
})
