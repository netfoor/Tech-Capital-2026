const BASE = import.meta.env.VITE_API_URL ?? '/api'

export async function obtener<T>(ruta: string): Promise<T> {
  const respuesta = await fetch(`${BASE}${ruta}`)
  if (!respuesta.ok) throw new Error(`Error ${respuesta.status} en ${ruta}`)
  return (await respuesta.json()) as T
}
