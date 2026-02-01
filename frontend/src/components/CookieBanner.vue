<template>
  <transition name="slide-up">
    <div v-if="visible" class="cookie-banner">
      <div class="cookie-container">
        <div class="cookie-content">
          <!-- Icono y texto -->
          <div class="cookie-text">
            <span class="cookie-icon">🍪</span>
            <div class="cookie-message">
              <p class="cookie-title">Utilizamos cookies</p>

              <p class="cookie-description cookie-description-desktop">
                Usamos cookies de análisis para mejorar tu experiencia y medir la efectividad de nuestras campañas.
                <strong>Al continuar navegando, aceptas su uso.</strong>
              </p>

              <p class="cookie-description cookie-description-mobile">
                Usamos cookies para mejorar tu experiencia.
                <strong>Al continuar, aceptas su uso.</strong>
              </p>
            </div>
          </div>

          <!-- Botones -->
          <div class="cookie-actions">
            <button @click="goToCookiesSection" class="btn-more-info">
              Más info
            </button>

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
    let cookiesAccepted = false

    try {
      // Intentar leer de localStorage
      cookiesAccepted = localStorage.getItem('cookies_accepted') === 'true'
      console.log('Estado de cookies (localStorage):', cookiesAccepted)
    } catch (error) {
      console.warn('No se puede acceder a localStorage:', error)
      // Fallback a sessionStorage
      try {
        cookiesAccepted = sessionStorage.getItem('cookies_accepted') === 'true'
        console.log('Estado de cookies (sessionStorage):', cookiesAccepted)
      } catch (e) {
        console.error('No se puede acceder a ningún storage:', e)
      }
    }

    if (!cookiesAccepted) {
      // Mostrar después de 2 segundos
      setTimeout(() => {
        this.visible = true
        console.log('Banner de cookies mostrado')
      }, 2000)
    } else {
      console.log('Cookies ya aceptadas, no se muestra el banner')
    }
  },
  methods: {
    acceptCookies() {
      try {
        // Guardar en localStorage que ya aceptó
        localStorage.setItem('cookies_accepted', 'true')
        console.log('Cookies aceptadas y guardadas en localStorage')
        this.visible = false
      } catch (error) {
        console.error('Error al guardar en localStorage:', error)
        // Si falla localStorage, intentar con sessionStorage como fallback
        try {
          sessionStorage.setItem('cookies_accepted', 'true')
          console.log('Guardado en sessionStorage como fallback')
          this.visible = false
        } catch (e) {
          console.error('Error crítico al guardar preferencia de cookies:', e)
        }
      }
    },

    goToCookiesSection() {
      try {
        // Marcar que viene desde el banner de cookies
        sessionStorage.setItem('from_cookie_banner', 'true')

        // Navegar a la política de privacidad con el hash de cookies
        this.$router.push('/info?legal=privacy#cookies')
      } catch (error) {
        console.error('Error al navegar:', error)
        // Fallback: navegar sin sessionStorage
        this.$router.push('/info?legal=privacy#cookies')
      }
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

/* ✅ Por defecto mostrar versión desktop */
.cookie-description-mobile {
  display: none;
}

.cookie-description-desktop {
  display: block;
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
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.3s ease;
  white-space: nowrap;
  text-decoration: underline;
}

.btn-more-info:hover {
  color: #ff4d5a;
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

/* ✅ MODIFICADO: Versión móvil más compacta */
@media (max-width: 639px) {
  .cookie-banner {
    bottom: 0;
    padding-bottom: env(safe-area-inset-bottom, 0);
  }

  .cookie-container {
    padding-bottom: 0.5rem;
  }

  .cookie-content {
    padding: 0.6rem 0.9rem; /* ✅ Reducido más el padding */
    gap: 0.7rem; /* ✅ Menos espacio entre elementos */
  }

  .cookie-text {
    gap: 0.7rem; /* ✅ Menos espacio entre icono y texto */
  }

  .cookie-icon {
    font-size: 1.3rem; /* ✅ Icono más pequeño */
    margin-top: 0;
  }

  .cookie-message {
    font-size: 0.75rem; /* ✅ Texto más pequeño */
    line-height: 1.4; /* ✅ Altura de línea ajustada */
  }

  .cookie-title {
    margin: 0 0 0.3rem 0; /* ✅ Menos margen */
    font-size: 0.8rem; /* ✅ Título más pequeño */
  }

  /* ✅ Ocultar versión desktop y mostrar móvil */
  .cookie-description-desktop {
    display: none;
  }

  .cookie-description-mobile {
    display: block;
  }

  .cookie-actions {
    gap: 0.7rem; /* ✅ Menos espacio entre botones */
  }

  .btn-more-info {
    font-size: 0.75rem; /* ✅ Botón más pequeño */
  }

  .btn-accept {
    width: 100%;
    justify-content: center;
    padding: 0.55rem 1rem; /* ✅ Padding reducido */
    font-size: 0.8rem; /* ✅ Texto más pequeño */
  }

  .btn-icon {
    font-size: 0.9rem;
  }
}
</style>
