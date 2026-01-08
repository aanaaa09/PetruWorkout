<template>
  <div class="info-view">
    <FullNavbar @scroll-to="scrollToSection" />
    <main v-if="!currentLegalPage">
      <AboutSection id="sobre-mi" />
      <ServicesSection id="servicios" />
      <GuaranteeSection />
      <TestimonialsSection id="testimonios" />
      <ContactForm id="contacto" />
      <WhatsAppButton />
    </main>

    <!-- ✅ MODIFICADO: Solo mostrar footer si no hay página legal activa -->
    <FullFooter v-if="!currentLegalPage" @show-legal="showLegalPage" />

    <!-- ✅ Páginas legales como overlay -->
    <component
      v-if="currentLegalPage"
      :is="currentLegalComponent"
      @close="closeLegalPage"
    />
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
import WhatsAppButton from '@/components/shared/WhatsAppButton.vue'

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
    WhatsAppButton,
    PrivacyPolicy,
    TermsConditions,
    LegalNotice
  },
  data() {
    return {
      currentLegalPage: null
    }
  },
  mounted() {
    // Actualizar canonical para /info
    const canonical = document.querySelector('link[rel="canonical"]')
    if (canonical) {
      canonical.href = 'https://petrucalistenia.com/info'
    }

    // Actualizar title
    document.title = 'Servicios y Testimonios - PetruWorkout | Entrenador Personal'

    // ✅ NUEVO: Verificar si viene con parámetro legal en la URL
    this.checkLegalParam()
  },
  watch: {
    // ✅ NUEVO: Observar cambios en la ruta
    '$route.query'() {
      this.checkLegalParam()
    }
  },
  computed: {
    currentLegalComponent() {
      const components = {
        'privacy': PrivacyPolicy,
        'terms': TermsConditions,
        'legal-notice': LegalNotice
      }
      return components[this.currentLegalPage]
    }
  },
  methods: {
    scrollToSection(sectionId) {
      const el = document.getElementById(sectionId)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    },

    showLegalPage(pageType) {
      this.currentLegalPage = pageType
      window.scrollTo(0, 0)
    },

    // ✅ NUEVO: Cerrar página legal
    closeLegalPage() {
      this.currentLegalPage = null
      // Limpiar el parámetro de la URL
      this.$router.replace({ query: {} })
      window.scrollTo(0, 0)
    },

    // ✅ NUEVO: Verificar parámetro legal en la URL
    checkLegalParam() {
      const legalParam = this.$route.query.legal
      if (legalParam && ['privacy', 'terms', 'legal-notice'].includes(legalParam)) {
        this.currentLegalPage = legalParam
        window.scrollTo(0, 0)
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
</style>
