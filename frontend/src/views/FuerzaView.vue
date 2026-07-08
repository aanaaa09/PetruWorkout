<template>
  <div class="fuerza-page">
    <SimpleNavbar />
    <div class="content-wrapper">
      
      <div class="success-header">
        <h1>¡Diagnóstico recibido con éxito!&nbsp;👌</h1>
        <p class="subtitle">
          Revisaré tus respuestas personalmente en las próximas horas para ver qué está fallando en tu entrenamiento y explicarte cuál sería el paso a paso
        </p>
      </div>

      <div class="video-section">
        <p class="video-intro">Mientras tanto, mira lo que han conseguido otros alumnos en solo 3 meses:</p>
        
        <div class="video-wrapper">
          <iframe 
            width="100%" 
            height="100%" 
            src="https://www.youtube.com/embed/J0Smcj8H0A8?rel=0&modestbranding=1" 
            title="Resultados Reales - Petru Workout" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
          </iframe>
        </div>
      </div>

      <div class="cta-section">
        <h3 class="cta-title">¿Quieres acelerar el proceso?</h3>
        <p class="cta-desc">
          Si vas totalmente en serio y quieres que hablemos mañana mismo para valorar tu caso y te comente mi servicio, reserva una sesión de 10 minutos en el calendario:
        </p>
        
        <a href="https://calendly.com/petruworkout/reunion" target="_blank" rel="noopener noreferrer" class="btn-calendly">
          🗓️ Reservar mi valoración
        </a>
      </div>

      <div class="back-link-wrapper">
        <a href="/#resultados" class="btn-back-home">
          ← Quiero ver más casos de éxito en la página principal
        </a>
      </div>

    </div>
  </div>
</template>

<script>
import SimpleNavbar from '@/components/navigation/SimpleNavbar.vue'

export default {
  name: 'FuerzaView',
  components: {
    SimpleNavbar
  }
}
</script>

<style scoped>
.fuerza-page {
  min-height: 100vh;
  background: var(--bg-primary, #0d0d0d);
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  flex: 1;
  max-width: 1100px;
  margin: 0 auto;
  padding: 6rem 1rem 4rem; /* Reduced side padding to give more room */
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
}

.success-header {
  text-align: center;
  margin-bottom: 3rem;
}

.success-header h1 {
  font-size: clamp(1.8rem, 4.5vw, 3rem);
  font-weight: 900;
  color: var(--color-accent, #06d6a0);
  margin-bottom: 1.5rem;
  line-height: 1.2;
  white-space: nowrap; /* Force one line on desktop */
}

.subtitle {
  font-size: 1.15rem;
  color: var(--color-text-secondary, #e0e0e0);
  line-height: 1.6;
  max-width: 700px;
  margin: 0 auto;
}

.video-section {
  width: 100%;
  margin-bottom: 4rem;
  text-align: center;
}

.video-intro {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: white;
}

.video-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  border: 1px solid rgba(255,255,255,0.1);
  background: #000;
}

.video-wrapper iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.cta-section {
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.1) 0%, rgba(6, 214, 160, 0.05) 100%);
  border: 2px solid rgba(6, 214, 160, 0.3);
  border-radius: 20px;
  padding: 3rem 2rem;
  text-align: center;
  width: 100%;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.cta-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: white;
  margin-bottom: 1rem;
}

.cta-desc {
  font-size: 1.1rem;
  color: var(--color-text-secondary, #e0e0e0);
  line-height: 1.6;
  margin-bottom: 2rem;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

.btn-calendly {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary, linear-gradient(135deg, #06d6a0, #04ad80));
  color: white;
  text-decoration: none;
  font-weight: 800;
  font-size: 1.15rem;
  padding: 1.25rem 2.5rem;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
  margin-bottom: 2rem;
  width: 100%;
  max-width: 450px;
}

.btn-calendly:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.6);
}

.cta-note {
  font-size: 0.95rem;
  color: rgba(255,255,255,0.5);
  line-height: 1.5;
  max-width: 600px;
  margin: 0 auto;
}

.back-link-wrapper {
  margin-top: 3rem;
  text-align: center;
}

.btn-back-home {
  display: inline-flex;
  align-items: center;
  color: var(--color-text-secondary, #e0e0e0);
  text-decoration: none;
  font-size: 1.05rem;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.btn-back-home:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 5.5rem 1rem 3rem;
  }
  
  .success-header {
    margin-bottom: 2.5rem;
  }
  
  .success-header h1 {
    white-space: normal; /* Allow wrapping on mobile */
    font-size: 1.8rem;
  }
  
  .cta-section {
    padding: 2rem 1.5rem;
  }
  
  .cta-title {
    font-size: 1.4rem;
  }
  
  .btn-calendly {
    font-size: 1.05rem;
    padding: 1.1rem 1.5rem;
  }
}
</style>
