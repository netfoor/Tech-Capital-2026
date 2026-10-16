/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: false,
      includeAssets: ['iconos/icono.svg', 'iconos/apple-touch-icon.png'],
      manifest: {
        id: '/',
        name: 'Puebla Viva 360',
        short_name: 'Puebla Viva',
        description: 'Descubre, planea y vive recorridos por Puebla con información de accesibilidad honesta.',
        lang: 'es-MX',
        dir: 'ltr',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        orientation: 'any',
        background_color: '#faf6ef',
        theme_color: '#1f4e8c',
        categories: ['travel', 'navigation'],
        icons: [
          { src: '/iconos/icono-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: '/iconos/icono-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
          { src: '/iconos/icono-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
          { src: '/iconos/icono.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
        ],
      },
      workbox: {
        // Shell de la app precargado; la navegación sin red cae en index.html.
        globPatterns: ['**/*.{js,css,html,svg,png,webmanifest}'],
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api\//],
        cleanupOutdatedCaches: true,
        runtimeCaching: [
          {
            // Última respuesta de lugares y destinos: sirve sin conexión (offline parcial).
            urlPattern: ({ url, request }) =>
              request.method === 'GET' && /^\/api\/(pois|destinos)(\/|\?|$)/.test(url.pathname + url.search),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'poi-ultima',
              networkTimeoutSeconds: 5,
              expiration: { maxEntries: 30, maxAgeSeconds: 7 * 24 * 60 * 60 },
              cacheableResponse: { statuses: [200] },
            },
          },
        ],
      },
    }),
  ],
  server: {
    proxy: {
      '/api': {
        target: process.env.API_URL ?? 'http://localhost:8000',
        rewrite: (ruta) => ruta.replace(/^\/api/, ''),
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/pruebas/setup.ts'],
    testTimeout: 30000,
  },
})
