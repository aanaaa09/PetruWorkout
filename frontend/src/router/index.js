import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import InfoView from '@/views/InfoView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: 'PetruWorkout - Entrenador Personal de Calistenia',
        description: 'Consigue menos de 20% de grasa y +3kg de músculo en 90 días. Entrenador personal online especializado en calistenia.'
      }
    },
    {
      path: '/info',
      name: 'info',
      component: InfoView,
      meta: {
        title: 'Más Información - PetruWorkout',
        description: 'Conoce más sobre mi método de entrenamiento, servicios y testimonios de clientes.'
      }
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      }
    }
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0, behavior: 'smooth' }
  }
})

// Actualizar meta tags en cada cambio de ruta
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'PetruWorkout'

  const metaDescription = document.querySelector('meta[name="description"]')
  if (metaDescription) {
    metaDescription.setAttribute('content', to.meta.description || '')
  }

  next()
})

export default router
