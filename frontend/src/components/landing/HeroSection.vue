<template>
  <section id="hero" class="hero-section">

```
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

    <!-- Imagen móvil colocada aquí -->
    <div class="hero-image-mobile">
      <img
        :src="mobileImage"
        alt="Petru - Entrenador Personal de Calistenia"
        @error="handleImageError"
      />
    </div>

    <div class="hero-cta">
      <a
        href="https://calendly.com/petruworkout/reunion"
        target="_blank"
        rel="noopener noreferrer"
        class="btn btn-primary"
        @click="trackButtonClick('Agendar Llamada')"
      >
        📅 AGENDAR LLAMADA GRATUITA
      </a>
    </div>

    <div class="guarantee-box">
      <div class="guarantee-text">
        <strong>SI NO LO CONSIGUES, TE DEVUELVO TODO TU DINERO</strong>
        <span>FIRMADO POR CONTRATO</span>
      </div>
    </div>

  </div>

  <!-- Imagen escritorio -->
  <div class="hero-image hero-image-desktop">
    <img
      :src="desktopImage"
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
```

  </section>
</template>

<script>
export default {
  name: 'HeroSection',
  data() {
    return {
      desktopImage: '/images/petru-hero.png',
      mobileImage: '/images/petru-hero-movil.png'
    }
  },
  methods: {
    handleImageError(e) {
      e.target.style.display = 'none'
    },
    trackButtonClick(buttonName) {
      if (window.gtag) {
        window.gtag('event', 'button_click', {
          'button_name': buttonName,
          'page_path': window.location.pathname
        });
      } else {
        console.log('gtag no disponible');
      }
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
  font-size: clamp(1.8rem, 4vw, 3rem);
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

.hero-cta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin: 0.5rem 0;
}

.btn {
  padding: 1.2rem 2.5rem;
  border-radius: 12px;
  font-weight: 800;
  font-size: 1.1rem;
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  background: var(--gradient-primary);
  color: white;
  box-shadow: 0 10px 40px rgba(6, 214, 160, 0.5);
  transform: scale(1.05);
  animation: pulse 2s infinite;
}

.btn-primary:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 15px 50px rgba(6, 214, 160, 0.6);
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 10px 40px rgba(6, 214, 160, 0.5);
  }
  50% {
    box-shadow: 0 10px 40px rgba(6, 214, 160, 0.7);
  }
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

.guarantee-box {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(6, 214, 160, 0.06);
  border: 1px solid rgba(6, 214, 160, 0.2);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  margin: 0;
}

.guarantee-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 100%;
}

.guarantee-text strong {
  color: rgba(6, 214, 160, 0.85);
  font-size: 0.9rem;
  font-weight: 600;
  line-height: 1.3;
}

.guarantee-text span {
  color: rgba(6, 214, 160, 0.55);
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.05em;
}

/* Imagen mobile - oculta por defecto */
.hero-image-mobile {
  display: none;
}

/* Imagen desktop */
.hero-image-desktop {
  position: relative;
  display: flex;
  justify-content: center;
}

.hero-image img {
  max-width: 100%;
  height: auto;
  max-height: 450px;
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
    gap: 2rem;
    text-align: center;
  }

  .hero-text {
    align-items: center;
  }

  .hero-image-desktop {
    order: -1;
  }

  .hero-image img {
    max-height: 280px;
  }

  .hero-cta {
    justify-content: center;
  }

  .hero-title {
    font-size: clamp(1.4rem, 5vw, 2rem);
  }
}

@media (max-width: 640px) {
  .hero-section {
    padding: 5rem 1rem 2rem;
    min-height: 100vh;
  }

  .hero-content {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .hero-text {
    gap: 1rem;
    text-align: center;
    align-items: center;
  }

  .hero-badge {
    font-size: 0.8rem;
    padding: 0.4rem 0.9rem;
  }

  .hero-title {
    font-size: 1.4rem;
    line-height: 1.3;
  }

  .hero-cta {
    flex-direction: column;
    width: 100%;
    margin: 0.8rem 0;
  }

  .btn {
    width: 100%;
    justify-content: center;
    padding: 1.2rem 1.5rem;
    font-size: 1rem;
    font-weight: 900;
  }

  .guarantee-box {
    text-align: center;
    padding: 0.8rem 1rem;
    margin: 0 0 1.5rem 0;
  }

  .guarantee-text strong {
    font-size: 0.8rem;
    line-height: 1.3;
  }

  .guarantee-text span {
    font-size: 0.7rem;
  }

  /* Ocultar imagen desktop */
  .hero-image-desktop {
    display: none;
  }

  /* Mostrar imagen mobile debajo de garantía */
  .hero-image-mobile {
    display: flex;
    justify-content: center;
    width: 100%;
    margin-top: 0.5rem;
  }

  .hero-image-mobile img {
    max-width: 90%;
    height: auto;
    max-height: 350px;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  }

  .scroll-indicator {
    display: none;
  }
}
</style>
