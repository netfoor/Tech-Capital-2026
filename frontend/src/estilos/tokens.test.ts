import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

const tokens = readFileSync(join(process.cwd(), 'src/estilos/tokens.css'), 'utf-8')

const valores = Object.fromEntries(
  [...tokens.matchAll(/--(color-[\w-]+):\s*(#[0-9a-f]{6})/gi)].map(([, nombre, hex]) => [nombre, hex]),
)

function luminancia(hex: string): number {
  const canales = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
  const [r, g, b] = canales.map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4))
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

function contraste(a: string, b: string): number {
  const [claro, oscuro] = [luminancia(a), luminancia(b)].sort((x, y) => y - x)
  return (claro + 0.05) / (oscuro + 0.05)
}

const c = (nombre: string) => {
  if (nombre === 'blanco') return '#ffffff'
  const valor = valores[`color-${nombre}`]
  if (!valor) throw new Error(`Falta el token --color-${nombre}`)
  return valor
}

// Pares de docs/diseno.md §2: texto ≥ 4.5:1; bordes de controles ≥ 3:1.
const TEXTO: [string, string][] = [
  ['texto', 'fondo'],
  ['texto', 'superficie'],
  ['texto', 'superficie-alta'],
  ['texto-suave', 'fondo'],
  ['texto-suave', 'superficie'],
  ['texto-suave', 'superficie-alta'],
  ['primario', 'superficie'],
  ['primario', 'fondo'],
  ['primario-fuerte', 'primario-suave'],
  ['blanco', 'primario'],
  ['blanco', 'acento'],
  ['acento-fuerte', 'acento-suave'],
  ['verificado', 'verificado-fondo'],
  ['sin-verificar', 'sin-verificar-fondo'],
  ['reportado', 'reportado-fondo'],
  ['reportado', 'superficie'],
  ['moderacion', 'moderacion-fondo'],
  ['texto', 'sintetico'],
  ['texto', 'sintetico-raya'],
]

const CONTROLES: [string, string][] = [
  ['borde-control', 'superficie'],
  ['borde-control', 'fondo'],
  ['foco', 'fondo'],
  ['foco', 'superficie'],
]

describe('tokens de color', () => {
  it.each(TEXTO)('%s sobre %s cumple AA para texto (4.5:1)', (frente, fondo) => {
    expect(contraste(c(frente), c(fondo))).toBeGreaterThanOrEqual(4.5)
  })

  it.each(CONTROLES)('%s sobre %s cumple 3:1 para componentes', (frente, fondo) => {
    expect(contraste(c(frente), c(fondo))).toBeGreaterThanOrEqual(3)
  })
})
