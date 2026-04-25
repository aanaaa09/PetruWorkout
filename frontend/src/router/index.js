import HomeView from '@/views/HomeView.vue'
import InfoView from '@/views/InfoView.vue'
import TeamView from '@/views/TeamView.vue'
import CalculatorView from '@/views/CalculatorView.vue'


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
  },
  {
    path: '/calculator',
    name: 'calculator',
    component: CalculatorView,
    meta: {
      title: 'Calculadora de Calorías - PetruWorkout | Calcula tus Macros',
      description: 'Calculadora gratuita de calorías y macronutrientes. Descubre cuántas calorías necesitas según tu objetivo: perder grasa, mantener peso o ganar músculo.',
      keywords: 'calculadora calorías, calcular macros, IMC, déficit calórico, superávit calórico, nutrición deportiva',
      ogImage: 'https://petrucalistenia.com/logo.png',
      canonical: 'https://petrucalistenia.com/calculator'
    }
  },
  {
    path: '/testfuerza',
    name: 'test fuerza',
    component: () => import('@/views/TestFuerza.vue'),
    meta: {
      title: 'Test de fuerza | Calcula Fuerza Real',
      description: 'Calculadora gratuita de fuerza. Descubre cómo progresar adecuadamente.',
      keywords: 'calculadora fuerza, sentadillas, fondos, dominadas, flexiones',
      ogImage: 'https://petrucalistenia.com/logo.png',
      canonical: 'https://petrucalistenia.com/testffuerza'
    }
  },
  {
  path: '/admin',
  name: 'admin',
  component: () => import('@/components/admin/AdminView.vue'),
  meta: {
    title: 'Panel de Administración - PetruWorkout',
    description: 'Panel de control administrativo',
    robots: 'noindex, nofollow'  //Evita que Google indexe esto
  }
}
]

export default routes
