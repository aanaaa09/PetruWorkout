<template>
  <div class="landing-view">
    <HeroSection />
    <AboutSection />
    <ServicesSection />
    <TestimonialsSection />
    <CalendlySection />
    <ContactForm />
    <Footer />
  </div>
</template>

<script>
import HeroSection from '../components/landing/HeroSection.vue'
import AboutSection from '../components/landing/AboutSection.vue'
import ServicesSection from '../components/landing/ServicesSection.vue'
import TestimonialsSection from '../components/landing/TestimonialsSection.vue'
import CalendlySection from '../components/landing/CalendlySection.vue'
import ContactForm from '../components/landing/ContactForm.vue'
import Footer from '../components/landing/Footer.vue'

export default {
  name: 'LandingView',
  components: {
    HeroSection,
    AboutSection,
    ServicesSection,
    TestimonialsSection,
    CalendlySection,
    ContactForm,
    Footer
  }
}
</script>

<style scoped>
.landing-view {
  width: 100%;
  min-height: 100vh;
}
</style>
