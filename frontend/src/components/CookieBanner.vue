<template>
  <transition name="slide-up">
    <div v-if="visible" class="cookie-banner">
      <div class="cookie-container">
        <div class="cookie-content">
          <!-- Icono y texto -->
          <div class="cookie-text">
            <span class="cookie-icon">🍪</span>
            <div class="cookie-message">
              <p class="cookie-title">Utilizamos cookies propias y de terceros</p>
              <p class="cookie-description">
                Usamos cookies de análisis (Google Analytics) para mejorar tu experiencia y medir la efectividad de nuestras campañas.
                <strong>Al continuar navegando, aceptas su uso.</strong>
              </p>
            </div>
          </div>

          <!-- Botones -->
          <div class="cookie-actions">
            <router-link to="/privacidad" class="btn-more-info">
              Más información
            </router-link>

            <button @click="acceptCookies" class="btn-accept">
              Aceptar
              <span class="btn-icon">✓</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'CookieBanner',
  data() {
    return {
      visible: false
    }
  },
  mounted() {
    // Verificar si ya aceptó las cookies
    const cookiesAccepted = localStorage.getItem('cookies_accepted')

    if (!cookiesAccepted) {
      // Mostrar después de 2 segundos
      setTimeout(() => {
        this.visible = true
      }, 2000)
    }
  },
  methods: {
    acceptCookies() {
      // Guardar en localStorage que ya aceptó
      localStorage.setItem('cookies_accepted', 'true')
      this.visible = false
    }
  }
}
</script>

<style scoped>
.cookie-banner {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 9999;
}

.cookie-container {
  background: linear-gradient(135deg, rgba(17, 17, 17, 0.98) 0%, rgba(0, 0, 0, 0.98) 100%);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(230, 57, 70, 0.2);
  box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.5);
}

.cookie-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: flex-start;
}

.cookie-text {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  flex: 1;
}

.cookie-icon {
  font-size: 2rem;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.cookie-message {
  font-size: 0.875rem;
  line-height: 1.6;
}

.cookie-title {
  color: white;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.cookie-description {
  color: #d1d5db;
  margin: 0;
}

.cookie-description strong {
  color: white;
  font-weight: 600;
}

.cookie-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.btn-more-info {
  font-size: 0.875rem;
  color: #e63946;
  text-decoration: none;
  transition: color 0.3s ease;
  white-space: nowrap;
}

.btn-more-info:hover {
  color: #ff4d5a;
  text-decoration: underline;
}

.btn-accept {
  background: linear-gradient(135deg, #e63946 0%, #d62828 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(230, 57, 70, 0.3);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  margin-left: auto;
}

.btn-accept:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(230, 57, 70, 0.5);
  background: linear-gradient(135deg, #ff4d5a 0%, #e63946 100%);
}

.btn-icon {
  font-size: 1rem;
  font-weight: bold;
}

/* Animación de entrada */
.slide-up-enter-active {
  animation: slideUp 0.5s ease-out;
}

.slide-up-leave-active {
  animation: slideDown 0.3s ease-in;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes slideDown {
  from {
    transform: translateY(0);
    opacity: 1;
  }
  to {
    transform: translateY(100%);
    opacity: 0;
  }
}

/* Responsive */
@media (min-width: 640px) {
  .cookie-content {
    flex-direction: row;
    align-items: center;
    padding: 1.25rem 2rem;
  }

  .cookie-actions {
    width: auto;
    margin-left: auto;
  }

  .btn-accept {
    margin-left: 0;
  }
}

@media (max-width: 639px) {
  .cookie-icon {
    font-size: 1.5rem;
  }

  .cookie-message {
    font-size: 0.8125rem;
  }

  .btn-accept {
    width: 100%;
    justify-content: center;
  }
}
</style>
