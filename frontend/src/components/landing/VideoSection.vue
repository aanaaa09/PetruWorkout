<template>
  <section id="video" class="video-section">
    <div class="video-container">
      <div class="section-header">
        <span class="section-tag">CONOCE MI MÉTODO</span>
        <h2 class="section-title">Así trabajo con mis clientes</h2>
        <p class="section-subtitle">
          Mira cómo transformo vidas con mi método de entrenamiento personalizado
        </p>
      </div>

      <div class="video-wrapper">
        <iframe
          class="video-frame"
          width="100%"
          height="100%"
          src="https://www.youtube.com/embed/yCDxpnd_Dz0?rel=0&modestbranding=1"
          title="Petru Workout - Método de Entrenamiento"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
        ></iframe>
      </div>

      <div class="video-cta">
        <p>¿Quieres ver más contenido?</p>
        <div class="social-buttons">
          <a
            href="https://www.youtube.com/@petruworkout"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-youtube"
          >
            ▶️ Suscríbete en YouTube
          </a>
          <a
            href="https://www.instagram.com/petruworkout"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-instagram"
          >
            📷 Sígueme en Instagram
          </a>
          <a
            href="https://linkedin.com/in/adrián-oltean-696a2236b"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-linkedin"
          >
            💼 Conéctate en LinkedIn
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'VideoSection'
}
</script>

<style scoped>
.video-section {
  padding: 6rem 2rem;
  background: var(--bg-secondary);
}

.video-container {
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

.video-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* Aspect ratio 16:9 */
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  background: #000;
}

.video-frame {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-cta {
  text-align: center;
  margin-top: 3rem;
}

.video-cta p {
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
  margin-bottom: 1.5rem;
}

.social-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.875rem 1.75rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-youtube {
  background: #ff0000;
  color: white;
  box-shadow: 0 4px 20px rgba(255, 0, 0, 0.3);
}

.btn-youtube:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(255, 0, 0, 0.5);
}

.btn-instagram {
  background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045);
  color: white;
  box-shadow: 0 4px 20px rgba(253, 29, 29, 0.3);
}

.btn-instagram:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(253, 29, 29, 0.5);
}

.btn-linkedin {
  background: #0077b5;
  color: white;
  box-shadow: 0 4px 20px rgba(0, 119, 181, 0.3);
}

.btn-linkedin:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(0, 119, 181, 0.5);
  background: #005885;
}

@media (max-width: 768px) {
  .video-section {
    padding: 4rem 1rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .social-buttons {
    flex-direction: column;
    max-width: 300px;
    margin: 0 auto;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
