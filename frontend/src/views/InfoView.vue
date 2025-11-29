<template>
  <div class="info-view">
    <FullNavbar @scroll-to="scrollToSection" />
    <HeroSection id="inicio" />
    <SocialProof />
    <ResultsSection id="resultados" />
    <VideoSection id="video" />
    <AboutSection id="sobre-mi" />
    <ServicesSection id="servicios" />
    <GuaranteeSection />
    <TestimonialsSection id="testimonios" />
    <CalendlySection id="calendly" />
    <ContactForm id="contacto" />
    <FullFooter />
  </div>
</template>

<script>
import FullNavbar from '@/components/navigation/FullNavbar.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import SocialProof from '@/components/landing/SocialProof.vue'
import ResultsSection from '@/components/landing/ResultsSection.vue'
import VideoSection from '@/components/landing/VideoSection.vue'
import AboutSection from '@/components/landing/AboutSection.vue'
import ServicesSection from '@/components/landing/ServicesSection.vue'
import GuaranteeSection from '@/components/landing/GuaranteeSection.vue'
import TestimonialsSection from '@/components/landing/TestimonialsSection.vue'
import CalendlySection from '@/components/landing/CalendlySection.vue'
import ContactForm from '@/components/landing/ContactForm.vue'
import FullFooter from '@/components/navigation/FullFooter.vue'

export default {
  name: 'InfoView',
  components: {
    FullNavbar: FullNavbar,
    HeroSection,
    SocialProof,
    ResultsSection,
    VideoSection,
    AboutSection,
    ServicesSection,
    GuaranteeSection,
    TestimonialsSection,
    CalendlySection,
    ContactForm,
    FullFooter
  },
  methods: {
    scrollToSection(sectionId) {
      const el = document.getElementById(sectionId)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' })
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
