<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-main">
        <div class="footer-brand">
          <h3 class="logo">
            <span class="logo-accent">PETRU</span>WORKOUT
          </h3>
          <p>
            Entrenador personal especializado en calistenia y transformación física.
            Ayudo a personas a conseguir el cuerpo que siempre han querido.
          </p>
        </div>

        <div class="footer-links">
          <div class="link-group">
            <h4>Navegación</h4>
            <a href="#sobre-mi">Sobre mí</a>
            <a href="#servicios">Servicios</a>
            <a href="#resultados">Resultados</a>
            <a href="#testimonios">Testimonios</a>
          </div>

          <div class="link-group">
            <h4>Contacto</h4>
            <a href="#calendly">Agendar Llamada</a>
            <a href="#contacto">Formulario</a>
            <a href="mailto:petruworkout@gmail.com">Email</a>
          </div>

          <div class="link-group">
            <h4>Legal</h4>
            <a href="#" @click.prevent="handlePrivacyClick">Política de Privacidad</a>
            <a href="#" @click.prevent="handleLegalClick">Aviso Legal</a>
            <a href="#" @click.prevent="handleTermsClick">Términos y Condiciones</a>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <p class="copyright">
          © {{ currentYear }} PetruWorkout. Todos los derechos reservados.
        </p>

        <p class="credits">
          Desarrollado por
          <a
            href="https://linkedin.com/in/ana-seseña-4290891bb"
            target="_blank"
            rel="noopener noreferrer"
          >
            Ana Seseña
          </a>
        </p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer',
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  },
  methods: {
    handlePrivacyClick() {
      console.log('Privacy clicked')
      this.$emit('show-privacy')
    },
    handleLegalClick() {
      console.log('Legal clicked')
      this.$emit('show-legal')
    },
    handleTermsClick() {
      console.log('Terms clicked')
      this.$emit('show-terms')
    }
  }
}
</script>

<style scoped>
.app-footer {
  background: rgba(0, 0, 0, 0.6);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding: 4rem 2rem 2rem;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-main {
  display: grid;
  grid-template-columns: 1.5fr 2fr;
  gap: 4rem;
  padding-bottom: 3rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.footer-brand {
  max-width: 350px;
}

.logo {
  font-size: 1.5rem;
  font-weight: 900;
  color: white;
  margin: 0 0 1rem 0;
}

.logo-accent {
  color: var(--color-accent);
}

.footer-brand p {
  color: var(--color-text-muted);
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0;
}

.footer-links {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.link-group h4 {
  font-size: 1rem;
  color: white;
  font-weight: 700;
  margin: 0 0 1rem 0;
}

.link-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.link-group a {
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
  cursor: pointer;
}

.link-group a:hover {
  color: var(--color-accent);
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.copyright {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin: 0;
}

.credits {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin: 0;
}

.credits a {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.credits a:hover {
  text-decoration: underline;
}

@media (max-width: 968px) {
  .footer-main {
    grid-template-columns: 1fr;
    gap: 3rem;
  }

  .footer-brand {
    max-width: 100%;
    text-align: center;
  }

  .footer-links {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 640px) {
  .app-footer {
    padding: 3rem 1rem 1.5rem;
  }

  .footer-links {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .link-group {
    align-items: center;
  }

  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
}
</style>
