import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { toHaveNoViolations } from 'jest-axe'
import { afterEach, beforeEach, expect, vi } from 'vitest'
import { reiniciarModo } from '../api/modo'
import { recargarAlmacen } from '../almacen/almacen'
import { reiniciarDestinos } from '../hooks/datos'

expect.extend(toHaveNoViolations)

if (!window.matchMedia) {
  Object.defineProperty(window, 'matchMedia', {
    value: (consulta: string) => ({
      matches: consulta.includes('min-width'),
      media: consulta,
      addEventListener: () => {},
      removeEventListener: () => {},
      addListener: () => {},
      removeListener: () => {},
      onchange: null,
      dispatchEvent: () => false,
    }),
  })
}

window.scrollTo = () => {}

beforeEach(() => {
  window.localStorage.clear()
  recargarAlmacen()
  reiniciarModo()
  reiniciarDestinos()
  // Por omisión no hay API: la app entra en modo de demostración.
  vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new TypeError('sin red'))))
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
  document.documentElement.removeAttribute('data-lenguaje')
})
