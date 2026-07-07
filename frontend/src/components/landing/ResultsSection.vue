<template>
  <section id="resultados" class="results-section">
    <div class="results-container">
      <div class="section-header">
        <span class="section-tag">{{ sectionTag }}</span>
        <h2 class="section-title">{{ sectionTitle }}</h2>
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

      <!-- CTA DEBAJO DE LAS FOTOS -->
      <div class="results-cta">
        <p>El siguiente cambio puede ser el tuyo</p>
        <button
          class="btn btn-primary"
          @click="$emit('open-form')"
        >
          Descubre cómo mejorar →
        </button>
      </div>

      <!-- SECCIÓN DE VIDEOS -->
      <div class="videos-section">
        <div class="videos-header">
          <h3>{{ videosTitle }}</h3>
          <p>{{ videosSubtitle }}</p>
        </div>

        <div class="videos-grid">
          <div
            v-for="video in videoTestimonials"
            :key="video.id"
            class="video-wrapper"
          >
            <div
              v-if="!playingVideos[video.id]"
              class="video-play-overlay"
              @click="playVideo(video.id)"
            >
              <img
                v-if="video.poster"
                :src="video.poster"
                :srcset="video.posterSmall ? `${video.posterSmall} 400w, ${video.poster} 800w` : undefined"
                sizes="(max-width: 640px) 400px, 800px"
                :alt="'Testimonio ' + video.id"
                class="video-poster"
              />
              <div class="play-icon-wrap">
                <svg width="52" height="52" viewBox="0 0 52 52" fill="none">
                  <circle cx="26" cy="26" r="26" fill="rgba(0,0,0,0.55)"/>
                  <polygon points="21,16 39,26 21,36" fill="white"/>
                </svg>
              </div>
            </div>

            <video
              :ref="'video-' + video.id"
              :src="video.src"
              :poster="video.poster || undefined"
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

      <!-- SECCIÓN REGALO -->
      <div class="gift-cta-section">
        <div class="gift-cta-inner">
          <div class="gift-icon-wrap">🎁</div>
          <h3 class="gift-title">Si has llegado hasta aquí, tienes un regalo</h3>
          <p class="gift-subtitle">
            Únete al grupo privado de WhatsApp y accede a la calculadora de calorías personalizada
          </p>
          <button class="btn-gift" @click="showGiftModal = true">
            Únete al grupo + calculadora de calorías 🎁
          </button>
        </div>
      </div>

      <!-- Modal regalo -->
      <transition name="modal-fade">
        <div v-if="showGiftModal" class="modal-overlay" @click.self="closeGiftModal">
          <div class="modal-content">
            <button @click="closeGiftModal" class="modal-close">✕</button>

            <h2 class="modal-title">🎁 Accede al regalo exclusivo</h2>
            <p class="modal-description">
              Únete al grupo privado y recibe tu regalo de bienvenida
            </p>

            <form @submit.prevent="handleGiftSubmit" class="email-form">
              <div class="form-group">
                <input
                  v-model="giftEmail"
                  type="email"
                  placeholder="tu@email.com"
                  required
                  class="email-input"
                  :class="{ 'input-error': giftEmailError }"
                  @input="giftEmailError = ''"
                />
                <span v-if="giftEmailError" class="error-text">{{ giftEmailError }}</span>
              </div>

              <div class="checkbox-group">
                <input
                  v-model="giftAcceptPrivacy"
                  type="checkbox"
                  id="gift-privacy"
                  required
                />
                <label for="gift-privacy">
                  Acepto la
                  <router-link
                    to="/info?legal=privacy"
                    class="link-button"
                    @click="closeGiftModal"
                  >
                    política de privacidad
                  </router-link>
                </label>
              </div>

              <div v-if="giftError" class="error-message">{{ giftError }}</div>
              <div v-if="giftSuccess" class="success-message">{{ giftSuccess }}</div>

              <button
                type="submit"
                class="btn-submit"
                :disabled="giftLoading"
              >
                {{ giftLoading ? '⏳ Procesando...' : 'Accede al grupo y a mi regalo' }}
              </button>
            </form>
          </div>
        </div>
      </transition>

    </div>
  </section>
</template>
<script>
import { trackCalendlyClick } from '@/utils/tracking.js'

export default {
  name: 'ResultsSection',
  props: {
    content: { type: Object, default: null },
    loading: { type: Boolean, default: true }
  },
  data() {
    return {
      videoTestimonials: [
        { id: 1, src: '/videos/video1.mp4', poster: '/videos/thumbs/thumb1.webp', posterSmall: '/videos/thumbs/thumb1-small.webp' },
        { id: 2, src: '/videos/video2.mp4', poster: '/videos/thumbs/thumb2.webp', posterSmall: '/videos/thumbs/thumb2-small.webp' },
        { id: 3, src: '/videos/video3.mp4', poster: '/videos/thumbs/thumb3.webp', posterSmall: '/videos/thumbs/thumb3-small.webp' },
      ],
      playingVideos: {},
      showGiftModal: false,
      giftEmail: '',
      giftAcceptPrivacy: false,
      giftLoading: false,
      giftError: '',
      giftSuccess: '',
      giftEmailError: '',
    }
  },
  computed: {
    sectionTag() { return this.content?.section_tag || 'RESULTADOS REALES' },
    sectionTitle() { return this.content?.title || 'Transformaciones de mis clientes' },
    videosTitle() { return this.content?.videos_title || 'Esto es lo que opinan mis clientes' },
    videosSubtitle() { return this.content?.videos_subtitle || 'Testimonios reales de personas que han logrado sus objetivos' },
    activeUsers() {
      return (this.content?.users || []).filter(u => u.name && u.name.trim())
    },
    imgV() {
      return this.content?._img_version ? `?v=${this.content._img_version}` : ''
    },
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
    onPlay(id)  { this.playingVideos = { ...this.playingVideos, [id]: true  } },
    onPause(id) { this.playingVideos = { ...this.playingVideos, [id]: false } },
    onPause(id) { this.playingVideos = { ...this.playingVideos, [id]: false } },
    closeGiftModal() {
      this.showGiftModal = false
      this.giftEmail = ''
      this.giftAcceptPrivacy = false
      this.giftError = ''
      this.giftSuccess = ''
      this.giftLoading = false
      this.giftEmailError = ''
    },
    validateGiftEmail() {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!this.giftEmail) { this.giftEmailError = ''; return true }
      if (!emailRegex.test(this.giftEmail)) {
        this.giftEmailError = 'Formato de email incorrecto (ejemplo: correo@gmail.com)'
        return false
      }
      this.giftEmailError = ''
      return true
    },
    async handleGiftSubmit() {
      this.giftError = ''
      this.giftSuccess = ''
      this.giftEmailError = ''
      if (!this.validateGiftEmail()) { this.giftError = 'Por favor, introduce un email válido'; return }
      if (!this.giftAcceptPrivacy)   { this.giftError = 'Debes aceptar la política de privacidad'; return }
      this.giftLoading = true
      try {
        const response = await fetch('https://petruworkout-production.up.railway.app/api/lead/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: this.giftEmail }),
        })
        const data = await response.json()
        sessionStorage.setItem('petru_has_team_access', 'true')
        if (response.ok) {
          this.giftSuccess = data.nuevo
            ? '¡Perfecto! Revisa tu email. Redirigiendo...'
            : '¡Ya estás registrado! Redirigiendo...'
          setTimeout(() => this.$router.push('/team'), 2000)
        } else {
          this.giftError = data.error || 'Error al registrar. Intenta de nuevo.'
        }
      } catch {
        this.giftError = 'Error de conexión. Intenta de nuevo.'
      } finally {
        this.giftLoading = false
      }
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

.result-images { padding: 1.5rem; background: rgba(0, 0, 0, 0.2); }
.result-images img { width: 100%; height: auto; border-radius: 10px; object-fit: cover; }

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

/* CTA debajo de fotos */
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
  border: none;
  outline: none;
  border-radius: 10px;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 8px 30px rgba(6,214,160,0.4);
  transition: all 0.3s ease;
}
.btn-primary:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(6,214,160,0.5); }

/* Videos */
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
.video-poster {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: cover; z-index: 0;
}
.video-play-overlay {
  position: absolute; inset: 0; z-index: 2;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; background: rgba(0, 0, 0, 0.15); transition: background 0.2s;
}
.video-play-overlay:hover { background: rgba(0, 0, 0, 0.35); }
.play-icon-wrap { position: relative; z-index: 3; transition: transform 0.2s; }
.video-play-overlay:hover .play-icon-wrap { transform: scale(1.12); }

/* Sección regalo */
.gift-cta-section {
  margin-top: 5rem;
  padding-top: 4rem;
  border-top: 1px solid rgba(255,255,255,0.1);
}
.gift-cta-inner {
  text-align: center;
  padding: 3.5rem 2rem;
  background: linear-gradient(135deg, rgba(6,214,160,0.12) 0%, rgba(6,214,160,0.04) 100%);
  border: 2px solid rgba(6,214,160,0.35);
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
}
.gift-icon-wrap {
  font-size: 3.5rem;
  animation: giftBounce 2.5s ease-in-out infinite;
}
@keyframes giftBounce {
  0%, 100% { transform: translateY(0) rotate(-5deg); }
  50%       { transform: translateY(-10px) rotate(5deg); }
}
.gift-title {
  font-size: clamp(1.5rem, 3vw, 2.25rem);
  font-weight: 900;
  color: white;
  margin: 0;
  line-height: 1.2;
  max-width: 700px;
}
.gift-subtitle {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  margin: 0;
  max-width: 580px;
  line-height: 1.6;
}
.btn-gift {
  background: var(--gradient-primary);
  color: white;
  padding: 1.2rem 2.5rem;
  border: none;
  border-radius: 12px;
  font-weight: 800;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6,214,160,0.4);
  margin-top: 0.5rem;
}
.btn-gift:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(6,214,160,0.6); }

/* Modal */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.85);
  backdrop-filter: blur(10px);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999; padding: 1rem;
}
.modal-content {
  background: rgba(26,26,26,0.98);
  border: 1px solid rgba(6,214,160,0.3);
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 500px; width: 100%;
  position: relative;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.modal-close {
  position: absolute; top: 1rem; right: 1rem;
  background: rgba(255,255,255,0.1); border: none; color: white;
  width: 35px; height: 35px; border-radius: 50%; cursor: pointer;
  font-size: 1.5rem; display: flex; align-items: center; justify-content: center;
  transition: all 0.3s ease;
}
.modal-close:hover { background: rgba(255,255,255,0.2); transform: rotate(90deg); }
.modal-title { font-size: 1.75rem; color: white; margin: 0 0 0.5rem 0; text-align: center; }
.modal-description { font-size: 1rem; color: var(--color-text-secondary); text-align: center; margin: 0 0 2rem 0; }

.email-form { display: flex; flex-direction: column; gap: 1.5rem; }
.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.email-input {
  padding: 1rem;
  border: 2px solid rgba(6,214,160,0.3); border-radius: 10px;
  background: rgba(255,255,255,0.05); color: white; font-size: 1rem;
  transition: all 0.3s ease;
}
.email-input.input-error { border-color: rgba(239,35,60,0.5); background: rgba(239,35,60,0.1); }
.email-input::placeholder { color: var(--color-text-muted); }
.email-input:focus { outline: none; border-color: var(--color-accent); background: rgba(255,255,255,0.08); }
.error-text { color: #ff6b6b; font-size: 0.85rem; font-weight: 600; }

.checkbox-group {
  display: flex; align-items: flex-start; gap: 0.75rem;
  font-size: 0.9rem; color: var(--color-text-secondary);
}
.checkbox-group input[type="checkbox"] { margin-top: 0.25rem; width: 18px; height: 18px; cursor: pointer; flex-shrink: 0; }
.link-button {
  color: var(--color-accent); text-decoration: underline; cursor: pointer;
  font-size: inherit; padding: 0; font-family: inherit; background: none; border: none;
}
.link-button:hover { color: var(--color-accent-light); }

.error-message {
  padding: 0.875rem; background: rgba(239,35,60,0.2); border: 1px solid rgba(239,35,60,0.4);
  border-radius: 10px; color: #ff6b6b; font-weight: 600; text-align: center;
}
.success-message {
  padding: 0.875rem; background: rgba(6,214,160,0.2); border: 1px solid rgba(6,214,160,0.4);
  border-radius: 10px; color: var(--color-accent); font-weight: 600; text-align: center;
}
.btn-submit {
  background: var(--gradient-primary); color: white; padding: 1rem 2rem;
  border: none; border-radius: 10px; font-weight: 700; font-size: 1rem;
  cursor: pointer; transition: all 0.3s ease; box-shadow: 0 8px 30px rgba(6,214,160,0.4);
}
.btn-submit:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 12px 40px rgba(6,214,160,0.6); }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

/* Responsive */
@media (max-width: 968px) {
  .results-grid   { grid-template-columns: 1fr; max-width: 500px; margin: 0 auto; }
  .videos-grid    { grid-template-columns: 1fr; max-width: 380px; margin: 0 auto; }
  .gift-cta-inner { padding: 2.5rem 1.5rem; }
}
@media (max-width: 640px) {
  .results-section { padding: 4rem 1rem; }
  .section-title   { font-size: 2rem; }
  .result-info h4  { font-size: 1.3rem; }
  .whatsapp-text   { font-size: 0.85rem; }
  .videos-header h3 { font-size: 1.5rem; }
  .results-cta     { padding: 2rem 1.5rem; }
  .results-cta p   { font-size: 1.25rem; }
  .gift-title      { font-size: 1.5rem; }
  .btn-gift        { width: 100%; font-size: 1rem; }
  .modal-content   { padding: 2rem 1.5rem; margin: 1rem; }
  .modal-title     { font-size: 1.5rem; }
}
</style>
