<template>
  <div class="info-view">
    <FullNavbar @scroll-to="scrollToSection" />
    <main>
      <AboutSection id="sobre-mi" />
      <ServicesSection id="servicios" />
      <GuaranteeSection />
      <TestimonialsSection id="testimonios" />
      <CalendlySection id="calendly" />
      <ContactForm id="contacto" />
    </main>
    <FullFooter @show-legal="showLegalPage" />

    <component
      v-if="currentLegalPage"
      :is="currentLegalComponent"
      @close="currentLegalPage = null"
    />
  </div>
</template>

<script>
import FullNavbar from '@/components/navigation/FullNavbar.vue'
import AboutSection from '@/components/landing/AboutSection.vue'
import ServicesSection from '@/components/landing/ServicesSection.vue'
import GuaranteeSection from '@/components/landing/GuaranteeSection.vue'
import TestimonialsSection from '@/components/landing/TestimonialsSection.vue'
import CalendlySection from '@/components/landing/CalendlySection.vue'
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
    CalendlySection,
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
  // ✅ AÑADIR ESTO:
  mounted() {
    // Actualizar canonical para /info
    const canonical = document.querySelector('link[rel="canonical"]')
    if (canonical) {
      canonical.href = 'https://petrucalistenia.com/info'
    }

    // Actualizar title
    document.title = 'Servicios y Testimonios - PetruWorkout | Entrenador Personal'
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
