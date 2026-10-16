import { useId, useState, type ReactNode } from 'react'
import type { Ficha, Fuente } from './api'
import { entero, SIN_DATO, uno } from './formato'
import { useVista } from './vista'

export function BandaSintetica({ children }: { children?: ReactNode }) {
  return (
    <p className="tb-banda" role="note">
      <strong>DATOS SINTÉTICOS DE DEMOSTRACIÓN</strong>
      {children ? <span> · {children}</span> : null}
    </p>
  )
}

export function Procedencia({ valor }: { valor: string | null | undefined }) {
  if (!valor) return null
  return (
    <span className={`tb-etiqueta tb-${valor}`} title={valor === 'derivado' ? 'La fuente lo calcula con un factor o supuesto' : 'Registro directo de la fuente o cálculo sobre valores medidos'}>
      {valor === 'derivado' ? 'Derivado' : 'Medido'}
    </span>
  )
}

export function Kpi({
  etiqueta,
  valor,
  detalle,
  procedencia,
}: {
  etiqueta: string
  valor: string
  detalle?: string
  procedencia?: string | null
}) {
  return (
    <div className="tb-kpi">
      <dt>{etiqueta}</dt>
      <dd>
        <span className="tb-kpi-valor">{valor}</span>
        {procedencia ? <Procedencia valor={procedencia} /> : null}
        {detalle ? <span className="tb-kpi-detalle">{detalle}</span> : null}
      </dd>
    </div>
  )
}

/** Ficha metodológica visible junto a cada gráfico. */
export function FichaMetodologica({
  fichas,
  fuentes,
  n,
}: {
  fichas: Ficha[]
  fuentes: Fuente[]
  n?: string
}) {
  const vista = useVista()
  if (!fichas.length) return null
  return (
    <aside className="tb-ficha" aria-label={`Ficha metodológica: ${fichas.map((f) => f.nombre).join(', ')}`}>
      {fichas.map((f) => (
        <div key={f.metric_id} className="tb-ficha-item">
          <p>
            <strong>{f.nombre}</strong> <Procedencia valor={f.procedencia} />
          </p>
          <p>
            <span className="tb-ficha-campo">Fórmula:</span> {f.formula ?? SIN_DATO}
          </p>
          {vista === 'tecnica' ? (
            <>
              <p>
                <span className="tb-ficha-campo">Pregunta:</span> {f.pregunta}
              </p>
              <p>
                <span className="tb-ficha-campo">Denominador:</span> {f.denominador ?? 'no aplica'}
              </p>
              <p>
                <span className="tb-ficha-campo">Versión:</span> {f.version} ·{' '}
                <span className="tb-ficha-campo">k mínimo:</span>{' '}
                {f.k_minimo ?? 'no aplica (no describe personas)'}
              </p>
              <p>
                <span className="tb-ficha-campo">Decisión potencial:</span> {f.decision_potencial}
              </p>
            </>
          ) : null}
          <p>
            <span className="tb-ficha-campo">Limitación:</span> {f.limitaciones}
          </p>
        </div>
      ))}
      {n ? (
        <p>
          <span className="tb-ficha-campo">n:</span> {n}
        </p>
      ) : null}
      <p>
        <span className="tb-ficha-campo">Fuente:</span>{' '}
        {fuentes.length
          ? fuentes.map((f, i) => (
              <span key={f.fuente_id}>
                {i > 0 ? '; ' : ''}
                {f.url ? (
                  <a href={f.url} target="_blank" rel="noreferrer">
                    {f.nombre}
                  </a>
                ) : (
                  f.nombre
                )}
                {f.institucion ? `, ${f.institucion}` : ''}
                {f.fecha_consulta ? ` (consulta ${f.fecha_consulta})` : ''}
                {vista === 'tecnica' && f.sha256 ? (
                  <code className="tb-sha"> SHA-256 {f.sha256.slice(0, 12)}…</code>
                ) : null}
              </span>
            ))
          : 'registro de primera parte de la app'}
      </p>
    </aside>
  )
}

export type Columna<T> = { titulo: string; valor: (fila: T) => ReactNode; numerica?: boolean }

export function TablaDatos<T>({
  titulo,
  columnas,
  filas,
  clave,
}: {
  titulo: string
  columnas: Columna<T>[]
  filas: T[]
  clave: (fila: T, i: number) => string
}) {
  return (
    <div className="tb-tabla-contenedor" tabIndex={0} role="region" aria-label={`Tabla: ${titulo}`}>
      <table className="tb-tabla">
        <caption>{titulo}</caption>
        <thead>
          <tr>
            {columnas.map((c) => (
              <th key={c.titulo} scope="col" className={c.numerica ? 'tb-num' : undefined}>
                {c.titulo}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((f, i) => (
            <tr key={clave(f, i)}>
              {columnas.map((c, j) =>
                j === 0 ? (
                  <th key={c.titulo} scope="row">
                    {c.valor(f)}
                  </th>
                ) : (
                  <td key={c.titulo} className={c.numerica ? 'tb-num' : undefined}>
                    {c.valor(f)}
                  </td>
                ),
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/** Gráfico con su tabla alternativa: el botón alterna entre ambos. */
export function Grafico({
  titulo,
  resumen,
  grafico,
  tabla,
  ficha,
  acciones,
}: {
  titulo: string
  resumen?: ReactNode
  grafico: ReactNode
  tabla: ReactNode
  ficha?: ReactNode
  acciones?: ReactNode
}) {
  const [verTabla, setVerTabla] = useState(false)
  const id = useId()
  return (
    <section className="tb-tarjeta" aria-labelledby={id}>
      <header className="tb-tarjeta-cabeza">
        <h3 id={id}>{titulo}</h3>
        <div className="tb-acciones">
          {acciones}
          <button type="button" className="tb-boton-sec" aria-pressed={verTabla} onClick={() => setVerTabla(!verTabla)}>
            {verTabla ? 'Ver gráfico' : 'Ver tabla de datos'}
          </button>
        </div>
      </header>
      {resumen ? <div className="tb-resumen">{resumen}</div> : null}
      {verTabla ? tabla : grafico}
      {ficha}
    </section>
  )
}

export type Barra = {
  etiqueta: string
  valor: number | null
  texto?: string
  resaltada?: boolean
  marca?: string
}

/** Barras horizontales en SVG. El valor siempre va escrito; el color no es el único código. */
export function BarrasH({
  titulo,
  descripcion,
  barras,
  maximo,
  referencia,
  formato = uno,
}: {
  titulo: string
  descripcion: string
  barras: Barra[]
  maximo?: number
  referencia?: { valor: number; etiqueta: string }
  formato?: (v: number) => string
}) {
  const id = useId()
  const alto = 26
  const izquierda = 190
  const ancho = 640
  const area = 330
  const tope = maximo ?? Math.max(1, ...barras.map((b) => b.valor ?? 0), referencia?.valor ?? 0)
  const escala = (v: number) => (area * v) / tope
  const altoTotal = barras.length * alto + (referencia ? 28 : 8)
  return (
    <svg
      className="tb-svg"
      viewBox={`0 0 ${ancho} ${altoTotal}`}
      role="img"
      aria-labelledby={`${id}-t ${id}-d`}
      preserveAspectRatio="xMinYMin meet"
    >
      <title id={`${id}-t`}>{titulo}</title>
      <desc id={`${id}-d`}>{descripcion}</desc>
      {barras.map((b, i) => {
        const y = i * alto + 4
        return (
          <g key={`${b.etiqueta}-${i}`}>
            <text x={izquierda - 8} y={y + 15} textAnchor="end" className="tb-svg-etiqueta">
              {b.etiqueta.length > 26 ? `${b.etiqueta.slice(0, 25)}…` : b.etiqueta}
            </text>
            {b.valor != null ? (
              <rect
                x={izquierda}
                y={y + 3}
                width={Math.max(1, escala(b.valor))}
                height={alto - 9}
                rx={3}
                className={b.resaltada ? 'tb-barra tb-barra-resaltada' : 'tb-barra'}
              />
            ) : null}
            <text
              x={izquierda + (b.valor != null ? escala(b.valor) : 0) + 6}
              y={y + 15}
              className="tb-svg-valor"
            >
              {b.texto ?? (b.valor != null ? formato(b.valor) : SIN_DATO)}
              {b.marca ? ` ${b.marca}` : ''}
            </text>
          </g>
        )
      })}
      {referencia ? (
        <g>
          <line
            x1={izquierda + escala(referencia.valor)}
            x2={izquierda + escala(referencia.valor)}
            y1={0}
            y2={barras.length * alto + 6}
            className="tb-referencia"
          />
          <text
            x={izquierda + escala(referencia.valor)}
            y={barras.length * alto + 22}
            textAnchor="middle"
            className="tb-svg-etiqueta"
          >
            {referencia.etiqueta}
          </text>
        </g>
      ) : null}
    </svg>
  )
}

export type Punto = { x: string; y: number | null; hueco?: boolean }

/** Serie en SVG con el valor escrito en cada punto. Un punto «hueco» es parcial. */
export function Linea({
  titulo,
  descripcion,
  puntos,
  formato = entero,
  umbral,
}: {
  titulo: string
  descripcion: string
  puntos: Punto[]
  formato?: (v: number) => string
  umbral?: { valor: number; etiqueta: string }
}) {
  const id = useId()
  const ancho = 640
  const alto = 220
  const m = { izq: 16, der: 16, arr: 28, aba: 30 }
  const valores = puntos.map((p) => p.y).filter((v): v is number => v != null)
  const min = Math.min(...valores, umbral?.valor ?? Infinity) * 0.9
  const max = Math.max(...valores, umbral?.valor ?? -Infinity) * 1.05
  const x = (i: number) => m.izq + ((ancho - m.izq - m.der) * i) / Math.max(1, puntos.length - 1)
  const y = (v: number) => m.arr + ((alto - m.arr - m.aba) * (max - v)) / (max - min || 1)
  const trazo = puntos
    .map((p, i) => (p.y == null ? null : `${x(i)},${y(p.y)}`))
    .filter(Boolean)
    .join(' ')
  return (
    <svg className="tb-svg" viewBox={`0 0 ${ancho} ${alto}`} role="img" aria-labelledby={`${id}-t ${id}-d`}>
      <title id={`${id}-t`}>{titulo}</title>
      <desc id={`${id}-d`}>{descripcion}</desc>
      {umbral ? (
        <g>
          <line x1={m.izq} x2={ancho - m.der} y1={y(umbral.valor)} y2={y(umbral.valor)} className="tb-referencia" />
          <text x={ancho - m.der} y={y(umbral.valor) - 4} textAnchor="end" className="tb-svg-etiqueta">
            {umbral.etiqueta}
          </text>
        </g>
      ) : null}
      <polyline points={trazo} className="tb-linea" />
      {puntos.map((p, i) =>
        p.y == null ? null : (
          <g key={p.x}>
            <circle cx={x(i)} cy={y(p.y)} r={4.5} className={p.hueco ? 'tb-punto tb-punto-hueco' : 'tb-punto'} />
            <text x={x(i)} y={y(p.y) - 9} textAnchor="middle" className="tb-svg-valor">
              {formato(p.y)}
            </text>
            <text x={x(i)} y={alto - 10} textAnchor="middle" className="tb-svg-etiqueta">
              {p.x}
              {p.hueco ? '*' : ''}
            </text>
          </g>
        ),
      )}
    </svg>
  )
}

export function Cargando({ que }: { que: string }) {
  return <p role="status">Cargando {que}…</p>
}

export function ErrorCarga({ mensaje }: { mensaje: string }) {
  return (
    <p role="alert" className="tb-error">
      No se pudo cargar: {mensaje}
    </p>
  )
}
