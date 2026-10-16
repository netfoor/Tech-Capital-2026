import type { AtributoAccesibilidad, DatoAccesibilidad, RangoCosto } from '../api/tipos'
import type { Textos } from '../i18n/es'
import { aNumero } from './accesibilidad'
import { fechaCorta } from './tiempo'

export function textoCategoria(t: Textos, categoria: string): string {
  const conocido = t.categorias[categoria]
  if (conocido) return conocido
  const texto = categoria.replace(/_/g, ' ')
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

export function textoCosto(t: Textos, costo: string | null): string {
  if (costo && costo in t.costos) return t.costos[costo as RangoCosto]
  return t.costoDesconocido
}

/** Texto del valor de un atributo. Sin dato → «No tenemos este dato todavía». Nunca «accesible». */
export function textoValor(t: Textos, atributo: AtributoAccesibilidad, dato: DatoAccesibilidad): string {
  const { valor } = dato
  if (valor === null || valor === undefined || valor === '') return t.ficha.noTenemos
  if (typeof valor === 'boolean') return valor ? t.ficha.si : t.ficha.no
  if (atributo === 'pendiente_pct' || atributo === 'numero_escalones') {
    const numero = aNumero(valor)
    if (numero !== null) return atributo === 'pendiente_pct' ? t.ficha.porcentaje(numero) : t.ficha.escalones(numero)
  }
  const texto = String(valor).trim()
  const binario = texto.toLowerCase()
  if (binario === 'si' || binario === 'sí') return t.ficha.si
  if (binario === 'no') return t.ficha.no
  if (binario === 'limitado') return t.ficha.limitado
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

export function textoOrigen(t: Textos, dato: DatoAccesibilidad): string | null {
  const partes: string[] = []
  if (dato.origen) partes.push(t.ficha.aportadoPor(t.origenes[dato.origen] ?? dato.origen.replace(/_/g, ' ')))
  if (dato.fecha) partes.push(t.ficha.fechaDato(fechaCorta(dato.fecha)))
  if (dato.confianza !== null && dato.confianza !== undefined && dato.origen) partes.push(`(${t.ficha.confianza(dato.confianza)})`)
  return partes.length ? partes.join(' ') : null
}

export const CATEGORIAS = ['museo', 'templo', 'zona_arqueologica', 'mirador', 'mercado', 'plaza', 'artesanias', 'biblioteca']
