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
            <img :src="result.image" :alt="result.name" @error="handleImageError" />
          </div>

          <div class="result-info">
            <h4>{{ result.name }}</h4>
            <p class="result-stats-text">{{ result.stats }}</p>
            <p class="result-duration">{{ result.duration }}</p>
            <p class="result-quote">"{{ result.quote }}"</p>
          </div>
        </div>
      </div>

      <div class="results-cta">
        <p>¿Quieres ser el próximo?</p>
        <a href="#calendly" class="btn btn-primary">
          Empieza Tu Transformación →
        </a>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ResultsSection',
  data() {
    return {
      results: [
        {
          image: '/images/results/esteban.png',
          name: 'Esteban',
          stats: 'Antes 25% grasa, ahora 12% grasa',
          duration: '2 semanas',
          quote: 'Excelente, hasta he dejado de fumar. Estoy muy feliz por mis resultados, gracias a Petru por estar siempre pendiente.'
        },
        {
          image: '/images/results/sergio.png',
          name: 'Sergio',
          stats: '+2,5kg de músculo',
          duration: '10 semanas',
          quote: 'La dieta propuesta por Petru me ha sentado muy bien, y mediante los entrenamientos voy logrando progresos que no esperaba ver. Gracias al apoyo de Petru, es un gran entrenador, desearía haberle conocido antes.'
        },
        {
          image: '/images/results/oscar.png',
          name: 'Óscar',
          stats: 'Antes 25% de grasa, ahora 16% de grasa',
          duration: '12 semanas',
          quote: 'Estoy muy agradecido por haber dado este paso, disfruto entrenando y cada día que pasa me siento mejor.'
        },
        {
          image: '/images/results/pedro.png',
          name: 'Pedro',
          stats: 'Antes 22% de grasa, ahora 17% de grasa',
          duration: '14 semanas',
          quote: 'Agradecido de cambiar mis hábitos gracias a Petru, estoy mejorando constantemente y tratando de no salirme del camino. Su apoyo y motivación constantes han sido claves.'
        }
      ]
    }
  },
  methods: {
     handleImageError(e) {
      if (e.target.dataset.errorHandled) return;
      e.target.dataset.errorHandled = 'true';
      e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="250"%3E%3Crect width="200" height="250" fill="%231a1a1a"/%3E%3Ctext x="50%25" y="50%25" font-size="24" fill="%23e63946" text-anchor="middle" dominant-baseline="middle"%3EFOTO%3C/text%3E%3C/svg%3E';
    }
  }
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
  border-color: rgba(230, 57, 70, 0.3);
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

.result-quote {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-style: italic;
  margin: 0;
  line-height: 1.5;
}

.results-cta {
  text-align: center;
  margin-top: 4rem;
  padding: 3rem;
  background: linear-gradient(135deg, rgba(230, 57, 70, 0.1) 0%, rgba(230, 57, 70, 0.05) 100%);
  border-radius: 20px;
  border: 1px solid rgba(230, 57, 70, 0.2);
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
  box-shadow: 0 8px 30px rgba(230, 57, 70, 0.4);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(230, 57, 70, 0.5);
}

@media (max-width: 968px) {
  .results-grid {
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

  .results-cta {
    padding: 2rem 1.5rem;
  }

  .results-cta p {
    font-size: 1.25rem;
  }
}
</style>
