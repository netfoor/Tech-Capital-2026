import { forwardRef, useId } from 'react'
import { useTextos } from '../i18n/textos'
import { Icono } from './Icono'

interface Props {
  nombre: string
  leyenda: string
  valor: number | null
  error?: string
  alCambiar: (valor: number) => void
}

/** Calificación de 1 a 5 con radios nativos: funciona con teclado y lector de pantalla. */
export const Calificacion = forwardRef<HTMLInputElement, Props>(function Calificacion(
  { nombre, leyenda, valor, error, alCambiar },
  ref,
) {
  const t = useTextos()
  const base = useId()
  const idError = `${base}-error`
  return (
    <fieldset className="calificacion" aria-describedby={error ? idError : undefined} aria-invalid={error ? true : undefined}>
      <legend>{leyenda}</legend>
      {error && (
        <p className="campo__error" id={idError}>
          <Icono nombre="reportado" className="pastilla__icono" />
          {error}
        </p>
      )}
      <div className="calificacion__opciones">
        {t.resena.escala.map((texto, indice) => {
          const numero = indice + 1
          const id = `${base}-${numero}`
          return (
            <div key={numero} className="calificacion__opcion">
              <input
                ref={numero === 1 ? ref : undefined}
                id={id}
                type="radio"
                name={nombre}
                value={numero}
                checked={valor === numero}
                onChange={() => alCambiar(numero)}
              />
              <label htmlFor={id}>
                <span className="calificacion__numero">{numero}</span>
                <span className="visualmente-oculto">, </span>
                <span>{texto}</span>
              </label>
            </div>
          )
        })}
      </div>
    </fieldset>
  )
})
