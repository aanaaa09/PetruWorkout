<template>
  <div v-if="!disabled" class="sticky-cta">
    <CtaButton calm @click="$emit('open-form')">Descubre qué te frena</CtaButton>
  </div>
</template>

<script>
import CtaButton from '@/components/landing/CtaButton.vue'

// Botón siempre fijo abajo (móvil y escritorio), sin animación
export default {
  name: 'StickyCta',
  components: { CtaButton },
  props: {
    // true mientras el formulario está abierto
    disabled: { type: Boolean, default: false }
  },
}
</script>

<style scoped>
.sticky-cta {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 800;
  display: flex;
  justify-content: center;
  padding: 0.9rem 1rem calc(0.9rem + env(safe-area-inset-bottom, 0));
  background: linear-gradient(180deg, rgba(13,13,13,0) 0%, rgba(13,13,13,0.95) 45%);
  /* la franja transparente no debe bloquear clics en el contenido de detrás */
  pointer-events: none;
}

.sticky-cta :deep(.cta-btn) {
  pointer-events: auto;
  padding: 1rem 1.25rem;
}
</style>

<style>
/* si el banner de cookies se vuelve a activar, el botón se coloca encima */
body.cookie-visible .sticky-cta { bottom: 72px; }
</style>
