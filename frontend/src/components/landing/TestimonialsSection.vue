<template>
  <section id="testimonios" class="testimonials-section">
    <div class="testimonials-container">
      <div class="section-header">
        <span class="section-tag">TESTIMONIOS</span>
        <h2 class="section-title">Lo que dicen mis clientes</h2>
        <p class="section-subtitle">
          Opiniones verificadas de personas que han trabajado conmigo
        </p>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando testimonios...</p>
      </div>

      <!-- Empty state -->
      <div v-else-if="testimonials.length === 0" class="empty-state">
        <div class="empty-icon">💬</div>
        <h3>Próximamente</h3>
        <p>Las reseñas de mis clientes aparecerán aquí pronto.</p>
        <p class="empty-note">
          ¿Ya eres cliente? Pronto podrás dejar tu reseña.
        </p>
      </div>

      <!-- Testimonials grid -->
      <div v-else class="testimonials-grid">
        <div
          v-for="testimonial in testimonials"
          :key="testimonial.id"
          class="testimonial-card"
        >
          <div class="testimonial-header">
            <div class="avatar">
              {{ getInitials(testimonial.nombre) }}
            </div>
            <div class="info">
              <h4>{{ testimonial.nombre }}</h4>
              <div class="stars">
                <span v-for="n in 5" :key="n" class="star" :class="{ filled: n <= testimonial.valoracion }">
                  ★
                </span>
              </div>
            </div>
          </div>

          <p class="testimonial-text">"{{ testimonial.texto }}"</p>

          <span class="testimonial-date">{{ formatDate(testimonial.fecha) }}</span>
        </div>
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
  name: 'TestimonialsSection',
  data() {
    return {
      testimonials: [],
      loading: true
    }
  },
  mounted() {
    this.loadTestimonials()
  },
  methods: {
    async loadTestimonials() {
      try {
        const response = await fetch('http://localhost:5000/api/resenas/publicas')
        if (response.ok) {
          const data = await response.json()
          this.testimonials = data.resenas || []
        }
      } catch (error) {
        console.log('No se pudieron cargar las reseñas')
        this.testimonials = []
      } finally {
        this.loading = false
      }
    },
    getInitials(name) {
      return name
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long'
      })
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

.loading-state {
  text-align: center;
  padding: 4rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: var(--color-text-muted);
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

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.testimonial-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 2rem;
  transition: all 0.3s ease;
}

.testimonial-card:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-5px);
}

.testimonial-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  color: white;
}

.info h4 {
  font-size: 1rem;
  color: white;
  margin: 0 0 0.25rem 0;
}

.stars {
  display: flex;
  gap: 2px;
}

.star {
  color: rgba(255, 255, 255, 0.2);
  font-size: 1rem;
}

.star.filled {
  color: #ffd700;
}

.testimonial-text {
  font-size: 1rem;
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin: 0 0 1rem 0;
  font-style: italic;
}

.testimonial-date {
  font-size: 0.8rem;
  color: var(--color-text-muted);
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

@media (max-width: 968px) {
  .testimonials-grid {
    grid-template-columns: 1fr;
    max-width: 500px;
    margin: 0 auto;
  }
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

  .testimonial-card {
    padding: 1.5rem;
  }
}
</style>
