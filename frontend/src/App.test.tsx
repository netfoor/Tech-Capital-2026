import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import App from './App'

describe('App', () => {
  it('muestra la vista del visitante en la raíz', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Puebla Viva 360')
  })
})
