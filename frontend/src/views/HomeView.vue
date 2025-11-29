<template>
  <div class="home-view">
    <SimpleNavbar />
    <HeroSection />
    <VideoSection />
    <ResultsSection />
    <SimpleFooter />
  </div>
</template>

<script>
import SimpleNavbar from '@/components/navigation/SimpleNavbar.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import VideoSection from '@/components/landing/VideoSection.vue'
import ResultsSection from '@/components/landing/ResultsSection.vue'
import SimpleFooter from '@/components/navigation/SimpleFooter.vue'

export default {
  name: 'HomeView',
  components: {
    SimpleNavbar,
    HeroSection,
    VideoSection,
    ResultsSection,
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
