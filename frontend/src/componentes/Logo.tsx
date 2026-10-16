/** Flor de talavera de Puebla Viva 360. Decorativa: el nombre va siempre en texto al lado. */
export function Logo({ className }: { className?: string }) {
  const petalos = [0, 45, 90, 135, 180, 225, 270, 315]
  return (
    <svg className={className} viewBox="0 0 64 64" aria-hidden="true" focusable="false">
      <rect width="64" height="64" rx="16" fill="#1f4e8c" />
      <circle cx="32" cy="32" r="24" fill="none" stroke="#faf6ef" strokeWidth="1.5" strokeDasharray="2 3" opacity="0.7" />
      {petalos.map((angulo) => (
        <ellipse
          key={angulo}
          cx="32"
          cy="17.5"
          rx="5.2"
          ry="10"
          fill={angulo % 90 === 0 ? '#faf6ef' : '#9fc0e8'}
          transform={`rotate(${angulo} 32 32)`}
        />
      ))}
      <circle cx="32" cy="32" r="8.5" fill="#d9663a" stroke="#faf6ef" strokeWidth="2.5" />
      <circle cx="32" cy="32" r="3" fill="#faf6ef" />
    </svg>
  )
}
