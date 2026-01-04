<template>
  <section id="resultados" class="results-section">
    <div class="results-container">
      <div class="section-header">
        <span class="section-tag">RESULTADOS REALES</span>
        <h2 class="section-title">Transformaciones de mis clientes</h2>
      </div>

      <div class="results-grid">
        <div
          v-for="(result, index) in results"
          :key="index"
          class="result-card"
        >
          <div class="result-images">
            <img
              :srcset="`
                ${result.imagePath}-small.webp 330w,
                ${result.imagePath}-medium.webp 660w,
                ${result.imagePath}-large.webp 1000w
              `"
              sizes="(max-width: 640px) 330px, (max-width: 968px) 660px, 500px"
              :src="result.image"
              :alt="result.name"
              :width="result.width"
              :height="result.height"
              loading="lazy"
              @error="handleImageError"
            />
          </div>

          <div class="result-info">
            <h4>{{ result.name }}</h4>
            <p class="result-stats-text">{{ result.stats }}</p>
            <p class="result-duration">{{ result.duration }}</p>

            <!-- Mensaje estilo WhatsApp -->
            <div class="whatsapp-message">
              <div class="whatsapp-bubble">
                <p class="whatsapp-text">{{ result.quote }}</p>
                <span class="whatsapp-time">{{ result.time }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!--CTA WhatsApp -->
      <div class="whatsapp-cta">
        <p class="cta-text">¿Te gustaría conseguir resultados como estos?</p>
        <a
          href="https://wa.link/svhddh"
          target="_blank"
          rel="noopener noreferrer"
          class="btn-whatsapp-cta"
          @click="handleWhatsAppClick"
        >
          💬 Contactar con Petru
        </a>
      </div>

      <!--SECCIÓN DE VIDEOS -->
      <div class="videos-section">
        <div class="videos-header">
          <h3>Esto es lo que opinan mis clientes</h3>
          <p>Testimonios reales de personas que han logrado sus objetivos</p>
        </div>

        <div class="videos-grid">
          <div
            v-for="video in videoTestimonials"
            :key="video.id"
            class="video-wrapper"
          >
            <video
              :src="video.src"
              :poster="video.posterSmall"
              controls
              playsinline
              preload="none"
              width="377"
              height="640"
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
import { trackCalendlyClick, trackWhatsAppClick } from '@/utils/tracking.js'

export default {
  name: 'ResultsSection',
  data() {
    return {
      results: [
        {
          image: '/images/results/esteban.webp',
          imagePath: '/images/results/esteban',
          width: 534,
          height: 501,
          name: 'Esteban, 37 años',
          stats: 'Antes 25% grasa, ahora 12% grasa',
          duration: '12 semanas',
          quote: 'Excelente, de hecho ya hasta dejé el tabaco. Fumaba 3-5 cigarros al día y esta semana ya no fumé en lo absoluto. Estoy haciendo un gran cambio en mi persona y se empieza a notar. Estoy feliz por mis resultados y con mayor ánimo de poder seguir dando el máximo. Muchas gracias por estar al pendiente.',
          time: '17:12'
        },
        {
          image: '/images/results/sergio.webp',
          imagePath: '/images/results/sergio',
          width: 534,
          height: 545,
          name: 'Sergio, 34 años',
          stats: '+2,5kg de músculo',
          duration: '10 semanas',
          quote: 'Muchas gracias tío, la verdad que la dieta me está sentando muy bien y los entrenamientos mejor. Aún poco a poco voy logrando progresos que no esperaba ver. Sobre todo el apoyo que ofreces y das para todo. Para problemas con la dieta, problemas personales o de ejercicio, eres un gran entrenador y ojalá haberte conocido antes.',
          time: '6 min'
        },
        {
          image: '/images/results/oscar.webp',
          imagePath: '/images/results/oscar',
          width: 534,
          height: 517,
          name: 'Óscar, 28 años',
          stats: 'Antes 25% de grasa, ahora 16% de grasa',
          duration: '12 semanas',
          quote: 'Hola buenos días, además de que es un momento divertido y que me gusta, me lo paso bien y cada día que pasa me siento mejor. Cada pequeño avance como poder una repetición más o no estar tan cansado se nota y disfruto. Y esto es solo el comienzo, verás dentro de unos meses. Me alegro mucho y la verdad que estoy agradecido por dar ese paso.',
          time: '9:16'
        },
        {
          image: '/images/results/pedro.webp',
          imagePath: '/images/results/pedro',
          width: 534,
          height: 523,
          name: 'Pedro, 63 años',
          stats: 'Antes 22% de grasa, ahora 17% de grasa',
          duration: '14 semanas',
          quote: 'Con mis entrenamientos estamos de maravilla, vamos mejorando más y más día con día. Mi plan de nutrición me gusta y he notado que ya hay menos grasa. Estoy mejorando tratando de no salirme del camino y con tu apoyo que recibo constantemente me he sentido súper contento y con motivación para poder seguir. Como te he dicho, de ahora en adelante esto es un muy buen hábito para mí. ¡No hay marcha atrás!',
          time: '16:04'
        }
      ],
      videoTestimonials: [
        {
          id: 1,
          src: '/videos/video1.mp4',
          poster: '/videos/thumbs/thumb1.webp',
          posterSmall: '/videos/thumbs/thumb1-small.webp'
        },
        {
          id: 2,
          src: '/videos/video2.mp4',
          poster: '/videos/thumbs/thumb2.webp',
          posterSmall: '/videos/thumbs/thumb2-small.webp'
        },
        {
          id: 3,
          src: '/videos/video3.mp4',
          poster: '/videos/thumbs/thumb3.webp',
          posterSmall: '/videos/thumbs/thumb3-small.webp'
        }
      ]
    }
  },
  methods: {
    handleImageError(e) {
      if (e.target.dataset.errorHandled) return;
      e.target.dataset.errorHandled = 'true';
      e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="250"%3E%3Crect width="200" height="250" fill="%231a1a1a"/%3E%3Ctext x="50%25" y="50%25" font-size="24" fill="%23e63946" text-anchor="middle" dominant-baseline="middle"%3EFOTO%3C/text%3E%3C/svg%3E';
    },
    handleCalendlyClick() {
      trackCalendlyClick('results-cta-button', 'results-section')
    },
    handleWhatsAppClick() {
      trackWhatsAppClick('results-whatsapp-cta-button', 'results-section')
    }
  }
}
</script>

<style scoped>
/* Mantén todos tus estilos actuales exactamente igual */
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

.result-info {
  padding: 1.5rem;
}

.result-info h4 {
  font-size: 1.5rem;
  color: white;
  margin: 0 0 0.5rem 0;
  font-weight: 700;
}

.result-stats-text {
  font-size: 1rem;
  color: var(--color-accent);
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.result-duration {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin: 0 0 1rem 0;
  font-weight: 500;
}

.whatsapp-message {
  margin-top: 1rem;
}

.whatsapp-bubble {
  background: #075E54;
  background: linear-gradient(135deg, #128C7E 0%, #075E54 100%);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  position: relative;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.whatsapp-bubble::before {
  content: '';
  position: absolute;
  top: 0;
  left: -8px;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 8px 8px 0;
  border-color: transparent #075E54 transparent transparent;
}

.whatsapp-text {
  color: #ffffff;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0 0 0.5rem 0;
  word-wrap: break-word;
}

.whatsapp-time {
  display: block;
  text-align: right;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.25rem;
}

/* ===== CTA WHATSAPP ===== */
.whatsapp-cta {
  text-align: center;
  margin: 3rem 0;
  padding: 2.5rem;
  background: linear-gradient(135deg, rgba(37, 211, 102, 0.1) 0%, rgba(18, 140, 126, 0.05) 100%);
  border-radius: 20px;
  border: 2px solid rgba(37, 211, 102, 0.3);
}

.whatsapp-cta .cta-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 1.5rem 0;
}

.btn-whatsapp-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1.25rem 2.5rem;
  background: linear-gradient(135deg, #25D366, #128C7E);
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(37, 211, 102, 0.4);
}

.btn-whatsapp-cta:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(37, 211, 102, 0.6);
}

.videos-section {
  margin-top: 5rem;
  padding-top: 4rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.videos-header {
  text-align: center;
  margin-bottom: 3rem;
}

.videos-header h3 {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0 0 1rem 0;
}

.videos-header p {
  font-size: 1.1rem;
  color: var(--color-text-muted);
  margin: 0;
}

.videos-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.video-wrapper {
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
}

.video-wrapper:hover {
  transform: translateY(-5px);
  border-color: rgba(6, 214, 160, 0.3);
}

.video-wrapper video {
  width: 100%;
  height: auto;
  display: block;
}

.results-cta {
  text-align: center;
  margin-top: 4rem;
  padding: 3rem;
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.1) 0%, rgba(6, 214, 160, 0.05) 100%);
  border-radius: 20px;
  border: 1px solid rgba(6, 214, 160, 0.2);
}

.results-cta p {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 1.5rem 0;
}

.btn-primary {
  display: inline-block;
  background: var(--gradient-primary);
  color: white;
  padding: 1rem 2.5rem;
  border-radius: 10px;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.5);
}

@media (max-width: 968px) {
  .results-grid {
    grid-template-columns: 1fr;
    max-width: 500px;
    margin: 0 auto;
  }

  .videos-grid {
    grid-template-columns: 1fr;
    max-width: 500px;
    margin: 0 auto;
  }
}

@media (max-width: 640px) {
  .results-section {
    padding: 4rem 1rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .result-info h4 {
    font-size: 1.3rem;
  }

  .whatsapp-text {
    font-size: 0.85rem;
  }

  .videos-header h3 {
    font-size: 1.5rem;
  }

  .results-cta {
    padding: 2rem 1.5rem;
  }

  .results-cta p {
    font-size: 1.25rem;
  }

  .whatsapp-cta {
    padding: 2rem 1.5rem;
    margin: 2rem 0;
  }

  .whatsapp-cta .cta-text {
    font-size: 1.25rem;
  }

  .btn-whatsapp-cta {
    width: 100%;
    justify-content: center;
    padding: 1rem 1.5rem;
    font-size: 1rem;
  }
}
</style>
