<template>
  <section id="testimonios" class="testimonials-section">
    <div class="testimonials-container">
      <div class="section-header">
        <span class="section-tag">RESEÑAS</span>
        <h2 class="section-title">Lo que dicen mis clientes</h2>
        <p class="section-subtitle">
          Opiniones verificadas de personas que han trabajado conmigo
        </p>
      </div>

      <!-- Solo mostrar el estado de próximamente -->
      <div class="empty-state">
        <div class="empty-icon">💬</div>
        <h3>Próximamente</h3>
        <p>Las reseñas de mis clientes aparecerán aquí pronto.</p>
        <p class="empty-note">
          ¿Ya eres cliente? Pronto podrás dejar tu reseña.
        </p>
      </div>

      <!-- Trust indicators -->
      <div class="trust-indicators">
        <div class="indicator">
          <span class="indicator-icon">✓</span>
          <span>Opiniones verificadas</span>
        </div>
        <div class="indicator">
          <span class="indicator-icon">🔒</span>
          <span>Clientes reales</span>
        </div>
        <div class="indicator">
          <span class="indicator-icon">📊</span>
          <span>Resultados documentados</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'TestimonialsSection'
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

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  border: 2px dashed rgba(255, 255, 255, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: white;
  margin: 0 0 1rem 0;
}

.empty-state p {
  color: var(--color-text-muted);
  margin: 0;
}

.empty-note {
  margin-top: 1rem !important;
  font-size: 0.9rem;
  font-style: italic;
}

.trust-indicators {
  display: flex;
  justify-content: center;
  gap: 3rem;
  margin-top: 4rem;
  padding-top: 3rem;
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
}

@media (max-width: 640px) {
  .testimonials-section {
    padding: 4rem 1rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .trust-indicators {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .empty-state {
    padding: 3rem 1.5rem;
  }
}
</style>
