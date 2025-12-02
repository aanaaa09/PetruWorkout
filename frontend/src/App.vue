<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import { initTracking } from './utils/tracking'

export default {
  name: 'App',
  mounted() {
    // Inicializar tracking cuando la app se carga
    initTracking()

    // Añadir preconnect para Google Fonts si no existe
    if (!document.querySelector('link[href="https://fonts.googleapis.com"]')) {
      const preconnect1 = document.createElement('link');
      preconnect1.rel = 'preconnect';
      preconnect1.href = 'https://fonts.googleapis.com';
      document.head.appendChild(preconnect1);

      const preconnect2 = document.createElement('link');
      preconnect2.rel = 'preconnect';
      preconnect2.href = 'https://fonts.gstatic.com';
      preconnect2.crossOrigin = 'anonymous';
      document.head.appendChild(preconnect2);
    }
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
