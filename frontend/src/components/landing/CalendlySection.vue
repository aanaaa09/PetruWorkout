<template>
  <section id="calendly" class="calendly-section">
    <div class="calendly-container">
      <div class="calendly-header">
        <span class="section-tag">AGENDA TU LLAMADA</span>
        <h2>📅 Llamada Gratuita de Valoración</h2>
        <p>
          Sin compromisos. Hablemos sobre tus objetivos y cómo puedo ayudarte a alcanzarlos.
        </p>
      </div>

      <div class="calendly-benefits">
        <div class="benefit">
          <span class="benefit-icon">⏱️</span>
          <span>15-20 minutos</span>
        </div>
        <div class="benefit">
          <span class="benefit-icon">💯</span>
          <span>100% Gratis</span>
        </div>
        <div class="benefit">
          <span class="benefit-icon">🎯</span>
          <span>Plan personalizado</span>
        </div>
      </div>

      <!-- ✅ NUEVO: Botón para activar Calendly -->
      <div v-if="!calendlyLoaded" class="calendly-placeholder">
        <button @click="loadCalendly" class="btn-load-calendly">
          📅 Cargar Calendario de Citas
        </button>
        <p class="calendly-note-small">
          Haz clic para ver las fechas disponibles
        </p>
      </div>

      <!-- ✅ Solo se carga cuando el usuario hace clic -->
      <div v-else class="calendly-widget">
        <div
          class="calendly-inline-widget"
          :data-url="calendlyUrl"
          style="min-width:320px;height:700px;"
        ></div>
      </div>

      <div class="calendly-note">
        <p>
          💡 <strong>¿Prefieres escribirme primero?</strong>
          <a href="#contacto">Envíame un mensaje</a> y te responderé lo antes posible.
        </p>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'CalendlySection',
  data() {
    return {
      calendlyUrl: 'https://calendly.com/petruworkout/reunion?hide_gdpr_banner=1',
      calendlyLoaded: false,
      scriptsLoaded: false
    }
  },
  methods: {
    loadCalendly() {
      this.calendlyLoaded = true

      if (!this.scriptsLoaded) {
        this.scriptsLoaded = true

        // Cargar script de Calendly
        if (!document.querySelector('script[src*="calendly"]')) {
          const script = document.createElement('script')
          script.src = 'https://assets.calendly.com/assets/external/widget.js'
          script.async = true
          document.head.appendChild(script)
        }

        // Cargar CSS de Calendly
        if (!document.querySelector('link[href*="calendly"]')) {
          const link = document.createElement('link')
          link.rel = 'stylesheet'
          link.href = 'https://assets.calendly.com/assets/external/widget.css'
          document.head.appendChild(link)
        }
      }
    }
  }
}
</script>

<style scoped>
.calendly-section {
  padding: 6rem 2rem;
  background: var(--bg-secondary);
}

.calendly-container {
  max-width: 1000px;
  margin: 0 auto;
}

.calendly-header {
  text-align: center;
  margin-bottom: 2rem;
}

.section-tag {
  font-size: 0.85rem;
  color: var(--color-accent);
  font-weight: 700;
  letter-spacing: 0.15em;
  display: block;
  margin-bottom: 1rem;
}

.calendly-header h2 {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  margin: 0 0 1rem 0;
}

.calendly-header p {
  font-size: 1.1rem;
  color: var(--color-text-muted);
  max-width: 600px;
  margin: 0 auto;
}

.calendly-benefits {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.benefit {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50px;
  color: var(--color-text-secondary);
  font-size: 0.95rem;
}

.benefit-icon {
  font-size: 1.2rem;
}

/* ✅ NUEVO: Estilos del placeholder */
.calendly-placeholder {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  border: 2px dashed rgba(6, 214, 160, 0.3);
}

.btn-load-calendly {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1.25rem 2.5rem;
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
}

.btn-load-calendly:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.5);
}

.calendly-note-small {
  margin-top: 1rem;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.calendly-widget {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.calendly-note {
  text-align: center;
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
}

.calendly-note p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 1rem;
}

.calendly-note a {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
}

.calendly-note a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .calendly-section {
    padding: 4rem 1rem;
  }

  .calendly-header h2 {
    font-size: 2rem;
  }

  .calendly-benefits {
    gap: 1rem;
  }

  .benefit {
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
  }

  .calendly-inline-widget {
    height: 600px !important;
  }

  .btn-load-calendly {
    width: 100%;
    justify-content: center;
  }

  .calendly-placeholder {
    padding: 3rem 1.5rem;
  }
}
</style>
