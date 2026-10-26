<template>
  <section id="hero" class="hero-section">
    <div class="hero-content">
      <h1 class="hero-title" v-html="heroTitle"></h1>
      <p class="hero-sub">{{ heroSub }}</p>

      <!-- BOCETO: clips de ejemplo, se sustituyen por los vídeos reales de clientes -->
      <div class="clips" ref="clips">
        <figure v-for="(clip, i) in clips" :key="i" class="clip">
          <video
            :src="clip.src"
            :poster="clip.poster"
            loop
            muted
            playsinline
            preload="metadata"
            aria-hidden="true"
          ></video>
          <figcaption>
            <strong>{{ clip.name }}</strong>
            <span class="clip-result">{{ clip.result }}</span>
            <span class="clip-time">{{ clip.time }}</span>
          </figcaption>
        </figure>
      </div>

      <div class="cta-box">
        <CtaButton @click="$emit('open-form')">{{ btnText }}</CtaButton>
        <p class="cta-note">{{ note }}</p>
      </div>
    </div>
  </section>
</template>

<script>
import CtaButton from '@/components/landing/CtaButton.vue'

export default {
  name: 'HeroSection',
  components: { CtaButton },
  props: {
    content: { type: Object, default: null },
    loading: { type: Boolean, default: true }
  },
  data() {
    return {
      observer: null,
      // .t2 pasa a línea propia solo en escritorio (siempre 2 líneas)
      heroTitle: 'Un cuerpo <span class="highlight">fuerte y ágil</span> <span class="t2">a&nbsp;los&nbsp;30, a&nbsp;los&nbsp;40 y&nbsp;a&nbsp;los&nbsp;50</span>',
      heroSub: 'Mira lo que consiguen mis clientes.',
      btnText: 'Descubre qué te frena',
      note: '30 segundos · Gratis · Sin presión',      clips: [
        // Pedro (63) primero: es la prueba más fuerte para quien tiene 50 o más
        { src: '/videos/hero/pedro.mp4', poster: '/videos/hero/pedro.webp', name: 'Pedro, 63 años', result: 'De 1 a 10 dominadas', time: '6 meses' },
        { src: '/videos/hero/handstand.mp4', poster: '/videos/hero/handstand.webp', name: 'Franck, 29 años', result: 'De 0 a 30 s de pino', time: '6 meses' },
        { src: '/videos/hero/muscleup.mp4', poster: '/videos/hero/muscleup.webp', name: 'Sergio, 42 años', result: 'De 0 a 2 muscle-ups', time: '3 meses' },
      ],
    }
  },
  mounted() {
    const videos = this.$refs.clips?.querySelectorAll('video') || []
    // Solo se reproducen los clips visibles: ahorra datos y batería en móvil
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(({ target, isIntersecting }) => {
        if (isIntersecting) target.play().catch(() => {})
        else target.pause()
      })
    }, { threshold: 0.4 })
    videos.forEach(v => {
      v.muted = true
      this.observer.observe(v)
    })
  },
  beforeUnmount() {
    this.observer?.disconnect()
  },
}
</script>

<style scoped>
.hero-section {
  display: flex;
  justify-content: center;
  padding: 6rem 2rem 3rem;
  background: linear-gradient(135deg, rgba(13,13,13,0.95) 0%, rgba(26,26,26,0.9) 100%);
}

.hero-content {
  width: 100%;
  max-width: 1000px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1.5rem;
}

.hero-title {
  font-size: clamp(1.75rem, 4.5vw, 3rem);
  font-weight: 900;
  line-height: 1.15;
  color: white;
  margin: 0;
  max-width: 800px;
  text-wrap: balance;
}
:deep(.hero-title .highlight) { color: var(--color-accent); }

.hero-sub {
  margin: -0.5rem 0 0;
  font-size: 1.1rem;
  color: var(--color-text-muted);
}

/* ===== CLIPS ===== */
.clips {
  display: flex;
  justify-content: center;
  gap: 1rem;
  width: 100%;
}

.clip {
  position: relative;
  margin: 0;
  flex: 0 0 auto;
  width: clamp(180px, 22vw, 230px);
  aspect-ratio: 9 / 16;
  border-radius: 16px;
  overflow: hidden;
  background: #000;
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 20px 40px rgba(0,0,0,0.45);
}

.clip video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.clip figcaption {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  padding: 2.5rem 0.75rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  text-align: left;
  background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.85) 100%);
}
.clip figcaption strong { color: white; font-size: 0.95rem; }
.clip figcaption span { display: block; color: var(--color-accent); font-size: 0.8rem; font-weight: 700; }
/* el punto queda al final de la primera línea y el plazo siempre va entero en la segunda */
.clip figcaption .clip-result::after { content: ' ·'; }
.clip figcaption .clip-time {
  color: white;
  font-weight: 800;
  /* borde negro alrededor del texto blanco */
  text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000, 0 0 4px #000;
  white-space: nowrap;
}

/* ===== BOTÓN PRINCIPAL ===== */
.cta-box {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.9rem;
  margin-top: 0.5rem;
}

.cta-note {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-muted);
  line-height: 1.4;
}

/* ===== ESCRITORIO =====
   Todo el hero crece con la altura de la ventana: lo más grande posible
   pero con el botón siempre visible sin hacer scroll (portátiles incluidos) */
@media (min-width: 769px) {
  .hero-section { padding: 5rem 2rem 2rem; }
  .hero-content { max-width: 1200px; gap: 1.1rem; }
  .hero-title { font-size: clamp(2rem, 5.2vh, 3.6rem); max-width: 1000px; }
  :deep(.hero-title .t2) { display: block; }
  .hero-sub { margin-top: -0.25rem; font-size: clamp(1.05rem, 2.2vh, 1.35rem); }
  .clips { gap: 1.5rem; }
  .clip { width: auto; height: clamp(260px, calc(100vh - 410px), 640px); border-radius: 20px; }
  .clip figcaption { padding: 3rem 1rem 1rem; }
  .clip figcaption strong { font-size: 1.1rem; }
  .clip figcaption span { font-size: 0.95rem; }
  .cta-box { margin-top: 0.25rem; gap: 0.7rem; }
  .cta-box :deep(.cta-btn) { max-width: 560px; padding: 1.35rem 2rem; font-size: 1.45rem; }
  .cta-note { font-size: 1.05rem; }
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .hero-section { padding: 5rem 0 2rem; }
  .hero-content { gap: 1.1rem; }
  .hero-title { padding: 0 1.25rem; }
  .hero-sub { padding: 0 1.25rem; font-size: 1rem; }

  /* carrusel horizontal con el siguiente clip asomando */
  .clips {
    justify-content: flex-start;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    padding: 0 1.25rem;
    scroll-padding: 0 1.25rem;
    gap: 0.75rem;
    scrollbar-width: none;
  }
  .clips::-webkit-scrollbar { display: none; }
  .clip { width: 148px; scroll-snap-align: start; }
  .clip figcaption strong { font-size: 0.8rem; }
  .clip figcaption span { font-size: 0.7rem; }

  .cta-box { padding: 0 1.25rem; }
  .cta-note { font-size: 0.8rem; }
}
</style>
