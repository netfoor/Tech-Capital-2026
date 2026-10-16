import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router'
import { useTextos } from '../i18n/textos'
import type { PropsMapa } from './Mapa'

const ESTILO = 'https://tiles.openfreemap.org/styles/liberty'
const CENTRO_PUEBLA: [number, number] = [-98.2, 19.04]

function movimientoReducido(): boolean {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}

export default function MapaMapLibre({ puntos, trazo }: PropsMapa) {
  const t = useTextos()
  const contenedor = useRef<HTMLDivElement>(null)
  const mapa = useRef<maplibregl.Map | null>(null)
  const marcadores = useRef<maplibregl.Marker[]>([])
  const navegar = useNavigate()

  useEffect(() => {
    if (!contenedor.current) return
    const instancia = new maplibregl.Map({
      container: contenedor.current,
      style: ESTILO,
      center: CENTRO_PUEBLA,
      zoom: 9,
      attributionControl: { compact: false },
      cooperativeGestures: true,
    })
    instancia.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
    instancia.getCanvas().setAttribute('aria-hidden', 'true')
    instancia.getCanvas().tabIndex = -1
    mapa.current = instancia
    return () => {
      instancia.remove()
      mapa.current = null
    }
  }, [])

  useEffect(() => {
    const instancia = mapa.current
    if (!instancia) return
    marcadores.current.forEach((marcador) => marcador.remove())
    marcadores.current = []

    for (const punto of puntos) {
      const boton = document.createElement('button')
      boton.type = 'button'
      boton.className = `marcador ${punto.resaltado ? 'marcador--guardado' : ''}`
      boton.setAttribute('aria-label', t.mapa.marcador(punto.nombre))
      const numero = document.createElement('span')
      numero.textContent = punto.numero ? String(punto.numero) : ''
      numero.setAttribute('aria-hidden', 'true')
      boton.appendChild(numero)

      const contenido = document.createElement('div')
      const titulo = document.createElement('a')
      titulo.href = punto.ruta
      titulo.textContent = punto.nombre
      titulo.addEventListener('click', (evento) => {
        evento.preventDefault()
        navegar(punto.ruta)
      })
      const detalle = document.createElement('p')
      detalle.textContent = punto.detalle
      detalle.style.margin = '0.25rem 0 0'
      contenido.append(titulo, detalle)

      const marcador = new maplibregl.Marker({ element: boton, anchor: 'bottom' })
        .setLngLat([punto.lon, punto.lat])
        .setPopup(new maplibregl.Popup({ offset: 28, closeButton: true }).setDOMContent(contenido))
        .addTo(instancia)
      marcadores.current.push(marcador)
    }

    const dibujarTrazo = () => {
      const fuente = instancia.getSource('trazo') as maplibregl.GeoJSONSource | undefined
      const datos: GeoJSON.Feature = {
        type: 'Feature',
        properties: {},
        geometry: { type: 'LineString', coordinates: trazo ? puntos.map((punto) => [punto.lon, punto.lat]) : [] },
      }
      if (fuente) {
        fuente.setData(datos)
        return
      }
      instancia.addSource('trazo', { type: 'geojson', data: datos })
      instancia.addLayer({
        id: 'trazo',
        type: 'line',
        source: 'trazo',
        paint: { 'line-color': '#1f4e8c', 'line-width': 3, 'line-dasharray': [2, 1.5] },
      })
    }
    if (instancia.isStyleLoaded()) dibujarTrazo()
    else instancia.once('load', dibujarTrazo)

    if (puntos.length > 0) {
      const limites = new maplibregl.LngLatBounds()
      puntos.forEach((punto) => limites.extend([punto.lon, punto.lat]))
      instancia.fitBounds(limites, { padding: 56, maxZoom: 15.5, animate: !movimientoReducido() })
    }
  }, [puntos, trazo, t, navegar])

  return <div ref={contenedor} className="mapa__lienzo" role="region" aria-label={t.mapa.etiqueta(puntos.length)} />
}
