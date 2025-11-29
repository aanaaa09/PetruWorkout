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

export default {
  name: 'HomeView',
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
