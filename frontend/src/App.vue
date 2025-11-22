<template>
  <div id="app">
    <LandingView />
  </div>
</template>

<script>
import LandingView from "@/components/landing/LandingView.vue"

export default {
  name: 'App',
  components: {
    LandingView
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

#app {
  min-height: 100vh;
  background: var(--bg-primary);
}
</style>
