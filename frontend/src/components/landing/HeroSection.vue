<template>
  <section id="hero" class="hero-section">

    <div class="hero-bg">
  <div class="hero-overlay"></div>
    </div>

    <div class="hero-content">
      <div class="hero-text">
        <span class="hero-badge">🏋️ Entrenamiento Personal Online</span>

        <h1 class="hero-title">
          Consigue menos de <span class="highlight">20% de grasa</span>
          y <span class="highlight">+3kg de músculo</span> en
          <span class="accent">90 Días</span>
        </h1>

        <p class="hero-subtitle">
          Con Calistenia y mi método probado de entrenamiento personalizado
        </p>

        <div class="guarantee-box">
          <div class="guarantee-icon">🛡️</div>
          <div class="guarantee-text">
            <strong>SI NO LO CONSIGUES, TE DEVUELVO TODO TU DINERO</strong>
            <span>FIRMADO POR CONTRATO</span>
          </div>
        </div>

        <div class="hero-cta">
          <a
            href="https://calendly.com/petruworkout/reunion"
            target="_blank"
            rel="noopener noreferrer"
        class="btn btn-primary"
        >
        📅 Agendar Llamada Gratuita
      </a>
          <a href="#resultados" class="btn btn-secondary">
            Ver Transformaciones →
          </a>
        </div>

        <div class="hero-stats">
          <div class="stat">
            <span class="stat-number">50+</span>
            <span class="stat-label">Clientes Transformados</span>
          </div>
          <div class="stat">
            <span class="stat-number">5+</span>
            <span class="stat-label">Años de Experiencia</span>
          </div>
          <div class="stat">
            <span class="stat-number">98%</span>
            <span class="stat-label">Tasa de Éxito</span>
          </div>
        </div>
      </div>

      <div class="hero-image">
        <img
          src="/images/petru-hero.png"
          alt="Petru - Entrenador Personal de Calistenia"
          @error="handleImageError"
        />
        <div class="image-decoration"></div>
      </div>
    </div>

    <div class="scroll-indicator">
      <span>Descubre más</span>
      <div class="scroll-arrow">↓</div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HeroSection',
  data() {
    return {
      useVideo: true
    }
  },
  methods: {
    handleImageError(e) {
      e.target.style.display = 'none'
    }
  }
}
</script>

<style scoped>
.hero-section {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  padding: 6rem 2rem 4rem;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  background: linear-gradient(135deg, rgba(13, 13, 13, 0.95) 0%, rgba(26, 26, 26, 0.90) 100%);
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(13, 13, 13, 0.95) 0%,
    rgba(26, 26, 26, 0.85) 50%,
    rgba(13, 13, 13, 0.9) 100%
  );
}

.hero-content {
  max-width: 1400px;
  width: 100%;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 4rem;
  align-items: center;
  position: relative;
  z-index: 1;
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.hero-badge {
  display: inline-block;
  background: rgba(6, 214, 160, 0.15);
  border: 1px solid rgba(6, 214, 160, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-accent);
  width: fit-content;
}

.hero-title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 900;
  line-height: 1.1;
  color: white;
  margin: 0;
}

.hero-title .highlight {
  color: white;
  background: linear-gradient(135deg, #fff 0%, #e0e0e0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-title .accent {
  color: var(--color-accent);
  -webkit-text-fill-color: var(--color-accent);
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

.guarantee-box {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(6, 214, 160, 0.1);
  border: 2px solid var(--color-accent);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  margin: 0.5rem 0;
}

.guarantee-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.guarantee-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.guarantee-text strong {
  color: white;
  font-size: 1rem;
  font-weight: 700;
}

.guarantee-text span {
  color: var(--color-accent);
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.hero-cta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}

.btn {
  padding: 1rem 2rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 1rem;
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: var(--gradient-primary);
  color: white;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.5);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.hero-stats {
  display: flex;
  gap: 3rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: 900;
  color: var(--color-accent);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.hero-image {
  position: relative;
  display: flex;
  justify-content: center;
}

.hero-image img {
  max-width: 100%;
  height: auto;
  max-height: 600px;
  border-radius: 20px;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
  position: relative;
  z-index: 1;
}

.image-decoration {
  display: none;
}

.scroll-indicator {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-muted);
  font-size: 0.85rem;
  animation: bounce 2s infinite;
}

.scroll-arrow {
  font-size: 1.5rem;
}

@keyframes bounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(10px); }
}

@media (max-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 3rem;
    text-align: center;
  }

  .hero-text {
    align-items: center;
  }

  .hero-image {
    order: -1;
  }

  .hero-image img {
    max-height: 400px;
  }

  .hero-stats {
    justify-content: center;
  }

  .hero-cta {
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .hero-section {
    padding: 5rem 1rem 3rem;
  }

  .hero-stats {
    flex-direction: column;
    gap: 1.5rem;
  }

  .hero-cta {
    flex-direction: column;
    width: 100%;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .guarantee-box {
    flex-direction: column;
    text-align: center;
  }

  .scroll-indicator {
    display: none;
  }
}
</style>
