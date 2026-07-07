<template>
  <section id="video" class="video-section">
    <div class="video-container">
      <div class="section-header">
        <span class="section-tag">{{ sectionTag }}</span>
        <h2 class="section-title">{{ sectionTitle }}</h2>
      </div>

      <!-- skeleton mientras carga -->
<div v-if="loading || !youtubeId" class="video-skeleton"></div>

<!-- video real cuando ya hay datos -->
<div v-else class="video-wrapper" @click="loadVideo">
  <div v-if="!videoLoaded" class="video-thumbnail">
    <img :src="thumbnailUrl" alt="Video thumbnail">
    <button class="play-button" aria-label="Reproducir video">
      <svg width="68" height="48" viewBox="0 0 68 48">
        <path d="M66.52,7.74c-0.78-2.93-2.49-5.41-5.42-6.19C55.79,.13,34,0,34,0S12.21,.13,6.9,1.55 C3.97,2.33,2.27,4.81,1.48,7.74C0.06,13.05,0,24,0,24s0.06,10.95,1.48,16.26c0.78,2.93,2.49,5.41,5.42,6.19 C12.21,47.87,34,48,34,48s21.79-0.13,27.1-1.55c2.93-0.78,4.64-3.26,5.42-6.19C67.94,34.95,68,24,68,24S67.94,13.05,66.52,7.74z" fill="#f00"></path>
        <path d="M 45,24 27,14 27,34" fill="#fff"></path>
      </svg>
    </button>
  </div>
  <iframe
    v-if="videoLoaded"
    class="video-frame"
    width="100%"
    height="100%"
    :src="embedUrl"
    title="Petru Workout"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
  ></iframe>
</div>
      <div class="video-cta">
        <h3 class="cta-title">{{ ctaTitle }}</h3>
        <p class="cta-description">{{ ctaDescription }}</p>
        <button
          class="btn-calendly-cta"
          @click="$emit('open-form')"
        >
          Revisar mi caso
        </button>
      </div>


    </div>
  </section>
</template>

<script>
import { trackCalendlyClick } from '@/utils/tracking.js'

export default {
  name: 'VideoSection',
  props: {
    content: { type: Object, default: null },
    loading: { type: Boolean, default: true }
  },
  data() {
    return { videoLoaded: false }
  },
  computed: {
    youtubeId() { return this.content?.youtube_id || null },
    sectionTag() { return this.content?.section_tag || 'EMPIEZA DESDE CERO' },
    sectionTitle() { return this.content?.title || 'Así cambia la gente cuando empieza bien (de verdad)' },
    ctaTitle() { return this.content?.cta_title || '¿Listo para tu cambio?' },
    ctaDescription() { return this.content?.cta_description || 'Llama gratis: Analizamos tu situación, te doy un plan claro para empezar y resolvemos todas tus dudas.' },
    thumbnailUrl() {
      if (!this.youtubeId) return null
      return `https://img.youtube.com/vi/${this.youtubeId}/maxresdefault.jpg`
    },
    embedUrl() {
      if (!this.youtubeId) return null
      return `https://www.youtube.com/embed/${this.youtubeId}?autoplay=1&rel=0&modestbranding=1`
    },
  },
  methods: {
    loadVideo() { this.videoLoaded = true }
  },
}
</script>

<style scoped>
.video-section {
  padding: 6rem 2rem;
  background: var(--bg-secondary);
}

.video-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-tag {
  font-size: 0.85rem;
  color: var(--color-accent);
  font-weight: 700;
  letter-spacing: 0.15em;
  display: block;
  margin-bottom: 1rem;
}
.video-skeleton {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.section-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  margin: 0 0 1rem 0;
}

.video-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  background: #000;
  cursor: pointer;
}

.video-thumbnail {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.8);
  border: none;
  border-radius: 20px;
  padding: 1rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.play-button:hover {
  background: rgba(255, 0, 0, 0.9);
  transform: translate(-50%, -50%) scale(1.1);
}

.play-button svg {
  display: block;
}

.video-frame {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-cta {
  text-align: center;
  margin-top: 3rem;
  padding: 2.5rem;
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.1) 0%, rgba(6, 214, 160, 0.05) 100%);
  border-radius: 20px;
  border: 2px solid rgba(6, 214, 160, 0.3);
}

.cta-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  margin: 0 0 1rem 0;
}

.cta-description {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  margin: 0 0 2rem 0;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.btn-calendly-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1.25rem 2.5rem;
  background: var(--gradient-primary);
  color: white;
  border: none;
  outline: none;
  cursor: pointer;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
}

.btn-calendly-cta:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.6);
}
.video-whatsapp-line {
  text-align: center;
  margin-top: 1rem;
  font-size: 1rem;
  color: var(--color-text-muted);
}

.video-whatsapp-phone {
  color: #25D366;
  font-weight: 700;
  text-decoration: none;
  transition: color 0.3s ease;
}

.video-whatsapp-phone:hover {
  color: #4dff8a;
  text-decoration: underline;
}
@media (max-width: 768px) {
  .video-section {
    padding: 4rem 1rem;
  }

  .section-title {
    font-size: 1.6rem;
  }

  .video-cta {
    padding: 2rem 1.5rem;
    margin-top: 2rem;
  }

  .cta-title {
    font-size: 1.5rem;
  }

  .cta-description {
    font-size: 1rem;
  }

  .btn-calendly-cta {
    width: 100%;
    justify-content: center;
    padding: 1rem 1.5rem;
    font-size: 1rem;
  }

}
</style>
