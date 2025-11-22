<template>
  <div class="landing-page">
    <Navbar @scroll-to="scrollToSection" />
    <HeroSection />
    <SocialProof />
    <VideoSection id="video" />
    <AboutSection id="sobre-mi" />
    <ServicesSection id="servicios" />
    <ResultsSection id="resultados" />
    <GuaranteeSection />
    <TestimonialsSection id="testimonios" />
    <CalendlySection id="calendly" />
    <ContactForm id="contacto" />
    <Footer />
  </div>
</template>

<script>
import Navbar from "./NavBar.vue"
import HeroSection from "./HeroSection.vue"
import SocialProof from "./SocialProof.vue"
import AboutSection from "./AboutSection.vue"
import ServicesSection from "./ServicesSection.vue"
import ResultsSection from "./ResultsSection.vue"
import GuaranteeSection from "./GuaranteeSection.vue"
import TestimonialsSection from "./TestimonialsSection.vue"
import CalendlySection from "./CalendlySection.vue"
import ContactForm from "./ContactForm.vue"
import Footer from "./Footer.vue"
import VideoSection from "./VideoSection.vue";

export default {
  name: 'LandingView',
  components: {
    Navbar,
    HeroSection,
    SocialProof,
    VideoSection,
    AboutSection,
    ServicesSection,
    ResultsSection,
    GuaranteeSection,
    TestimonialsSection,
    CalendlySection,
    ContactForm,
    Footer
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
.landing-page {
  width: 100%;
  min-height: 100vh;
  background: var(--bg-primary);
  overflow-x: hidden;
}
</style>
