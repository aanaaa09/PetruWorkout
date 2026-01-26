<template>
  <section id="hero" class="hero-section">
    <div class="hero-bg">
      <div class="hero-overlay"></div>
    </div>

    <div class="hero-content">
      <div class="hero-text">
        <h1 class="hero-title">
          El sistema para entrenar en casa o en el parque y conseguir
          <span class="highlight">fuerza real</span>
        </h1>

        <ul class="benefits-list">
          <li>
            <span class="check">✅</span>
            Cuerpo atlético y definido
          </li>
          <li>
            <span class="check">✅</span>
            Gana fuerza y movilidad para el día a día
          </li>
          <li>
            <span class="check">✅</span>
            Estrategia secreta para activar tu metabolismo y quemar grasa
          </li>
          <li>
            <span class="check">✅</span>
            Motivación diaria para mantenerte constante y no abandonar
          </li>
        </ul>

        <button @click="showModal = true" class="btn-gift">
          🎁 Empieza hoy con ventaja y llévate un regalo exclusivo al unirte
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
    </div>

    <!-- Modal para email -->
    <transition name="modal-fade">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content">
          <button @click="closeModal" class="modal-close">✕</button>

          <h2 class="modal-title">🎁 Accede al regalo exclusivo</h2>
          <p class="modal-description">
            Únete al grupo privado y recibe tu regalo de bienvenida
          </p>

          <form @submit.prevent="handleSubmit" class="email-form">
            <div class="form-group">
              <input
                v-model="email"
                type="email"
                placeholder="tu@email.com"
                required
                class="email-input"
              />
            </div>

            <div class="checkbox-group">
              <input
                v-model="acceptPrivacy"
                type="checkbox"
                id="privacy"
                required
              />
              <label for="privacy">
                Acepto la
                <button
                  type="button"
                  @click="openPrivacy"
                  class="link-button"
                >
                  política de privacidad
                </button>
              </label>
            </div>

            <div v-if="error" class="error-message">{{ error }}</div>
            <div v-if="success" class="success-message">{{ success }}</div>

            <button
              type="submit"
              class="btn-submit"
              :disabled="loading"
            >
              {{ loading ? '⏳ Procesando...' : 'Accede al grupo y a mi regalo' }}
            </button>
          </form>
        </div>
      </div>
    </transition>

    <div class="scroll-indicator">
      <span>Descubre más</span>
      <div class="scroll-arrow">↓</div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HeroSection',
  data() {
    return {
      desktopImage: '/images/petru-hero-optimized.webp',
      showModal: false,
      email: '',
      acceptPrivacy: false,
      loading: false,
      error: '',
      success: ''
    }
  },
  methods: {
    handleImageError(e) {
      e.target.style.display = 'none'
    },

    closeModal() {
      this.showModal = false
      this.resetForm()
    },

    resetForm() {
      this.email = ''
      this.acceptPrivacy = false
      this.error = ''
      this.success = ''
      this.loading = false
    },

    openPrivacy() {
      this.$router.push('/info?legal=privacy')
      this.closeModal()
    },

    async handleSubmit() {
      this.error = ''
      this.success = ''

      if (!this.acceptPrivacy) {
        this.error = 'Debes aceptar la política de privacidad'
        return
      }

      this.loading = true

      try {
        // Aquí guardarías el email en tu backend
        const response = await fetch('https://petruworkout-production.up.railway.app/api/lead/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: this.email })
        })

        const data = await response.json()

        if (response.ok) {
          this.success = '¡Perfecto! Redirigiendo al grupo...'
          setTimeout(() => {
            window.location.href = 'https://petrucalistenia.com/team'
          }, 1500)
        } else {
          this.error = data.error || 'Error al registrar. Intenta de nuevo.'
        }
      } catch (err) {
        console.error('Error:', err)
        this.error = 'Error de conexión. Intenta de nuevo.'
      } finally {
        this.loading = false
      }
    }
  }
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
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  background: linear-gradient(135deg, rgba(13, 13, 13, 0.95) 0%, rgba(26, 26, 26, 0.90) 100%);
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(13, 13, 13, 0.95) 0%,
    rgba(26, 26, 26, 0.85) 50%,
    rgba(13, 13, 13, 0.9) 100%
  );
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
  margin-top: 0;
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* ===== TÍTULO ===== */
.hero-title {
  font-size: clamp(1.8rem, 4vw, 3rem);
  font-weight: 900;
  line-height: 1.2;
  color: white;
  margin: 0;
}

.hero-title .highlight {
  color: var(--color-accent);
}

/* ===== LISTA DE BENEFICIOS ===== */
.benefits-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
   gap: 0.5rem;
}

.benefits-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  line-height: 1.3;
}

.check {
  color: var(--color-accent);
  font-size: 1.3rem;
  flex-shrink: 0;
}

/* ===== BOTÓN REGALO ===== */
.btn-gift {
  background: var(--gradient-primary);
  color: white;
  padding: 1.2rem 2rem;
  border: none;
  border-radius: 12px;
  font-weight: 800;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
  text-align: center;
}

.btn-gift:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.6);
}

/* ===== MODAL ===== */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-content {
  background: rgba(26, 26, 26, 0.98);
  border: 1px solid rgba(6, 214, 160, 0.3);
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 500px;
  width: 100%;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

.modal-title {
  font-size: 1.75rem;
  color: white;
  margin: 0 0 0.5rem 0;
  text-align: center;
}

.modal-description {
  font-size: 1rem;
  color: var(--color-text-secondary);
  text-align: center;
  margin: 0 0 2rem 0;
}

/* ===== FORMULARIO ===== */
.email-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.email-input {
  padding: 1rem;
  border: 2px solid rgba(6, 214, 160, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.email-input::placeholder {
  color: var(--color-text-muted);
}

.email-input:focus {
  outline: none;
  border-color: var(--color-accent);
  background: rgba(255, 255, 255, 0.08);
}

.checkbox-group {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.checkbox-group input[type="checkbox"] {
  margin-top: 0.25rem;
  width: 18px;
  height: 18px;
  cursor: pointer;
  flex-shrink: 0;
}

.link-button {
  background: none;
  border: none;
  color: var(--color-accent);
  text-decoration: underline;
  cursor: pointer;
  font-size: inherit;
  padding: 0;
  font-family: inherit;
}

.link-button:hover {
  color: var(--color-accent-light);
}

.error-message {
  padding: 0.875rem;
  background: rgba(239, 35, 60, 0.2);
  border: 1px solid rgba(239, 35, 60, 0.4);
  border-radius: 10px;
  color: #ff6b6b;
  font-weight: 600;
  text-align: center;
}

.success-message {
  padding: 0.875rem;
  background: rgba(6, 214, 160, 0.2);
  border: 1px solid rgba(6, 214, 160, 0.4);
  border-radius: 10px;
  color: var(--color-accent);
  font-weight: 600;
  text-align: center;
}

.btn-submit {
  background: var(--gradient-primary);
  color: white;
  padding: 1rem 2rem;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.6);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ===== IMAGEN ===== */
.hero-image-desktop {
  position: relative;
  display: flex;
  justify-content: center;
}

.hero-image img {
  max-width: 100%;
  height: auto;
  border-radius: 20px;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
}

/* ===== INDICADOR DE SCROLL ===== */
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

.scroll-arrow {
  font-size: 1.5rem;
}

@keyframes bounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(10px); }
}

/* ===== RESPONSIVE TABLET ===== */
@media (max-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }

  .hero-text {
    align-items: center;
  }

  .benefits-list {
    align-items: flex-start;
    max-width: 600px;
  }

  .hero-image-desktop {
    order: -1;
  }
}

/* ===== RESPONSIVE MÓVIL ===== */
@media (max-width: 640px) {
  .hero-section {
    padding: 5rem 1rem 2rem;
  }

  .hero-title {
    font-size: 1.5rem;
  }

  .benefits-list li {
    font-size: 1rem;
  }

  .btn-gift {
    font-size: 1rem;
    padding: 1rem 1.5rem;
  }

  .modal-content {
    padding: 2rem 1.5rem;
  }

  .modal-title {
    font-size: 1.5rem;
  }

  .hero-image-desktop {
    display: none;
  }

  .scroll-indicator {
    display: none;
  }
}
</style>
