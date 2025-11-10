import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // Rutas del juego
      '/cancion': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/verificar': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/rendirse': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/sync': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/sync-all': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/playlists': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      // Rutas de rondas
      '/api/rondas': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      // Rutas de autenticación
      '/api/auth': {
        target: 'http://localhost:5000',  // ⚠️ Cambiar a 5000 si usas un solo servidor
        changeOrigin: true
      }
    }
  }
})
