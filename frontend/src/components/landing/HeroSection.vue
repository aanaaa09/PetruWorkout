<template>
  <section id="hero" class="hero-section">
    <div class="hero-bg">
      <div class="hero-overlay"></div>
    </div>

    <div class="hero-content">
      <div class="hero-text">
        <h1 class="hero-title">
          {{ heroTitle }}<span class="highlight"> {{ heroHighlight }}</span>
        </h1>

        <ul class="benefits-list">
          <li v-for="(benefit, i) in benefits" :key="i">
            <span class="check">✅</span>
            {{ benefit }}
          </li>
        </ul>

        <!-- Botón Calendly (ahora abre modal) -->
        <button
          class="btn-gift"
          @click="openModal"
        >
          {{ btnText }}
        </button>
      </div>

      <!-- Imagen escritorio -->
      <div class="hero-image hero-image-desktop">
        <img
          :src="desktopImage"
          alt="Petru - Entrenador Personal de Calistenia"
          width="441"
          height="450"
          fetchpriority="high"
          loading="eager"
          @error="handleImageError"
        />
      </div>

      <!-- Imagen móvil -->
      <div class="hero-image hero-image-mobile">
        <img
          :src="mobileImage"
          alt="Petru - Entrenador Personal de Calistenia"
          width="300"
          height="300"
          fetchpriority="high"
          loading="eager"
          @error="handleImageError"
        />
      </div>
    </div>

    <div class="scroll-indicator">
      <span>Descubre más</span>
      <div class="scroll-arrow">↓</div>
    </div>

    <!-- Modal de Ayuda -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h2 class="modal-title">¿Necesitas ayuda para mejorar en calistenia?</h2>
        <div class="modal-actions">
          <a
            href="https://calendly.com/petruworkout/reunion"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-yes"
            @click="handleCalendlyClick"
          >
            Sí
          </a>
          <button class="btn-no" @click="closeModal">
            No
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { trackCalendlyClick } from '@/utils/tracking.js'

export default {
  name: 'HeroSection',
  props: {
    content: { type: Object, default: null },
    loading: { type: Boolean, default: true }
  },
  data() {
    return {
      showModal: false
    }
  },
  computed: {
    heroTitle() {
      return this.content?.title || 'El Sistema para entrenar en Casa o en el Parque y conseguir'
    },
    heroHighlight() {
      return this.content?.highlight || 'fuerza real'
    },
    benefits() {
      return this.content?.benefits?.length ? this.content.benefits : [
        'Cuerpo atlético y definido',
        'Gana fuerza y movilidad para el día a día',
        'Estrategia secreta para activar tu metabolismo y quemar grasa',
        'Motivación diaria para mantenerte constante y no abandonar',
      ]
    },
    btnText() {
      return this.content?.calendly_button_text || 'EMPIEZA AHORA'
    },
    desktopImage() {
      return this.content?.desktop_image || '/images/petru-hero-nuevo.webp'
    },
    mobileImage() {
      return this.content?.mobile_image || '/images/petru-hero-nuevo.webp'
    },
  },
  methods: {
    handleImageError(e) { e.target.style.display = 'none' },
    openModal() {
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    handleCalendlyClick() {
      trackCalendlyClick('hero-calendly-button', 'hero-section')
      this.showModal = false
    },
  },
}
</script>
<style scoped>
/* ===== ESTILOS GENERALES ===== */
.hero-section {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  padding: 6rem 2rem 4rem;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 0;
  background: linear-gradient(135deg, rgba(13,13,13,0.95) 0%, rgba(26,26,26,0.90) 100%);
}

.hero-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, rgba(13,13,13,0.95) 0%, rgba(26,26,26,0.85) 50%, rgba(13,13,13,0.9) 100%);
}

/* ===== CONTENIDO HERO ===== */
.hero-content {
  max-width: 1400px;
  width: 100%;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 4rem;
  align-items: center;
  position: relative;
  z-index: 1;
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.hero-title {
  font-size: clamp(1.8rem, 4vw, 3rem);
  font-weight: 900;
  line-height: 1.2;
  color: white;
  margin: 0;
}

.hero-title .highlight { color: var(--color-accent); }

.benefits-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.benefits-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.check {
  color: var(--color-accent);
  font-size: 1.3rem;
  flex-shrink: 0;
  line-height: 1.4;
}

.btn-gift {
  display: inline-block;
  background: var(--gradient-primary);
  color: white;
  padding: 1.2rem 2rem;
  border: none;
  border-radius: 12px;
  font-weight: 800;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6,214,160,0.4);
  text-align: center;
  text-decoration: none;
}
.btn-gift:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(6,214,160,0.6);
}

/* ===== IMÁGENES ===== */
.hero-image-desktop { position: relative; display: flex; justify-content: center; }
.hero-image-mobile  { display: none; }

.hero-image img {
  max-width: 750px;
  width: 100%;
  height: 450px;
  object-fit: cover;
  object-position: center;
  border-radius: 20px;
  box-shadow: 0 30px 60px rgba(0,0,0,0.5);
}

/* ===== SCROLL ===== */
.scroll-indicator {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-muted);
  font-size: 0.85rem;
  animation: bounce 2s infinite;
}
.scroll-arrow { font-size: 1.5rem; }

@keyframes bounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50%       { transform: translateX(-50%) translateY(10px); }
}

/* ===== RESPONSIVE ===== */
@media (max-width: 1024px) {
  .hero-content { grid-template-columns: 1fr; gap: 3rem; text-align: center; }
  .hero-text { align-items: center; }
  .benefits-list { align-items: flex-start; max-width: 600px; text-align: left; }
  .hero-image-desktop { order: -1; }
  .hero-image img { max-width: 450px; }
}

@media (max-width: 640px) {
  .hero-section { padding: 5rem 1.5rem 3rem; }
  .hero-content { grid-template-columns: 1fr; gap: 2.5rem; }
  .hero-text { order: 2; align-items: center; text-align: center; gap: 1.5rem; }
  .hero-image-desktop { display: none; }
  .hero-image-mobile  { display: flex; order: 1; justify-content: center; }
  .hero-image img     { max-width: 300px; width: 100%; height: auto; }
  .hero-title         { font-size: 1.75rem; }
  .benefits-list      { order: 3; align-items: flex-start; width: 100%; text-align: left; gap: 0.875rem; }
  .benefits-list li   { font-size: 1rem; }
  .btn-gift           { order: 2; font-size: 1rem; padding: 1.1rem 1.5rem; width: 100%; }
  .scroll-indicator   { display: none; }
}

/* ===== MODAL AYUDA ===== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: #1a1a1a;
  padding: 3rem 2rem;
  border-radius: 20px;
  text-align: center;
  max-width: 450px;
  width: 90%;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  border: 1px solid rgba(255,255,255,0.1);
  animation: slideUp 0.3s ease-out;
}

.modal-title {
  color: white;
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 2rem;
  line-height: 1.3;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-yes, .btn-no {
  padding: 1rem 2rem;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  text-decoration: none;
  display: flex;
  justify-content: center;
  align-items: center;
}

.btn-yes {
  background: var(--gradient-primary);
  color: white;
  border: none;
  box-shadow: 0 4px 15px rgba(6,214,160,0.3);
}

.btn-yes:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(6,214,160,0.5);
}

.btn-no {
  background: transparent;
  color: #a0a0a0;
  border: 2px solid rgba(255,255,255,0.2);
}

.btn-no:hover {
  background: rgba(255,255,255,0.05);
  color: white;
  border-color: rgba(255,255,255,0.4);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
