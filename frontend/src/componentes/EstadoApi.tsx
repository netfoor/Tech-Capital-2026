import { useEffect, useState } from 'react'
import { obtener } from '../api/cliente'

type Salud = { estado: string; base_de_datos: string }

export function EstadoApi() {
  const [salud, setSalud] = useState<Salud | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    obtener<Salud>('/health').then(setSalud).catch((e: Error) => setError(e.message))
  }, [])

  if (error) return <p role="status">Servicio no disponible: {error}</p>
  if (!salud) return <p role="status">Comprobando el servicio…</p>
  return (
    <p role="status">
      Servicio: {salud.estado} · Base de datos: {salud.base_de_datos}
    </p>
  )
}
