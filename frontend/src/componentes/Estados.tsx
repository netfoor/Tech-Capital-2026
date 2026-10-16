import type { CoberturaAccesibilidad, EstadoAtributo } from '../api/tipos'
import { useTextos } from '../i18n/textos'
import { Icono, type NombreIcono } from './Icono'

const ICONO_ESTADO: Record<EstadoAtributo, NombreIcono> = {
  verificado: 'verificado',
  sin_verificar: 'sinVerificar',
  reportado: 'reportado',
  en_moderacion: 'moderacion',
}

/** Estado de un atributo: ícono + texto + color. Nunca solo color. */
export function PastillaEstado({ estado }: { estado: EstadoAtributo }) {
  const t = useTextos()
  return (
    <span className={`pastilla pastilla--${estado}`}>
      <Icono nombre={ICONO_ESTADO[estado]} className="pastilla__icono" />
      {t.estados[estado]}
    </span>
  )
}

const ESTADO_COBERTURA: Record<CoberturaAccesibilidad, EstadoAtributo> = {
  verificada: 'verificado',
  parcial: 'en_moderacion',
  sin_verificar: 'sin_verificar',
}

export function PastillaCobertura({ cobertura }: { cobertura: CoberturaAccesibilidad }) {
  const t = useTextos()
  const estado = ESTADO_COBERTURA[cobertura] ?? 'sin_verificar'
  const clase = cobertura === 'parcial' ? 'pastilla--neutra' : `pastilla--${estado}`
  return (
    <span className={`pastilla ${clase}`}>
      <Icono nombre={cobertura === 'parcial' ? 'info' : ICONO_ESTADO[estado]} className="pastilla__icono" />
      {t.cobertura[cobertura] ?? t.cobertura.sin_verificar}
    </span>
  )
}

export function PastillaSintetica() {
  const t = useTextos()
  return (
    <span className="pastilla pastilla--sintetico">
      <Icono nombre="info" className="pastilla__icono" />
      {t.sintetico.etiqueta}
    </span>
  )
}
