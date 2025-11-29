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
  padding-bottom: 56.25%;
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

@media (max-width: 768px) {
  .video-section {
    padding: 4rem 1rem;
  }

  .section-title {
    font-size: 2rem;
  }
}
</style>
