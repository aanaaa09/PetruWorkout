<template>
  <section id="calendly" class="calendly-section">
    <div class="calendly-container">
      <div class="calendly-header">
        <h2>📅 Agenda tu Llamada Gratuita</h2>
        <p>Hablemos sobre tus objetivos y cómo puedo ayudarte a alcanzarlos</p>
      </div>

      <!-- Widget de Calendly -->
      <div class="calendly-widget">
        <div
          class="calendly-inline-widget"
          :data-url="calendlyUrl"
          style="min-width:320px;height:700px;"
        ></div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'CalendlySection',
  data() {
    return {
      calendlyUrl: 'https://calendly.com/petruworkout/reunion?hide_gdpr_banner=1'
    }
  },
  mounted() {
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
</script>

<style scoped>
.calendly-section {
  padding: 6rem 2rem;
  background: rgba(0, 0, 0, 0.2);
}

.calendly-container {
  max-width: 1000px;
  margin: 0 auto;
}

.calendly-header {
  text-align: center;
  margin-bottom: 3rem;
}

.calendly-header h2 {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  margin-bottom: 1rem;
}

.calendly-header p {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  max-width: 600px;
  margin: 0 auto;
}

.calendly-widget {
  background: white;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .calendly-section {
    padding: 4rem 1rem;
  }

  .calendly-header h2 {
    font-size: 2rem;
  }

  .calendly-inline-widget {
    height: 600px !important;
  }
}
</style>
