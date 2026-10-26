<template>
  <button class="cta-btn" :class="{ 'cta-calm': calm }" type="button">
    <span class="cta-label"><slot /></span>
    <span class="cta-arrow" aria-hidden="true">→</span>
  </button>
</template>

<script>
// Botón principal de la web: mismo aspecto y animación en todas las secciones
export default {
  name: 'CtaButton',
  props: {
    // true = sin animación ni efecto al pasar el ratón (para el botón fijo)
    calm: { type: Boolean, default: false }
  },
}
</script>

<style scoped>
.cta-btn {
  position: relative;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  width: 100%;
  max-width: 460px;
  padding: 1.25rem 1.5rem;
  border: none;
  outline: none;
  border-radius: 14px;
  background: var(--gradient-primary);
  color: #06120e;
  font-family: inherit;
  font-size: clamp(1.05rem, 4.8vw, 1.3rem);
  font-weight: 900;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  cursor: pointer;
  box-shadow: 0 10px 34px rgba(6, 214, 160, 0.5);
  animation: cta-pulse 2.2s ease-out infinite;
  transition: transform 0.2s ease;
}

.cta-btn:hover {
  transform: translateY(-3px) scale(1.02);
}

.cta-btn:active {
  transform: scale(0.98);
}

.cta-btn:focus-visible {
  outline: 3px solid white;
  outline-offset: 3px;
}

/* brillo que cruza el botón cada pocos segundos */
.cta-btn::after {
  content: '';
  position: absolute;
  top: 0;
  left: -60%;
  width: 40%;
  height: 100%;
  background: linear-gradient(100deg, transparent, rgba(255, 255, 255, 0.55), transparent);
  transform: skewX(-20deg);
  animation: cta-shine 3.6s ease-in-out infinite;
}

.cta-arrow {
  font-size: 1.4em;
  line-height: 1;
  animation: cta-nudge 1.2s ease-in-out infinite;
}

@keyframes cta-pulse {
  0%   { box-shadow: 0 10px 34px rgba(6, 214, 160, 0.5), 0 0 0 0 rgba(6, 214, 160, 0.55); }
  70%  { box-shadow: 0 10px 34px rgba(6, 214, 160, 0.5), 0 0 0 18px rgba(6, 214, 160, 0); }
  100% { box-shadow: 0 10px 34px rgba(6, 214, 160, 0.5), 0 0 0 0 rgba(6, 214, 160, 0); }
}

@keyframes cta-shine {
  0%, 55% { left: -60%; }
  100%    { left: 130%; }
}

@keyframes cta-nudge {
  0%, 100% { transform: translateX(0); }
  50%      { transform: translateX(5px); }
}

.cta-calm,
.cta-calm .cta-arrow {
  animation: none;
}
.cta-calm {
  box-shadow: 0 6px 20px rgba(6, 214, 160, 0.35);
}
.cta-calm::after {
  display: none;
}
.cta-calm:hover,
.cta-calm:active {
  transform: none;
}

@media (prefers-reduced-motion: reduce) {
  .cta-btn,
  .cta-btn::after,
  .cta-arrow { animation: none; }
}
</style>
