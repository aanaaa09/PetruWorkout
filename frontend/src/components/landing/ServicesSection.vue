<template>
  <section id="servicios" class="services-section">
    <div class="services-container">
      <div class="section-header">
        <span class="section-tag">CÓMO TRABAJO</span>
        <h2 class="section-title">Entrena donde estés, cuando quieras</h2>
        <p class="section-subtitle">
          Entrenamiento personalizado 100% online adaptado a tu ritmo de vida
        </p>
      </div>

      <div class="services-grid">
        <div class="service-card">
          <div class="card-header">
            <span class="card-icon">🌍</span>
            <h3>Clases Online</h3>
            <p class="card-subtitle">España & Internacional</p>
          </div>

          <ul class="features-list">
            <li><span class="check">✓</span> Entrena desde cualquier lugar del mundo</li>
            <li><span class="check">✓</span> Sin necesidad de gimnasio ni equipamiento</li>
            <li><span class="check">✓</span> Todo desde la comodidad de tu casa</li>
            <li><span class="check">✓</span> Horarios flexibles adaptados a ti</li>
            <li><span class="check">✓</span> Seguimiento personalizado 24/7</li>
            <li><span class="check">✓</span> Videollamadas de control y motivación</li>
          </ul>

          <div class="card-highlight">
            <p>🎯 <strong>Perfecto para ti</strong> si viajas, trabajas desde casa o vives fuera de España</p>
          </div>
        </div>

        <div class="service-card featured">
          <div class="card-header">
            <span class="card-icon">🤝</span>
            <h3>Clases Presenciales</h3>
            <p class="card-subtitle">Toledo & Madrid</p>
          </div>

          <ul class="features-list">
            <li><span class="check">✓</span> Sesiones 1 a 1 en persona</li>
            <li><span class="check">✓</span> Corrección de técnica en tiempo real</li>
            <li><span class="check">✓</span> Entrenamientos en parques y espacios abiertos</li>
            <li><span class="check">✓</span> Posibilidad de entrenar en grupo</li>
            <li><span class="check">✓</span> Quedadas y eventos especiales</li>
            <li><span class="check">✓</span> Motivación extra con presencia física</li>
          </ul>

          <div class="card-highlight">
            <p>🔥 <strong>Experiencia premium</strong> para residentes en Toledo y Madrid</p>
          </div>
        </div>

        <div class="service-card">
          <div class="card-header">
            <span class="card-icon">🎯</span>
            <h3>Plan Híbrido</h3>
            <p class="card-subtitle">Lo Mejor de Ambos</p>
          </div>

          <ul class="features-list">
            <li><span class="check">✓</span> Combina online y presencial</li>
            <li><span class="check">✓</span> Máxima flexibilidad de horarios</li>
            <li><span class="check">✓</span> Sesiones presenciales cuando quieras</li>
            <li><span class="check">✓</span> Seguimiento online continuo</li>
            <li><span class="check">✓</span> Ideal para agendas cambiantes</li>
            <li><span class="check">✓</span> Aprovecha cada oportunidad de entrenar</li>
          </ul>

          <div class="card-highlight">
            <p>💪 <strong>La opción definitiva</strong> para no perderte ni un solo día</p>
          </div>
        </div>
      </div>

      <div class="benefits-banner">
        <div class="benefit-item">
          <span class="benefit-icon">🏠</span>
          <div>
            <strong>Sin Material Extra</strong>
            <p>Solo necesitas tu cuerpo y ganas de transformarte</p>
          </div>
        </div>
        <div class="benefit-item">
          <span class="benefit-icon">⏰</span>
          <div>
            <strong>Horarios Flexibles</strong>
            <p>Entrena cuando mejor te venga, sin ataduras</p>
          </div>
        </div>
        <div class="benefit-item">
          <span class="benefit-icon">📍</span>
          <div>
            <strong>Dónde Tú Quieras</strong>
            <p>Casa, parque, hotel... donde te encuentres</p>
          </div>
        </div>
      </div>

      <div class="services-cta">
        <h3>¿Listo para empezar tu transformación?</h3>
        <p>Agenda una llamada gratuita de 20 minutos y te cuento cómo puedo ayudarte</p>
        <a
          href="https://calendly.com/petruworkout/reunion"
          target="_blank"
          rel="noopener noreferrer"
          class="btn btn-primary"
          @click="handleCalendlyClick"
        >
          📅 Agendar Llamada Gratuita
        </a>
      </div>
    </div>
  </section>
</template>

<script>

export default {
  name: 'ServicesSection',
  methods: {
    handleCalendlyClick() {
      trackCalendlyClick('services-cta-button', 'services-section')
    }
  }
}
</script>

<style scoped>
.services-section {
  padding: 6rem 2rem;
  background: var(--bg-primary);
}

.services-container {
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

.services-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  align-items: stretch;
  margin-bottom: 4rem;
}

.service-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  position: relative;
}

.service-card:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-5px);
  border-color: rgba(6, 214, 160, 0.3);
}

.service-card.featured {
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.1) 0%, rgba(6, 214, 160, 0.05) 100%);
  border-color: var(--color-accent);
  transform: scale(1.05);
}

.service-card.featured:hover {
  transform: scale(1.05) translateY(-5px);
}

.featured-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--gradient-primary);
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.5rem 1rem;
  border-radius: 50px;
  white-space: nowrap;
}

.card-header {
  text-align: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.card-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.card-header h3 {
  font-size: 1.5rem;
  color: white;
  margin: 0 0 0.5rem 0;
}

.card-subtitle {
  font-size: 0.9rem;
  color: var(--color-accent);
  font-weight: 600;
  margin: 0;
}

.features-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem 0;
  flex: 1;
}

.features-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.6rem 0;
  color: var(--color-text-secondary);
  font-size: 0.95rem;
  line-height: 1.5;
}

.check {
  color: var(--color-accent);
  font-weight: 700;
  flex-shrink: 0;
  font-size: 1.1rem;
}

.card-highlight {
  background: rgba(6, 214, 160, 0.1);
  border-left: 3px solid var(--color-accent);
  padding: 1rem;
  border-radius: 8px;
  margin-top: auto;
}

.card-highlight p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
}

.benefits-banner {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  margin-bottom: 4rem;
  padding: 2.5rem;
  background: rgba(6, 214, 160, 0.05);
  border-radius: 20px;
  border: 1px solid rgba(6, 214, 160, 0.2);
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.benefit-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.benefit-item strong {
  display: block;
  color: white;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.benefit-item p {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  line-height: 1.4;
}

.services-cta {
  text-align: center;
  padding: 3rem 2rem;
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.1) 0%, rgba(6, 214, 160, 0.05) 100%);
  border-radius: 20px;
  border: 2px solid var(--color-accent);
}

.services-cta h3 {
  font-size: 1.8rem;
  color: white;
  margin: 0 0 1rem 0;
}

.services-cta p {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  margin: 0 0 2rem 0;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1.25rem 2.5rem;
  background: var(--gradient-primary);
  color: white;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.5);
}

@media (max-width: 968px) {
  .services-grid {
    grid-template-columns: 1fr;
    max-width: 500px;
    margin: 0 auto 4rem;
  }

  .service-card.featured {
    transform: none;
    order: -1;
  }

  .service-card.featured:hover {
    transform: translateY(-5px);
  }

  .benefits-banner {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

@media (max-width: 640px) {
  .services-section {
    padding: 4rem 1rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .service-card {
    padding: 1.5rem;
  }

  .benefits-banner {
    padding: 1.5rem;
  }

  .services-cta {
    padding: 2rem 1.5rem;
  }

  .services-cta h3 {
    font-size: 1.5rem;
  }

  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}
</style>
