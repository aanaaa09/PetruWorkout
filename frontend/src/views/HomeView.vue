<template>
  <div class="home-view">
    <SimpleNavbar />
    <HeroSection />
    <SocialProof />
    <ResultsSection />
    <VideoSection />
    <SimpleFooter />
  </div>
</template>

<script>
import SimpleNavbar from '@/components/navigation/SimpleNavbar.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import ResultsSection from '@/components/landing/ResultsSection.vue'
import VideoSection from '@/components/landing/VideoSection.vue'
import SimpleFooter from '@/components/navigation/SimpleFooter.vue'

export default {
  name: 'HomeView',
  components: {
    SimpleNavbar,
    HeroSection,
    SocialProof,
    ResultsSection,
    VideoSection,
    SimpleFooter
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
