<template>
  <section class="hero-section">
    <div class="hero-content">
      <div class="hero-text">
        <h1 class="hero-title">
          <span class="brand-name">PETRU</span>WORKOUT
        </h1>
        <h2 class="hero-headline">
          Consigue menos de 20% de grasa y +3kg de músculo en 90 Días
        </h2>
        <p class="hero-guarantee">
          SI NO LO CONSIGUES, TE DEVUELVO TODO TU DINERO – FIRMADO POR CONTRATO
        </p>
        <div class="hero-cta">
          <a href="#calendly" class="btn btn-primary">
            📅 Agendar Llamada Gratuita
          </a>
          <a href="#testimonios" class="btn btn-secondary">
            ⭐ Ver Testimonios
          </a>
        </div>
      </div>

      <div class="hero-image">
        <img
          src="/images/petru-hero.jpg"
          alt="Petru - Entrenador Personal de Calistenia"
          class="petru-photo"
        />
        <div class="stats-badge">
          <div class="stat-item">
            <span class="stat-number">1000+</span>
            <span class="stat-label">Clientes Transformados</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Social Proof -->
    <div class="social-proof">
      <p class="proof-text">Personas que han confiado en mí</p>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HeroSection'
}
</script>

<style scoped>
.hero-section {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  max-width: 1400px;
  width: 100%;
  align-items: center;
  position: relative;
  z-index: 1;
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.hero-title {
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 900;
  line-height: 1;
  margin: 0;
  color: var(--color-text-primary);
  letter-spacing: -0.03em;
}

.brand-name {
  color: var(--color-accent);
  display: block;
  text-transform: uppercase;
}

.hero-headline {
  font-size: clamp(1.25rem, 3vw, 1.75rem);
  font-weight: 700;
  color: var(--color-text-secondary);
  line-height: 1.3;
  margin: 0;
}

.hero-guarantee {
  font-size: clamp(0.9rem, 2vw, 1.1rem);
  font-weight: 700;
  color: var(--color-accent);
  line-height: 1.5;
  text-transform: uppercase;
  padding: 1rem;
  background: rgba(230, 57, 70, 0.1);
  border-left: 4px solid var(--color-accent);
  border-radius: var(--radius-sm);
}

.hero-cta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.hero-image {
  position: relative;
  animation: fadeIn 1s ease 0.3s both;
}

.petru-photo {
  width: 100%;
  max-width: 500px;
  height: auto;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.stats-badge {
  position: absolute;
  bottom: 2rem;
  left: 2rem;
  right: 2rem;
  padding: 1.5rem;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 900;
  color: var(--color-accent);
}

.stat-label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  text-align: center;
}

.social-proof {
  margin-top: 4rem;
  text-align: center;
}

.proof-text {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Responsive */
@media (max-width: 968px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 3rem;
    text-align: center;
  }

  .hero-text {
    align-items: center;
  }

  .hero-cta {
    justify-content: center;
  }

  .hero-image {
    order: -1;
  }

  .stats-badge {
    position: relative;
    bottom: auto;
    left: auto;
    right: auto;
    margin-top: -2rem;
  }
}

@media (max-width: 480px) {
  .hero-cta {
    flex-direction: column;
    width: 100%;
  }

  .btn {
    width: 100%;
  }
}
</style>
