import { useCallback, useEffect, useState } from 'react'
import { listarDestinos } from '../api/cliente'
import type { Destino } from '../api/tipos'

export interface Carga<T> {
  datos: T | null
  cargando: boolean
  error: boolean
  reintentar: () => void
}

/** Carga asíncrona con estado de error y reintento. `clave` cambia → se vuelve a pedir. */
export function useCarga<T>(pedir: () => Promise<T>, clave: string): Carga<T> {
  const [estado, setEstado] = useState<{ datos: T | null; cargando: boolean; error: boolean }>({
    datos: null,
    cargando: true,
    error: false,
  })
  const [intento, setIntento] = useState(0)

  useEffect(() => {
    let vigente = true
    setEstado((previo) => ({ ...previo, cargando: true, error: false }))
    pedir()
      .then((datos) => vigente && setEstado({ datos, cargando: false, error: false }))
      .catch(() => vigente && setEstado({ datos: null, cargando: false, error: true }))
    return () => {
      vigente = false
    }
    // `pedir` se recrea en cada render; la clave decide cuándo volver a pedir.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clave, intento])

  const reintentar = useCallback(() => setIntento((n) => n + 1), [])
  return { ...estado, reintentar }
}

let destinosEnMemoria: Promise<Destino[]> | null = null

export function reiniciarDestinos() {
  destinosEnMemoria = null
}

/** Destinos del catálogo; se piden una vez por sesión. */
export function useDestinos(): Record<string, Destino> {
  const [destinos, setDestinos] = useState<Record<string, Destino>>({})
  useEffect(() => {
    let vigente = true
    destinosEnMemoria ??= listarDestinos().catch((error) => {
      destinosEnMemoria = null
      throw error
    })
    destinosEnMemoria
      .then((lista) => {
        if (vigente) setDestinos(Object.fromEntries(lista.map((destino) => [destino.destino_id, destino])))
      })
      .catch(() => undefined)
    return () => {
      vigente = false
    }
  }, [])
  return destinos
}

export function nombreDestino(destinos: Record<string, Destino>, destinoId: string): string {
  return destinos[destinoId]?.nombre ?? destinoId.replace(/-/g, ' ').replace(/^\w/, (letra) => letra.toUpperCase())
}
