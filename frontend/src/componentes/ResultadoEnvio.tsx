import { Link, useLocation } from 'react-router'
import type { ResultadoEnvio } from '../api/tipos'
import { useTextos } from '../i18n/textos'
import { Aviso } from './Avisos'

interface Props {
  titulo: string
  resultado: ResultadoEnvio
  textos: { servidor: string; demo: string; sinSesion: string }
  rutaFicha: string
}

/** Confirmación de un envío. Si quedó solo en el dispositivo, dice por qué y qué hacer. */
export function ResultadoLocal({ titulo, resultado, textos, rutaFicha }: Props) {
  const t = useTextos()
  const { pathname } = useLocation()
  const tono = resultado.destino === 'servidor' ? 'exito' : resultado.motivo === 'sin_sesion' ? 'alerta' : 'sintetico'
  const mensaje = resultado.destino === 'servidor' ? textos.servidor : resultado.motivo === 'sin_sesion' ? textos.sinSesion : textos.demo
  return (
    <div className="pila-grande" style={{ maxWidth: '40rem' }}>
      <h1>{titulo}</h1>
      <Aviso tono={tono} rol="status">
        <p>{mensaje}</p>
      </Aviso>
      <div className="acciones">
        {resultado.motivo === 'sin_sesion' && (
          <Link className="boton boton--principal" to={`/cuenta?volver=${encodeURIComponent(pathname)}`}>
            {t.cuenta.irACuenta}
          </Link>
        )}
        <Link className={`boton ${resultado.motivo === 'sin_sesion' ? 'boton--secundario' : 'boton--principal'}`} to={rutaFicha}>
          {t.reportar.volverFicha}
        </Link>
      </div>
    </div>
  )
}
