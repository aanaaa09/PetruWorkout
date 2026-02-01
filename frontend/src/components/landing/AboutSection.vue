<template>
  <section id="sobre-mi" class="about-section">
    <div class="about-container">
      <div class="about-image">

        <img
          src="/images/petru-about.webp"
          alt="Petru - Entrenador Personal"
          width="571"
          height="565"
          fetchpriority="high"
          loading="eager"
          @error="handleImageError"
        />
        <div class="experience-badge">
          <span class="years">5+</span>
          <span class="text">años de experiencia</span>
        </div>
      </div>

      <div class="about-content">
        <span class="section-tag">SOBRE MÍ</span>
        <h2 class="about-title">
          Hola, soy <span class="accent">Petru</span>
        </h2>

        <p class="about-description">
          Soy entrenador personal especializado en <strong>calistenia y transformación física</strong>.
          Mi misión es ayudarte a conseguir el cuerpo que siempre has querido,
          sin necesidad de gimnasio ni equipamiento costoso.
        </p>

        <p class="about-description">
          He ayudado a más de <strong>50 personas</strong> a transformar su físico
          y su vida a través de mi método de entrenamiento personalizado.
        </p>

        <div class="credentials">
          <h3>Mis Credenciales</h3>
          <ul class="credentials-list">
            <li>
              <span class="check">✓</span>
              Certificación en Entrenamiento Personal
            </li>
            <li>
              <span class="check">✓</span>
              Especialista en Calistenia y Street Workout
            </li>
            <li>
              <span class="check">✓</span>
              Experto en Nutrición Deportiva
            </li>
          </ul>
        </div>

        <div class="about-values">
          <div class="value-card">
            <span class="value-icon">🎯</span>
            <h4>Resultados</h4>
            <p>Método probado con garantía de devolución</p>
          </div>
          <div class="value-card">
            <span class="value-icon">🤝</span>
            <h4>Compromiso</h4>
            <p>Seguimiento personalizado semanal</p>
          </div>
          <div class="value-card">
            <span class="value-icon">💡</span>
            <h4>Adaptación</h4>
            <p>Planes ajustados a tu nivel y objetivos</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'AboutSection',
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
.about-section {
  padding: 6rem 2rem;
  background: var(--bg-secondary);
}

.about-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 4rem;
  align-items: center;
}

.about-image {
  position: relative;
}

.about-image img {
  width: 100%;
  max-width: 450px;
  height: auto; /* ✅ AÑADIDO para mantener ratio */
  border-radius: 20px;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4);
}

.experience-badge {
  position: absolute;
  bottom: -20px;
  right: -20px;
  background: var(--gradient-primary);
  padding: 1.5rem;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 10px 30px rgba(230, 57, 70, 0.4);
}

.experience-badge .years {
  font-size: 2.5rem;
  font-weight: 900;
  color: white;
  line-height: 1;
}

.experience-badge .text {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
}

.about-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-tag {
  font-size: 0.85rem;
  color: var(--color-accent);
  font-weight: 700;
  letter-spacing: 0.15em;
}

.about-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  margin: 0;
  line-height: 1.2;
}

.about-title .accent {
  color: var(--color-accent);
}

.about-description {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin: 0;
}

.about-description strong {
  color: white;
}

.credentials {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.credentials h3 {
  font-size: 1.1rem;
  color: white;
  margin: 0 0 1rem 0;
}

.credentials-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.credentials-list li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--color-text-secondary);
  font-size: 0.95rem;
}

.check {
  color: var(--color-success);
  font-weight: 700;
}

.about-values {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 1rem;
}

.value-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
}

.value-card:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-5px);
}

.value-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.value-card h4 {
  font-size: 1rem;
  color: white;
  margin: 0 0 0.5rem 0;
}

.value-card p {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.4;
}

@media (max-width: 968px) {
  .about-container {
    grid-template-columns: 1fr;
    gap: 3rem;
  }

  .about-image {
    display: flex;
    justify-content: center;
  }

  .about-image img {
    max-width: 350px;
  }

  .experience-badge {
    right: 10%;
  }

  .about-values {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .about-section {
    padding: 4rem 1rem;
  }

  .about-title {
    font-size: 2rem;
  }

  .about-description {
    font-size: 1rem;
  }
}
</style>
