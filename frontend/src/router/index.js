import HomeView from '@/views/HomeView.vue'
import InfoView from '@/views/InfoView.vue'

// Exportar solo las rutas (sin crear el router aquí)
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: 'PetruWorkout - Entrenador Personal de Calistenia | Toledo y Madrid',
      description: 'Consigue menos de 20% de grasa y +3kg de músculo en 90 días. Entrenador personal online especializado en calistenia. Garantía de devolución.',
      keywords: 'calistenia toledo, calistenia madrid, entrenador personal calistenia, transformación física',
      ogImage: 'https://petrucalistenia.com/logo.png',
      canonical: 'https://petrucalistenia.com/'
    }
  },
  {
    path: '/info',
    name: 'info',
    component: InfoView,
    meta: {
      title: 'Servicios y Testimonios - PetruWorkout | Entrenador Personal',
      description: 'Conoce mi método de entrenamiento, servicios de calistenia online y presencial en Toledo y Madrid. Ver testimonios reales de transformaciones exitosas.',
      keywords: 'servicios calistenia, testimonios entrenamiento, clases online calistenia',
      ogImage: 'https://petrucalistenia.com/logo.png',
      canonical: 'https://petrucalistenia.com/info'
    }
  }
]

export default routes
