import { useAlmacen } from '../almacen/almacen'
import { claro, es, type Textos } from './es'

function mezclar<T>(base: T, cambios: unknown): T {
  if (!cambios || typeof cambios !== 'object' || Array.isArray(cambios)) return (cambios ?? base) as T
  const resultado = { ...(base as Record<string, unknown>) }
  for (const [clave, valor] of Object.entries(cambios as Record<string, unknown>)) {
    const actual = resultado[clave]
    resultado[clave] =
      actual && typeof actual === 'object' && !Array.isArray(actual) && typeof valor === 'object'
        ? mezclar(actual, valor)
        : valor
  }
  return resultado as T
}

const textosClaros: Textos = mezclar(es, claro)

export function textosPara(lenguajeClaro: boolean): Textos {
  return lenguajeClaro ? textosClaros : es
}

/** Cadenas de la interfaz según la preferencia de lenguaje claro. */
export function useTextos(): Textos {
  const { preferencias } = useAlmacen()
  return textosPara(preferencias.lenguajeClaro)
}
