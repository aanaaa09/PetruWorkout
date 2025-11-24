<template>
  <section id="resultados" class="results-section">
    <div class="results-container">
      <div class="section-header">
        <span class="section-tag">RESULTADOS REALES</span>
        <h2 class="section-title">Transformaciones de mis clientes</h2>
        <p class="section-subtitle">
          Resultados verificados de personas que siguieron mi método
        </p>
      </div>

      <div class="results-grid">
        <div
          v-for="(result, index) in results"
          :key="index"
          class="result-card"
        >
          <div class="result-images">
            <div class="before-after">
              <div class="image-container before">
                <img :src="result.before" :alt="'Antes - ' + result.name" @error="handleImageError" />
                <span class="label">ANTES</span>
              </div>
              <div class="arrow">→</div>
              <div class="image-container after">
                <img :src="result.after" :alt="'Después - ' + result.name" @error="handleImageError" />
                <span class="label">DESPUÉS</span>
              </div>
            </div>
          </div>

          <div class="result-info">
            <h4>{{ result.name }}</h4>
            <div class="result-stats">
              <div class="stat">
                <span class="stat-value">{{ result.weightLost }}</span>
                <span class="stat-label">Kg perdidos</span>
              </div>
              <div class="stat">
                <span class="stat-value">{{ result.muscleGained }}</span>
                <span class="stat-label">Kg músculo</span>
              </div>
              <div class="stat">
                <span class="stat-value">{{ result.duration }}</span>
                <span class="stat-label">Semanas</span>
              </div>
            </div>
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
          before: '/images/results/npc1antes.png',
          after: '/images/results/npc1despues.png',
          weightLost: '-6',
          muscleGained: '+4',
          duration: '9',
          quote: 'Nunca pensé que podría conseguir esto con calistenia'
        },
        {
          before: '/images/results/npc2antes.png',
          after: '/images/results/npc2despues.png',
          weightLost: '-1',
          muscleGained: '+5',
          duration: '10',
          quote: 'El seguimiento de Petru fue clave para mis resultados'
        },
        {
          name: 'Jorge L.',
          before: '/images/results/jorge-before.jpg',
          after: '/images/results/jorge-after.jpg',
          weightLost: '-15',
          muscleGained: '+5',
          duration: '16',
          quote: 'Mi vida cambió completamente'
        }
      ]
    }
  },
  methods: {
     handleImageError(e) {
      // Evitar loops infinitos de error
      if (e.target.dataset.errorHandled) return;
      e.target.dataset.errorHandled = 'true';

      // Usar data URI en lugar de placeholder externo
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

.section-subtitle {
  font-size: 1.1rem;
  color: var(--color-text-muted);
  margin: 0;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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

.before-after {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.image-container {
  position: relative;
  flex: 1;
}

.image-container img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 10px;
}

.image-container .label {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
}

.image-container.after .label {
  background: var(--color-accent);
}

.arrow {
  color: var(--color-accent);
  font-size: 1.5rem;
  font-weight: 700;
  flex-shrink: 0;
}

.result-info {
  padding: 1.5rem;
}

.result-info h4 {
  display:none;
}

.result-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat {
  flex: 1;
  text-align: center;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--color-accent);
}

.stat-label {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
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
    max-width: 450px;
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

  .image-container img {
    height: 150px;
  }

  .results-cta {
    padding: 2rem 1.5rem;
  }

  .results-cta p {
    font-size: 1.25rem;
  }
}
</style>
