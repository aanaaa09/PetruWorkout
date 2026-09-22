<template>
  <section id="video" class="video-section">
    <div class="video-container">
      <div class="section-header">
        <span class="section-tag">{{ sectionTag }}</span>
        <h2 class="section-title">{{ sectionTitle }}</h2>
      </div>

      <!-- skeleton mientras carga -->
<div v-if="loading || !youtubeId" class="video-skeleton"></div>

      <div class="unified-card" @click="$emit('open-form')">
        <div class="video-wrapper">
          <div class="video-thumbnail">
            <img :src="thumbnailUrl" alt="Video thumbnail">
          </div>
        </div>
        
        <div class="client-result-bar" v-if="clientResult">
          {{ clientResult }}
        </div>

        <div class="video-cta">
          <button class="btn-calendly-cta btn-calendly-large">
            {{ ctaButtonText }}
          </button>
        </div>
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
    sectionTag() { return this.content?.section_tag || 'EMPIEZA CON ESTRUCTURA' },
    sectionTitle() { return this.content?.title || 'Esto es lo que pasa cuando sigues el paso a paso correcto para tu punto débil' },
    clientResult() { return this.content?.client_result || '[Nombre] tenía [punto débil concreto]. Esto es lo que cambió en 3 meses siguiendo su plan.' },

    ctaButtonText() { return this.content?.cta_button || 'DESCUBRIR MI PUNTO DÉBIL' },
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

.unified-card {
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.08) 0%, rgba(6, 214, 160, 0.03) 100%);
  border-radius: 20px;
  border: 2px solid rgba(6, 214, 160, 0.2);
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  cursor: pointer;
  transition: transform 0.3s ease, border-color 0.3s ease;
}
.unified-card:hover {
  transform: translateY(-4px);
  border-color: rgba(6, 214, 160, 0.4);
}

.video-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  background: #000;
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

.client-result-bar {
  background: rgba(0,0,0,0.3);
  padding: 1.5rem;
  font-size: 1.1rem;
  color: white;
  text-align: center;
  font-weight: 500;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.video-cta {
  text-align: center;
  padding: 2.5rem;
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

.btn-calendly-large {
  padding: 1.5rem 3.5rem;
  font-size: 1.25rem;
  font-weight: 800;
  width: 100%;
  max-width: 500px;
  justify-content: center;
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


  .btn-calendly-cta {
    width: 100%;
    justify-content: center;
    padding: 1rem 1.5rem;
    font-size: 1rem;
  }

}
</style>
