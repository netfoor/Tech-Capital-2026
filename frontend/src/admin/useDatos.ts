import { useCallback, useEffect, useState } from 'react'
import { obtener } from './api'

export function useDatos<T>(ruta: string, token: string, onNoAutorizado: () => void) {
  const [datos, setDatos] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [version, setVersion] = useState(0)

  useEffect(() => {
    let vigente = true
    obtener<T>(ruta, token)
      .then((d) => {
        if (vigente) {
          setDatos(d)
          setError(null)
        }
      })
      .catch((e: Error & { estado?: number }) => {
        if (!vigente) return
        if (e.estado === 401) onNoAutorizado()
        setError(e.message)
      })
    return () => {
      vigente = false
    }
  }, [ruta, token, version, onNoAutorizado])

  const recargar = useCallback(() => setVersion((v) => v + 1), [])
  return { datos, error, recargar }
}
