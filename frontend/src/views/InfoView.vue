<template>
  <div class="info-view">

    <!-- Navbar solo si NO hay página legal -->
    <FullNavbar v-if="!currentLegalPage" @scroll-to="scrollToSection" />

    <!-- Contenido principal - SOLO si NO hay página legal -->
    <main v-if="!currentLegalPage">
      <AboutSection id="sobre-mi" />
      <ServicesSection id="servicios" />
      <GuaranteeSection />
      <TestimonialsSection id="testimonios" />
      <ContactForm id="contacto" />
    </main>

    <!-- Footer solo si NO hay página legal -->
    <FullFooter v-if="!currentLegalPage" />

    <!-- Páginas legales - Se muestran SOLO cuando están activas -->
    <div v-if="currentLegalPage" class="legal-page-container">
      <PrivacyPolicy v-if="currentLegalPage === 'privacy'" />
      <TermsConditions v-if="currentLegalPage === 'terms'" />
      <LegalNotice v-if="currentLegalPage === 'legal-notice'" />
    </div>
  </div>
</template>

<script>
import FullNavbar from '@/components/navigation/FullNavbar.vue'
import AboutSection from '@/components/landing/AboutSection.vue'
import ServicesSection from '@/components/landing/ServicesSection.vue'
import GuaranteeSection from '@/components/landing/GuaranteeSection.vue'
import TestimonialsSection from '@/components/landing/TestimonialsSection.vue'
import ContactForm from '@/components/landing/ContactForm.vue'
import FullFooter from '@/components/navigation/FullFooter.vue'
import PrivacyPolicy from '@/components/legal/PrivacyPolicy.vue'
import TermsConditions from '@/components/legal/TermsConditions.vue'
import LegalNotice from '@/components/legal/LegalNotice.vue'

export default {
  name: 'InfoView',
  components: {
    FullNavbar,
    AboutSection,
    ServicesSection,
    GuaranteeSection,
    TestimonialsSection,
    ContactForm,
    FullFooter,
    PrivacyPolicy,
    TermsConditions,
    LegalNotice
  },
  data() {
    return {
      currentLegalPage: null
    }
  },

  beforeMount() {
    this.checkLegalParam()
  },
  mounted() {
    const canonical = document.querySelector('link[rel="canonical"]')
    if (canonical) canonical.href = 'https://petrucalistenia.com/info'

    // Volver a revisar por si acaso
    this.checkLegalParam()

    if (!this.currentLegalPage) {
      document.title = 'Servicios - PetruWorkout | Entrenador Personal'
    }

    console.log('📍 InfoView mounted - Legal page:', this.currentLegalPage)
  },
  watch: {
    '$route': {
      handler(to, from) {
        console.log('Route changed:', to.query.legal)
        this.checkLegalParam()
      },
      immediate: true
    }
  },
  methods: {
    scrollToSection(sectionId) {
      // Primero cerrar cualquier página legal
      if (this.currentLegalPage) {
        this.closeLegalPage()
      }

      // Esperar a que se cierre la página legal
      this.$nextTick(() => {
        setTimeout(() => {
          const el = document.getElementById(sectionId)
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }
        }, 100)
      })
    },
    closeLegalPage() {
      console.log('Closing legal page')
      this.currentLegalPage = null

      // Limpiar el query param sin recargar
      if (this.$route.query.legal) {
        this.$router.replace({ path: '/info', query: {} })
      }

      // Scroll al inicio
      this.$nextTick(() => {
        window.scrollTo({ top: 0, behavior: 'auto' })
        document.title = 'Servicios - PetruWorkout | Entrenador Personal'
      })
    },
    checkLegalParam() {
      const legalParam = this.$route.query.legal

      console.log('Checking legal param:', legalParam)
      console.log('Full route query:', this.$route.query)

      // Lista válida de páginas legales
      const validPages = ['privacy', 'terms', 'legal-notice']

      if (legalParam && validPages.includes(legalParam)) {
        console.log('Valid legal page detected:', legalParam)
        this.currentLegalPage = legalParam

        // Scroll al inicio inmediatamente
        this.$nextTick(() => {
          window.scrollTo({ top: 0, behavior: 'auto' })

          // Actualizar título según la página
          const titles = {
            'privacy': 'Política de Privacidad - PetruWorkout',
            'terms': 'Términos y Condiciones - PetruWorkout',
            'legal-notice': 'Aviso Legal - PetruWorkout'
          }
          document.title = titles[legalParam] || document.title
        })
      } else {
        console.log('No valid legal param, showing normal content')
        if (this.currentLegalPage !== null) {
          this.currentLegalPage = null
        }
      }
    }
  }
}
</script>

<style scoped>
.info-view {
  width: 100%;
  min-height: 100vh;
  background: var(--bg-primary);
}

.legal-page-container {
  width: 100%;
  min-height: 100vh;
}
</style>
