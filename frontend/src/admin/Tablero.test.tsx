import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { Tablero } from './Tablero'

const ficha = (metric_id: string, nombre: string) => ({
  metric_id,
  nombre,
  pregunta: '¿Pregunta?',
  formula: `Fórmula de ${nombre}`,
  unidad: 'porcentaje',
  denominador: 'Denominador',
  fuentes: ['sectur-ot-2026-06'],
  limitaciones: `Limitación de ${nombre}`,
  procedencia: 'medido',
  version: '1',
  k_minimo: null,
  decision_potencial: 'Decidir',
})

const fuente = {
  fuente_id: 'sectur-ot-2026-06',
  nombre: 'Observatorio Turístico',
  institucion: 'Secretaría',
  url: 'https://ejemplo.mx/ot.pdf',
  fecha_consulta: '2026-10-15',
  sha256: 'abcdef0123456789',
}

const destino = (nombre: string, ocupacion: number, candidato: boolean) => ({
  destino_id: nombre.toLowerCase(),
  centro_ot: nombre,
  nombre,
  ocupacion_pct: ocupacion,
  cuartos_libres_dia: 100,
  estadia_noches: 1.8,
  llegadas: 1000,
  afluencia_estimada: 2222,
  meses_con_dato: 12,
  crecimiento_llegadas_pct: null,
  crecimiento_motivo: 'sin evidencia suficiente',
  participacion_pct: 50,
  poi_catalogo: { real: 3, sintetico: 0 },
  candidato,
  serie_ocupacion: [],
})

const OFERTA = {
  modulo: 'oferta_demanda',
  is_synthetic: false,
  ventana: { desde: '2025-07', hasta: '2026-06', meses: 12 },
  estado: { ocupacion_pct: 51.8, cuartos_libres_dia: 11479, estadia_noches: 1.84, origen: 'fila «Estado» de la fuente' },
  hhi: {
    ventana_12m: 3114.9,
    centros: 18,
    cobertura_estado_pct: 87.3,
    serie_anual: [
      { anio: 2025, hhi: 3078.2, meses: 12, centros: 18, parcial: false },
      { anio: 2026, hhi: 3209.4, meses: 6, centros: 18, parcial: true },
    ],
  },
  mediana_cuartos_libres_dia: 100,
  destinos: [destino('Cholula', 57.8, false), destino('Atlixco', 44.8, true)],
  candidatos: [
    {
      destino_id: 'atlixco',
      nombre: 'Atlixco',
      ocupacion_pct: 44.8,
      cuartos_libres_dia: 436,
      poi_catalogo: { real: 3, sintetico: 0 },
      motivo: 'Ocupación 44.8 % menor que la del Estado',
    },
  ],
  campos: [],
  fichas: [ficha('ocupacion_12m', 'Ocupación hotelera'), ficha('hhi_llegadas', 'Índice HHI')],
  fuentes: [fuente],
  calculado_en: '2026-10-16T12:00:00+00:00',
}

const PANORAMA = {
  modulo: 'panorama',
  k_minimo: 10,
  aviso: 'Muestra de la app.',
  grupos: [
    {
      destino_id: 'cholula',
      nombre: 'Cholula',
      is_synthetic: true,
      suprimido: false,
      supresion_complementaria: false,
      personas: 15,
      visitas_observadas: 30,
      confianza_media: 0.8,
      cobertura_poi_pct: 40,
      permanencia: { suprimido: false, n: 30, p25_min: 20, mediana_min: 35, p75_min: 50 },
    },
    {
      destino_id: 'atlixco',
      nombre: 'Atlixco',
      is_synthetic: true,
      suprimido: true,
      supresion_complementaria: false,
      personas: null,
      visitas_observadas: null,
      confianza_media: null,
      cobertura_poi_pct: null,
      permanencia: { suprimido: true, n: null, p25_min: null, mediana_min: null, p75_min: null },
    },
  ],
  hay_reales: false,
  hay_sinteticos: true,
  fichas: [ficha('visitas_observadas', 'Visitas observadas')],
  fuentes: [],
  calculado_en: '2026-10-16T12:00:00+00:00',
}

const CASOS = {
  items: [
    {
      id: 7,
      poi_id: 'osm-n1',
      tipo: 'escalones',
      atributo: 'acceso_sin_escalones',
      estado: 'abierto',
      descripcion: 'Escalón en la entrada',
      creado_en: '2026-10-16T10:00:00+00:00',
    },
  ],
}

function respuesta(cuerpo: unknown, estado = 200) {
  return Promise.resolve(new Response(JSON.stringify(cuerpo), { status: estado }))
}

let llamadas: { url: string; init?: RequestInit }[] = []

function simularApi() {
  llamadas = []
  vi.stubGlobal(
    'fetch',
    vi.fn((url: string, init?: RequestInit) => {
      llamadas.push({ url, init })
      if (url.endsWith('/auth/login'))
        return respuesta({
          access_token: 'token-demo',
          usuario: { id: 'u1', correo: 'analista@ejemplo.mx', rol: 'analista', nombre_visible: 'Analista' },
        })
      if (url.includes('/b2b/supply-demand')) return respuesta(OFERTA)
      if (url.includes('modulo=panorama')) return respuesta(PANORAMA)
      if (url.includes('/decision'))
        return respuesta({
          id: 7,
          estado: 'aceptado',
          atributo_actualizado: { atributo: 'acceso_sin_escalones', valor: 'no', estado: 'reportado' },
        })
      if (url.includes('/moderation')) return respuesta(CASOS)
      return respuesta({ detail: 'no encontrado' }, 404)
    }),
  )
}

function montar(ruta = '/admin') {
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <Routes>
        <Route path="/admin/*" element={<Tablero />} />
      </Routes>
    </MemoryRouter>,
  )
}

async function entrar() {
  fireEvent.change(screen.getByLabelText('Correo'), { target: { value: 'analista@ejemplo.mx' } })
  fireEvent.change(screen.getByLabelText('Contraseña'), { target: { value: 'contrasena' } })
  fireEvent.click(screen.getByRole('button', { name: 'Entrar' }))
}

describe('Tablero institucional', () => {
  beforeEach(() => {
    sessionStorage.clear()
    simularApi()
  })
  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('pide iniciar sesión y abre Oferta–demanda con datos reales', async () => {
    montar()
    expect(screen.getByRole('heading', { name: 'Tablero institucional' })).toBeInTheDocument()
    await entrar()
    expect(await screen.findByRole('heading', { level: 2, name: 'Oferta–demanda' })).toBeInTheDocument()
    expect(await screen.findByText('3,115')).toBeInTheDocument()
    expect(screen.getByText(/Atlixco/, { selector: 'strong' })).toBeInTheDocument()
    // La petición lleva el token.
    const pedido = llamadas.find((l) => l.url.includes('/b2b/supply-demand'))
    expect((pedido?.init?.headers as Record<string, string>).Authorization).toBe('Bearer token-demo')
    // Datos reales: sin banda sintética.
    expect(screen.queryByText('DATOS SINTÉTICOS DE DEMOSTRACIÓN')).not.toBeInTheDocument()
  })

  it('cada gráfico tiene ficha metodológica y tabla de datos alternativa', async () => {
    montar()
    await entrar()
    const grafico = await screen.findByRole('img', { name: /Ocupación hotelera por destino/ })
    expect(grafico).toBeInTheDocument()
    const tarjeta = grafico.closest('section')!
    expect(within(tarjeta).getByText('Fórmula de Ocupación hotelera')).toBeInTheDocument()
    expect(within(tarjeta).getByText('Limitación de Ocupación hotelera')).toBeInTheDocument()
    fireEvent.click(within(tarjeta).getByRole('button', { name: 'Ver tabla de datos' }))
    const tabla = within(tarjeta).getByRole('table')
    expect(within(tabla).getByRole('rowheader', { name: 'Atlixco' })).toBeInTheDocument()
    expect(within(tabla).getAllByText('Sin evidencia suficiente').length).toBe(2)
  })

  it('la vista técnica muestra denominador y SHA-256', async () => {
    montar()
    await entrar()
    await screen.findByRole('img', { name: /Ocupación hotelera por destino/ })
    expect(screen.queryAllByText(/SHA-256/).length).toBe(0)
    fireEvent.click(screen.getByRole('radio', { name: 'Técnica' }))
    expect(screen.getAllByText(/SHA-256/).length).toBeGreaterThan(0)
    expect(screen.getByRole('heading', { name: /Vista técnica/ })).toBeInTheDocument()
  })

  it('marca lo sintético y muestra la supresión en Panorama', async () => {
    montar('/admin/panorama')
    await entrar()
    expect(await screen.findByText('DATOS SINTÉTICOS DE DEMOSTRACIÓN')).toBeInTheDocument()
    expect(screen.getByText(/Datos reales: sin evidencia suficiente/)).toBeInTheDocument()
    expect(screen.getAllByText('Suprimido (n < k)').length).toBeGreaterThan(0)
  })

  it('modera un caso desde la cola y avisa del cambio en la ficha', async () => {
    montar('/admin/moderacion')
    await entrar()
    fireEvent.click(await screen.findByRole('button', { name: 'Aceptar caso 7' }))
    expect(await screen.findByText(/Caso 7 aceptado\. La ficha cambió/)).toBeInTheDocument()
    const decision = llamadas.find((l) => l.url.includes('/moderation/7/decision'))
    expect(JSON.parse(String(decision?.init?.body))).toEqual({ decision: 'aceptar' })
  })

  it('rechaza cuentas sin rol del tablero', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        respuesta({
          access_token: 't',
          usuario: { id: 'u2', correo: 'ana@ejemplo.mx', rol: 'visitante', nombre_visible: null },
        }),
      ),
    )
    montar()
    await entrar()
    await waitFor(() =>
      expect(screen.getByRole('alert')).toHaveTextContent('no tiene acceso al tablero'),
    )
  })
})
