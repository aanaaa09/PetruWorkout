import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue()
  ],

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },

  ssgOptions: {
    // Rutas que quieres pre-renderizar
    includedRoutes: ['/', '/info'],

    // Formato de salida
    formatting: 'minify',

    // Crítico para SEO
    crittersOptions: {
      reduceInlineStyles: false,
    }
  },

  build: {
    outDir: 'dist',
    assetsDir: 'assets',

    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router']
        }
      }
    }
  }
})
