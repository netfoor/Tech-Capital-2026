import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// Sitio estático (ADR-0002). Sin recursos externos: todo se sirve desde el propio dominio.
export default defineConfig({
  site: 'https://techcapital.foor.dev',
  output: 'static',
  build: {
    inlineStylesheets: 'never',
  },
  devToolbar: { enabled: false },
  vite: {
    plugins: [tailwindcss()],
    // Sin scripts ni estilos en línea, para que la política de contenido pueda ser solo 'self'.
    build: { assetsInlineLimit: 0 },
  },
});
