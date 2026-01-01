<template>
  <section id="testimonios" class="testimonials-section">
    <div class="testimonials-container">
      <!-- Header -->
      <div class="section-header">
        <span class="section-tag">RESEÑAS</span>
        <h2 class="section-title">Lo que dicen mis clientes</h2>
        <p class="section-subtitle">
          Opiniones verificadas sobre mi
        </p>
      </div>

      <!-- Banner escribir reseña -->
      <div class="write-review-banner">
        <div class="banner-content">
          <div class="banner-icon">⭐</div>
          <div class="banner-text">
            <h3>¿Ya eres cliente?</h3>
            <p>Comparte tu experiencia y ayuda a otros a transformar su vida</p>
          </div>
        </div>

        <a
          href="https://g.page/r/CY-uUquICNdTEAE/review"
          target="_blank"
          rel="noopener noreferrer"
          class="btn-write-review"
        >
          ✍️ Escribir Reseña en Google
        </a>
      </div>

      <!-- Widget reseñas -->
      <div class="reviews-widget">
        <div class="elfsight-container">
          <div
            class="elfsight-app-c798cd4c-2cd5-492d-aa04-e5eda7d88ab2"
            data-elfsight-app-lazy
          ></div>
        </div>
      </div>

      <!-- Trust indicators -->
      <div class="trust-indicators">
        <div class="indicator">
          <span class="indicator-icon">✓</span>
          <span>Verificadas por Google</span>
        </div>
        <div class="indicator">
          <span class="indicator-icon">🔒</span>
          <span>Clientes reales</span>
        </div>
        <div class="indicator">
          <span class="indicator-icon">⭐</span>
          <span>100% transparentes</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'TestimonialsSection',
  mounted() {
    const SRC = 'https://elfsightcdn.com/platform.js'

    if (!document.querySelector(`script[src="${SRC}"]`)) {
      const script = document.createElement('script')
      script.src = SRC
      script.async = true
      document.body.appendChild(script)
    }
  }
}
</script>

<style scoped>
.testimonials-section {
  padding: 6rem 2rem;
  background: var(--bg-primary);
}

.testimonials-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
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

/* Banner */
.write-review-banner {
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.15) 0%, rgba(6, 214, 160, 0.05) 100%);
  border: 2px solid rgba(6, 214, 160, 0.3);
  border-radius: 20px;
  padding: 2.5rem;
  margin-bottom: 3rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex: 1;
}

.banner-icon {
  font-size: 3rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.banner-text h3 {
  font-size: 1.5rem;
  color: white;
  margin: 0 0 0.5rem 0;
}

.banner-text p {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.btn-write-review {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1.25rem 2.5rem;
  background: var(--gradient-primary);
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
  white-space: nowrap;
}

.btn-write-review:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.6);
}

/* Widget */
.reviews-widget {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.elfsight-container {
  min-height: 400px;
}

/* Trust */
.trust-indicators {
  display: flex;
  justify-content: center;
  gap: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.indicator-icon {
  color: var(--color-success);
  font-size: 1.2rem;
}

/* Responsive */
@media (max-width: 968px) {
  .write-review-banner {
    flex-direction: column;
    text-align: center;
    padding: 2rem;
  }

  .banner-content {
    flex-direction: column;
    text-align: center;
  }

  .btn-write-review {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .testimonials-section {
    padding: 4rem 1rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .banner-text h3 {
    font-size: 1.25rem;
  }

  .trust-indicators {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .reviews-widget {
    padding: 1rem;
  }
}
</style>
