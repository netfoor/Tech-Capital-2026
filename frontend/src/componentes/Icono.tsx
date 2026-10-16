// Íconos propios en SVG (trazo de 2 px, caja de 24 px). Decorativos por defecto.

const TRAZOS = {
  descubrir: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="m15.5 8.5-2 5-5 2 2-5z" />
    </>
  ),
  miMapa: (
    <>
      <path d="M9 4 3 6.5v13.5L9 17.5l6 2.5 6-2.5V4l-6 2.5z" />
      <path d="M9 4v13.5M15 6.5V20" />
    </>
  ),
  planear: (
    <>
      <rect x="3.5" y="5" width="17" height="15" rx="2" />
      <path d="M3.5 10h17M8 3v4M16 3v4M8 14h3M8 17h6" />
    </>
  ),
  recorrido: (
    <>
      <circle cx="6" cy="18" r="2.5" />
      <circle cx="18" cy="6" r="2.5" />
      <path d="M8.5 18H15a3 3 0 0 0 0-6H9a3 3 0 0 1 0-6h6.5" />
    </>
  ),
  verificado: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="m8 12.5 2.8 2.8L16.5 9.5" />
    </>
  ),
  sinVerificar: (
    <>
      <circle cx="12" cy="12" r="9" strokeDasharray="3 2.4" />
      <path d="M9.6 9.4a2.5 2.5 0 1 1 3.4 2.3c-.7.3-1 .8-1 1.5v.6" />
      <path d="M12 17h.01" strokeWidth="2.6" />
    </>
  ),
  reportado: (
    <>
      <path d="M10.3 4.2 2.6 17.5A2 2 0 0 0 4.3 20.5h15.4a2 2 0 0 0 1.7-3L13.7 4.2a2 2 0 0 0-3.4 0z" />
      <path d="M12 9.5v4.5M12 17h.01" />
    </>
  ),
  moderacion: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3.5 2" />
    </>
  ),
  guardar: <path d="M6.5 3.5h11a1 1 0 0 1 1 1V21L12 16.8 5.5 21V4.5a1 1 0 0 1 1-1z" />,
  guardado: <path d="M6.5 3.5h11a1 1 0 0 1 1 1V21L12 16.8 5.5 21V4.5a1 1 0 0 1 1-1z" fill="currentColor" />,
  bandera: (
    <>
      <path d="M5 21V4" />
      <path d="M5 4.5c4-2.5 7 2.5 14 0v9c-7 2.5-10-2.5-14 0" />
    </>
  ),
  estrella: <path d="m12 3.5 2.6 5.4 5.9.8-4.3 4.1 1 5.8L12 16.8l-5.2 2.8 1-5.8-4.3-4.1 5.9-.8z" />,
  arriba: <path d="m6 15 6-6 6 6" />,
  abajo: <path d="m6 9 6 6 6-6" />,
  atras: <path d="M15 6 9 12l6 6" />,
  cerrar: <path d="M6 6l12 12M18 6 6 18" />,
  mas: <path d="M12 5v14M5 12h14" />,
  info: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5.5M12 7.5h.01" />
    </>
  ),
  lista: <path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01" />,
  pin: (
    <>
      <path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z" />
      <circle cx="12" cy="9.5" r="2.5" />
    </>
  ),
  caminar: (
    <>
      <circle cx="13" cy="4.5" r="1.8" />
      <path d="m9 21 2.5-6.5L14 17v4M8.5 12l2-4.5 3.5 1.5 2 3.5M10.5 7.5 13 14" />
    </>
  ),
  candado: (
    <>
      <rect x="5" y="10.5" width="14" height="10" rx="2" />
      <path d="M8 10.5V8a4 4 0 0 1 8 0v2.5" />
    </>
  ),
  museo: (
    <>
      <path d="M3 9.5 12 4l9 5.5M4 20.5h16M6 10v8M10 10v8M14 10v8M18 10v8" />
    </>
  ),
  templo: (
    <>
      <path d="M12 2.5v4M10 4.5h4M6 21v-8l6-5 6 5v8M4 21h16" />
      <path d="M10 21v-4a2 2 0 0 1 4 0v4" />
    </>
  ),
  zona_arqueologica: (
    <>
      <path d="M2.5 20.5h19L17 15.5H7zM7 15.5l1.8-3.5h6.4l1.8 3.5M8.8 12l1.6-3.5h3.2l1.6 3.5M10.4 8.5 11 6h2l.6 2.5" />
    </>
  ),
  mirador: (
    <>
      <path d="m2.5 20 6.5-10 4 6 2.5-3.5 6 7.5z" />
      <circle cx="17" cy="6" r="2" />
    </>
  ),
  mercado: (
    <>
      <path d="M4 9h16l-1.6 10a1.5 1.5 0 0 1-1.5 1.3H7.1a1.5 1.5 0 0 1-1.5-1.3z" />
      <path d="m8.5 9 3.5-5.5L15.5 9M9.5 13v4M14.5 13v4" />
    </>
  ),
  plaza: (
    <>
      <path d="M12 21v-6M7 15h10a4 4 0 0 0-1-7.9A4 4 0 0 0 8 7.1 4 4 0 0 0 7 15zM5 21h14" />
    </>
  ),
  artesanias: (
    <>
      <path d="M9 3.5h6M10 3.5v3c-2.5 1-4.5 3.4-4.5 6.5a6.5 6.5 0 0 0 13 0c0-3.1-2-5.5-4.5-6.5v-3" />
      <path d="M6 13h12M7.5 17h9" />
    </>
  ),
  biblioteca: (
    <>
      <path d="M4 19.5V5a1.5 1.5 0 0 1 1.5-1.5H11v16H5.5A1.5 1.5 0 0 0 4 21M20 19.5V5a1.5 1.5 0 0 0-1.5-1.5H13v16h5.5A1.5 1.5 0 0 1 20 21" />
    </>
  ),
  gastronomia: (
    <>
      <path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10M17 21V3c-2.2 1.5-3 4-3 7v3h3" />
    </>
  ),
} as const

export type NombreIcono = keyof typeof TRAZOS

function iconoDeCategoria(categoria: string): NombreIcono {
  return categoria in TRAZOS ? (categoria as NombreIcono) : 'pin'
}

interface Props {
  nombre: NombreIcono
  className?: string
  /** Si se da, el ícono deja de ser decorativo y se anuncia con este texto. */
  etiqueta?: string
}

export function Icono({ nombre, className, etiqueta }: Props) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      width="24"
      height="24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden={etiqueta ? undefined : true}
      role={etiqueta ? 'img' : undefined}
      aria-label={etiqueta}
      focusable="false"
    >
      {TRAZOS[nombre]}
    </svg>
  )
}

/** Ícono de la categoría de un lugar (o un marcador genérico si no la conocemos). */
export function IconoCategoria({ categoria }: { categoria: string }) {
  return <Icono nombre={iconoDeCategoria(categoria)} />
}
