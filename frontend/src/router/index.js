import HomeView from '@/views/HomeView.vue'
import InfoView from '@/views/InfoView.vue'
import TeamView from '@/views/TeamView.vue'


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
  },
  {
    path: '/team',
    name: 'team',
    component: TeamView,
    meta: {
      title: 'Únete al Equipo - PetruWorkout | Grupo Exclusivo',
      description: 'Accede a contenido exclusivo, rutinas premium y únete a nuestra comunidad de WhatsApp. Recibe tu regalo de bienvenida.',
      keywords: 'grupo whatsapp fitness, comunidad calistenia, contenido exclusivo entrenamiento',
      ogImage: 'https://petrucalistenia.com/logo.png',
      canonical: 'https://petrucalistenia.com/team'
    }
  }
]

export default routes
