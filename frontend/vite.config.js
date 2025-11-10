import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/cancion': 'http://localhost:5000',
      '/verificar': 'http://localhost:5000',
      '/rendirse': 'http://localhost:5000'
    }
  }
})
