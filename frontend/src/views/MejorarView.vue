<template>
  <div class="simple-page">
    <SimpleNavbar />
    <div class="content-wrapper">
      <h1>Página de Mejorar</h1>
      <p>Próximamente añadiremos el contenido para menores de 18 años.</p>
    </div>
  </div>
</template>

<script>
import SimpleNavbar from '@/components/navigation/SimpleNavbar.vue'

export default {
  name: 'MejorarView',
  components: {
    SimpleNavbar
  }
}
</script>

<style scoped>
.simple-page {
  min-height: 100vh;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
}
.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  text-align: center;
  padding: 2rem;
}
h1 {
  font-size: 3rem;
  color: var(--color-accent);
  margin-bottom: 1rem;
}
</style>
