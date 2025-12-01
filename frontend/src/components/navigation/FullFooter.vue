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
            <router-link to="/">Inicio</router-link>
            <a href="#sobre-mi" @click.prevent="scrollTo('sobre-mi')">Sobre mí</a>
            <a href="#servicios" @click.prevent="scrollTo('servicios')">Servicios</a>
            <a href="#testimonios" @click.prevent="scrollTo('testimonios')">Reseñas</a>
          </div>

          <div class="link-group">
            <h4>Contacto</h4>
             <li class="nav-cta">
    <!-- ✅ CAMBIAR A LINK DIRECTO -->
    <a
      href="https://calendly.com/petruworkout/reunion"
      target="_blank"
      rel="noopener noreferrer"
      class="btn-cta"
    >
      Agendar Llamada
    </a>
  </li>
            <a href="#contacto" @click.prevent="scrollTo('contacto')">Formulario</a>
            <a href="mailto:petruworkout@gmail.com">Email</a>
          </div>

          <div class="link-group">
            <h4>Legal</h4>
            <button @click="$emit('show-legal', 'privacy')" class="footer-link-btn">
              Política de Privacidad
            </button>
            <button @click="$emit('show-legal', 'terms')" class="footer-link-btn">
              Términos y Condiciones
            </button>
            <button @click="$emit('show-legal', 'legal-notice')" class="footer-link-btn">
              Aviso Legal
            </button>
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
  name: 'FullFooter',
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  },
  methods: {
    scrollTo(sectionId) {
      const el = document.getElementById(sectionId)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
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

.link-group a,
.footer-link-btn {
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
  text-align: left;
  font-family: inherit;
}

.link-group a:hover,
.footer-link-btn:hover {
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

.copyright,
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

  .footer-link-btn {
    text-align: center;
  }

  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
}
</style>
