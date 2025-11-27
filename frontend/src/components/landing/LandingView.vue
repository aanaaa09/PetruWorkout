<template>
  <div class="landing-page">
    <!-- Páginas legales (se muestran en pantalla completa) -->
    <PrivacyPolicy v-if="showPrivacy" @close="closePrivacy" />
    <LegalNotice v-if="showLegal" @close="closeLegal" />
    <TermsConditions v-if="showTerms" @close="closeTerms" />

    <!-- Landing normal (oculto cuando hay página legal abierta) -->
    <div v-show="!showPrivacy && !showLegal && !showTerms">
      <Navbar @scroll-to="scrollToSection" />
      <HeroSection />
      <SocialProof />
      <ResultsSection id="resultados" />
      <VideoSection id="video" />
      <AboutSection id="sobre-mi" />
      <ServicesSection id="servicios" />
      <GuaranteeSection />
      <TestimonialsSection id="testimonios" />
      <CalendlySection id="calendly" />
      <ContactForm id="contacto" />
      <Footer
        @show-privacy="openPrivacy"
        @show-legal="openLegal"
        @show-terms="openTerms"
      />
    </div>
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
import VideoSection from "./VideoSection.vue"
import PrivacyPolicy from "../legal/PrivacyPolicy.vue"
import LegalNotice from "../legal/LegalNotice.vue"
import TermsConditions from "../legal/TermsConditions.vue"

export default {
  name: 'LandingView',
  components: {
    Navbar,
    HeroSection,
    VideoSection,
    AboutSection,
    ServicesSection,
    ResultsSection,
    GuaranteeSection,
    TestimonialsSection,
    CalendlySection,
    ContactForm,
    Footer,
    PrivacyPolicy,
    LegalNotice,
    TermsConditions
  },
  data() {
    return {
      showPrivacy: false,
      showLegal: false,
      showTerms: false
    }
  },
  methods: {
    scrollToSection(sectionId) {
      const el = document.getElementById(sectionId)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    },
    openPrivacy() {
      console.log('Opening Privacy Policy')
      this.showPrivacy = true
      this.showLegal = false
      this.showTerms = false
      window.scrollTo(0, 0)
    },
    openLegal() {
      console.log('Opening Legal Notice')
      this.showPrivacy = false
      this.showLegal = true
      this.showTerms = false
      window.scrollTo(0, 0)
    },
    openTerms() {
      console.log('Opening Terms & Conditions')
      this.showPrivacy = false
      this.showLegal = false
      this.showTerms = true
      window.scrollTo(0, 0)
    },
    closePrivacy() {
      console.log('Closing Privacy Policy')
      this.showPrivacy = false
      window.scrollTo(0, 0)
    },
    closeLegal() {
      console.log('Closing Legal Notice')
      this.showLegal = false
      window.scrollTo(0, 0)
    },
    closeTerms() {
      console.log('Closing Terms & Conditions')
      this.showTerms = false
      window.scrollTo(0, 0)
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
