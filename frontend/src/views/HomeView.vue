<template>
  <div class="home-view">
    <SimpleNavbar />
    <HeroSection />
    <VideoSection />
    <ResultsSection />
    <SimpleFooter @show-legal="showLegalPage" />
    <component
      v-if="currentLegalPage"
      :is="currentLegalComponent"
      @close="currentLegalPage = null"
    />
  </div>
</template>

<script>
import SimpleNavbar from '@/components/navigation/SimpleNavbar.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import VideoSection from '@/components/landing/VideoSection.vue'
import ResultsSection from '@/components/landing/ResultsSection.vue'
import SimpleFooter from '@/components/navigation/SimpleFooter.vue'
import PrivacyPolicy from '@/components/legal/PrivacyPolicy.vue'
import TermsConditions from '@/components/legal/TermsConditions.vue'
import LegalNotice from '@/components/legal/LegalNotice.vue'
import { useHead } from '@unhead/vue'

export default {
   name: 'HomeView',
  setup() {
    useHead({
      title: 'PetruWorkout - Entrenador Personal de Calistenia',
      meta: [
        { name: 'description', content: 'Entrenador personal de calistenia en Toledo, Madrid y online. Transforma tu cuerpo con el método PetruWorkout. Garantía de devolución del 100%.' },
        { property: 'og:title', content: 'PetruWorkout - Entrenador Personal de Calistenia' },
        { property: 'og:description', content: 'Entrenador personal de calistenia en Toledo, Madrid y online. Garantía de devolución del 100%.' },
        { property: 'og:url', content: 'https://petrucalistenia.com/' },
        { name: 'robots', content: 'index, follow' },
      ]
    })
  },
  components: {
    SimpleNavbar,
    HeroSection,
    VideoSection,
    ResultsSection,
    SimpleFooter,
    PrivacyPolicy,
    TermsConditions,
    LegalNotice
  },
  data() {
    return {
      currentLegalPage: null
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
    showLegalPage(pageType) {
      this.currentLegalPage = pageType
      window.scrollTo(0, 0)
    }
  }
}
</script>

<style scoped>
.home-view {
  width: 100%;
  min-height: 100vh;
  background: var(--bg-primary);
}
</style>
