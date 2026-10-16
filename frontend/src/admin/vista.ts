import { createContext, useContext } from 'react'

export type Vista = 'ejecutiva' | 'tecnica'

export const ContextoVista = createContext<Vista>('ejecutiva')

export const useVista = () => useContext(ContextoVista)
