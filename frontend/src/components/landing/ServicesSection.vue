<template>
  <section id="servicios" class="services-section">
    <div class="services-container">
      <div class="section-header">
        <span class="section-tag">SERVICIOS</span>
        <h2 class="section-title">Elige tu plan de transformación</h2>
        <p class="section-subtitle">
          Programas diseñados para llevar tu físico al siguiente nivel
        </p>
      </div>

      <div class="services-grid">
        <div class="service-card">
          <div class="card-header">
            <span class="card-icon">🏃</span>
            <h3>Plan Básico</h3>
            <p class="card-duration">4 Semanas</p>
          </div>

          <ul class="features-list">
            <li><span class="check">✓</span> Rutina personalizada semanal</li>
            <li><span class="check">✓</span> Plan de nutrición básico</li>
            <li><span class="check">✓</span> Videos explicativos</li>
            <li><span class="check">✓</span> Soporte por WhatsApp</li>
          </ul>

          <p class="card-ideal">Ideal para principiantes</p>

          <a href="#calendly" class="btn btn-outline">
            Más información
          </a>
        </div>

        <div class="service-card featured">
          <div class="featured-badge">🔥 MÁS POPULAR</div>
          <div class="card-header">
            <span class="card-icon">💪</span>
            <h3>Plan Pro</h3>
            <p class="card-duration">90 Días</p>
          </div>

          <ul class="features-list">
            <li><span class="check">✓</span> Todo del Plan Básico</li>
            <li><span class="check">✓</span> Seguimiento semanal personalizado</li>
            <li><span class="check">✓</span> Plan nutricional completo</li>
            <li><span class="check">✓</span> Ajustes según tu progreso</li>
            <li><span class="check">✓</span> Llamadas de seguimiento</li>
            <li><span class="check">✓</span> <strong>Garantía de resultados</strong></li>
          </ul>

          <p class="card-ideal">Para resultados garantizados</p>

          <a href="#calendly" class="btn btn-primary">
            Agendar Llamada Gratis
          </a>
        </div>

        <div class="service-card">
          <div class="card-header">
            <span class="card-icon">🏆</span>
            <h3>Plan Elite</h3>
            <p class="card-duration">6 Meses</p>
          </div>

          <ul class="features-list">
            <li><span class="check">✓</span> Todo del Plan Pro</li>
            <li><span class="check">✓</span> Coaching 1 a 1 semanal</li>
            <li><span class="check">✓</span> Plan de suplementación</li>
            <li><span class="check">✓</span> Acceso prioritario</li>
            <li><span class="check">✓</span> Comunidad privada</li>
          </ul>

          <p class="card-ideal">Transformación completa</p>

          <a href="#calendly" class="btn btn-outline">
            Más información
          </a>
        </div>
      </div>

      <div class="services-note">
        <p>
          💡 <strong>¿No sabes cuál elegir?</strong>
          Agenda una llamada gratuita y te ayudo a elegir el plan perfecto para ti.
        </p>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ServicesSection'
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
}

.service-card.featured {
  background: linear-gradient(135deg, rgba(230, 57, 70, 0.1) 0%, rgba(230, 57, 70, 0.05) 100%);
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

.card-duration {
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
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.features-list li:last-child {
  border-bottom: none;
}

.check {
  color: var(--color-success);
  font-weight: 700;
  flex-shrink: 0;
}

.card-ideal {
  text-align: center;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin: 0 0 1.5rem 0;
  font-style: italic;
}

.btn {
  display: block;
  text-align: center;
  padding: 1rem 1.5rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--gradient-primary);
  color: white;
  box-shadow: 0 8px 30px rgba(230, 57, 70, 0.3);
}

.btn-primary:hover {
  box-shadow: 0 12px 40px rgba(230, 57, 70, 0.5);
}

.btn-outline {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.4);
}

.services-note {
  text-align: center;
  margin-top: 3rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
}

.services-note p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 1rem;
}

@media (max-width: 968px) {
  .services-grid {
    grid-template-columns: 1fr;
    max-width: 450px;
    margin: 0 auto;
  }

  .service-card.featured {
    transform: none;
    order: -1;
  }

  .service-card.featured:hover {
    transform: translateY(-5px);
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
}
</style>
