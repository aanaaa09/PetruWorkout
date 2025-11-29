// frontend/src/main.js
import { ViteSSG } from 'vite-ssg'
import App from './App.vue'
import routes from './router'

// Importar estilos globales
import './styles/variables.css'
import './styles/animations.css'

// https://github.com/antfu/vite-ssg
export const createApp = ViteSSG(
  App,
  { routes },
  ({ app, router, routes, isClient, initialState }) => {
    // Configuración adicional si es necesario

    // Este código se ejecuta tanto en servidor como en cliente
    if (isClient) {
      // Código que solo se ejecuta en el navegador
      console.log('App corriendo en el cliente')
    }
  }
)
