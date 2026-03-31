<template>
  <section id="resultados" class="results-section">
    <div class="results-container">
      <div class="section-header">
        <span class="section-tag">{{ content.section_tag || 'RESULTADOS REALES' }}</span>
        <h2 class="section-title">{{ content.title || 'Transformaciones de mis clientes' }}</h2>
      </div>

      <div class="results-grid">
        <div
          v-for="(user, index) in activeUsers"
          :key="user.id"
          class="result-card"
        >
          <div class="result-images">
            <img
              :srcset="`
                /images/results/${user.image_slug}-small.webp${imgV} 330w,
                /images/results/${user.image_slug}-medium.webp${imgV} 660w,
                /images/results/${user.image_slug}-large.webp${imgV} 1000w
              `"
              sizes="(max-width: 640px) 330px, (max-width: 968px) 660px, 500px"
              :src="`/images/results/${user.image_slug}-large.webp${imgV}`"
              :alt="user.name"
              width="534"
              height="501"
              loading="lazy"
              @error="handleImageError"
            />
          </div>

          <div class="result-info">
            <h4>{{ user.name }}{{ user.age ? ', ' + user.age : '' }}</h4>
            <p v-if="user.stats" class="result-stats-text">{{ user.stats }}</p>
            <p v-if="user.duration" class="result-duration">{{ user.duration }}</p>

            <div v-if="user.whatsapp_text" class="whatsapp-message">
              <div class="whatsapp-bubble">
                <p class="whatsapp-text">{{ user.whatsapp_text }}</p>
                <span class="whatsapp-time">{{ user.whatsapp_time || '' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- SECCIÓN DE VIDEOS -->
      <div class="videos-section">
        <div class="videos-header">
          <h3>{{ content.videos_title || 'Esto es lo que opinan mis clientes' }}</h3>
          <p>{{ content.videos_subtitle || 'Testimonios reales de personas que han logrado sus objetivos' }}</p>
        </div>

        <div class="videos-grid">
          <div
            v-for="video in videoTestimonials"
            :key="video.id"
            class="video-wrapper"
          >
            <!-- Overlay de play antes de reproducir -->
            <div
              v-if="!playingVideos[video.id]"
              class="video-play-overlay"
              @click="playVideo(video.id, $event)"
            >
              <div class="play-icon-wrap">
                <svg width="52" height="52" viewBox="0 0 52 52" fill="none">
                  <circle cx="26" cy="26" r="26" fill="rgba(0,0,0,0.55)"/>
                  <polygon points="21,16 39,26 21,36" fill="white"/>
                </svg>
              </div>
            </div>

            <video
              :ref="'video-' + video.id"
              :src="`${video.src}${videoV}`"
              controls
              playsinline
              preload="metadata"
              width="377"
              height="640"
              @play="onPlay(video.id)"
              @pause="onPause(video.id)"
              @ended="onPause(video.id)"
            >
              Tu navegador no soporta el video.
            </video>
          </div>
        </div>
      </div>

      <div class="results-cta">
        <p>¿Quieres ser el próximo?</p>
        <a
          href="https://calendly.com/petruworkout/reunion"
          target="_blank"
          rel="noopener noreferrer"
          class="btn btn-primary"
          @click="handleCalendlyClick"
        >
          Empieza Tu Transformación →
        </a>
      </div>
    </div>
  </section>
</template>

<script>
import { useContent } from '@/composables/useContent.js'
import { trackCalendlyClick } from '@/utils/tracking.js'

export default {
  name: 'ResultsSection',
  data() {
    return {
      content: {
        section_tag: 'RESULTADOS REALES',
        title: 'Transformaciones de mis clientes',
        videos_title: 'Esto es lo que opinan mis clientes',
        videos_subtitle: 'Testimonios reales de personas que han logrado sus objetivos',
        users: [],
        _img_version: null,
        _video_version: null,
      },
      videoTestimonials: [
        { id: 1, src: '/videos/video1.mp4' },
        { id: 2, src: '/videos/video2.mp4' },
        { id: 3, src: '/videos/video3.mp4' },
      ],
      playingVideos: {},
    }
  },
  computed: {
    activeUsers() {
      return (this.content.users || []).filter(u => u.name && u.name.trim())
    },
    imgV() {
      return this.content._img_version ? `?v=${this.content._img_version}` : ''
    },
    videoV() {
      return this.content._video_version ? `?v=${this.content._video_version}` : ''
    },
  },
  async mounted() {
    try {
      const c = await useContent()
      if (c?.results) {
        this.content = { ...this.content, ...c.results }
      }
    } catch (e) {
      console.warn('useContent error:', e)
    }
  },
  methods: {
    handleImageError(e) {
      if (e.target.dataset.errorHandled) return
      e.target.dataset.errorHandled = 'true'
      e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="250"%3E%3Crect width="200" height="250" fill="%231a1a1a"/%3E%3Ctext x="50%25" y="50%25" font-size="24" fill="%23e63946" text-anchor="middle" dominant-baseline="middle"%3EFOTO%3C/text%3E%3C/svg%3E'
    },
    playVideo(id) {
      this.playingVideos = { ...this.playingVideos, [id]: true }
      this.$nextTick(() => {
        const ref = this.$refs[`video-${id}`]
        const el = Array.isArray(ref) ? ref[0] : ref
        if (el) el.play()
      })
    },
    onPlay(id) {
      this.playingVideos = { ...this.playingVideos, [id]: true }
    },
    onPause(id) {
      this.playingVideos = { ...this.playingVideos, [id]: false }
    },
    handleCalendlyClick() {
      trackCalendlyClick('results-cta-button', 'results-section')
    },
  },
}
</script>

<style scoped>
.results-section {
  padding: 6rem 2rem;
  background: var(--bg-secondary);
}

.results-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-tag {
  font-size: 0.85rem;
  color: var(--color-accent);
  font-weight: 700;
  letter-spacing: 0.15em;
  display: block;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  margin: 0 0 1rem 0;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
}

.result-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.result-card:hover {
  transform: translateY(-5px);
  border-color: rgba(6, 214, 160, 0.3);
}

.result-images {
  padding: 1.5rem;
  background: rgba(0, 0, 0, 0.2);
}

.result-images img {
  width: 100%;
  height: auto;
  border-radius: 10px;
  object-fit: cover;
}

.result-info { padding: 1.5rem; }
.result-info h4 { font-size: 1.5rem; color: white; margin: 0 0 0.5rem 0; font-weight: 700; }
.result-stats-text { font-size: 1rem; color: var(--color-accent); font-weight: 600; margin: 0 0 0.25rem 0; }
.result-duration { font-size: 0.9rem; color: var(--color-text-muted); margin: 0 0 1rem 0; font-weight: 500; }

.whatsapp-message { margin-top: 1rem; }
.whatsapp-bubble {
  background: linear-gradient(135deg, #128C7E 0%, #075E54 100%);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  position: relative;
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
.whatsapp-bubble::before {
  content: '';
  position: absolute;
  top: 0; left: -8px;
  width: 0; height: 0;
  border-style: solid;
  border-width: 0 8px 8px 0;
  border-color: transparent #075E54 transparent transparent;
}
.whatsapp-text { color: #ffffff; font-size: 0.9rem; line-height: 1.5; margin: 0 0 0.5rem 0; word-wrap: break-word; }
.whatsapp-time { display: block; text-align: right; font-size: 0.7rem; color: rgba(255,255,255,0.6); margin-top: 0.25rem; }

/* Videos section */
.videos-section {
  margin-top: 5rem;
  padding-top: 4rem;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.videos-header { text-align: center; margin-bottom: 3rem; }
.videos-header h3 { font-size: 2rem; font-weight: 700; color: white; margin: 0 0 1rem 0; }
.videos-header p  { font-size: 1.1rem; color: var(--color-text-muted); margin: 0; }

.videos-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }

.video-wrapper {
  border-radius: 12px;
  overflow: hidden;
  background: rgba(20, 20, 20, 0.9);
  border: 1px solid rgba(255,255,255,0.08);
  transition: all 0.3s ease;
  aspect-ratio: 9 / 16;
  position: relative;
}
.video-wrapper:hover { border-color: rgba(6,214,160,0.3); }

.video-wrapper video {
  width: 100%; height: 100%;
  display: block; object-fit: cover;
  position: absolute; top: 0; left: 0;
}

/* Custom play overlay */
.video-play-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: rgba(0, 0, 0, 0.25);
  transition: background 0.2s;
}
.video-play-overlay:hover {
  background: rgba(0, 0, 0, 0.4);
}
.play-icon-wrap {
  transition: transform 0.2s;
}
.video-play-overlay:hover .play-icon-wrap {
  transform: scale(1.12);
}

/* CTA */
.results-cta {
  text-align: center;
  margin-top: 4rem;
  padding: 3rem;
  background: linear-gradient(135deg, rgba(6,214,160,0.1) 0%, rgba(6,214,160,0.05) 100%);
  border-radius: 20px;
  border: 1px solid rgba(6,214,160,0.2);
}
.results-cta p { font-size: 1.5rem; font-weight: 700; color: white; margin: 0 0 1.5rem 0; }

.btn-primary {
  display: inline-block;
  background: var(--gradient-primary);
  color: white;
  padding: 1rem 2.5rem;
  border-radius: 10px;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 8px 30px rgba(6,214,160,0.4);
  transition: all 0.3s ease;
}
.btn-primary:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(6,214,160,0.5); }

@media (max-width: 968px) {
  .results-grid  { grid-template-columns: 1fr; max-width: 500px; margin: 0 auto; }
  .videos-grid   { grid-template-columns: 1fr; max-width: 380px; margin: 0 auto; }
}

@media (max-width: 640px) {
  .results-section  { padding: 4rem 1rem; }
  .section-title    { font-size: 2rem; }
  .result-info h4   { font-size: 1.3rem; }
  .whatsapp-text    { font-size: 0.85rem; }
  .videos-header h3 { font-size: 1.5rem; }
  .results-cta      { padding: 2rem 1.5rem; }
  .results-cta p    { font-size: 1.25rem; }
}
</style>
