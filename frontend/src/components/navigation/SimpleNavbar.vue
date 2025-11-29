<template>
  <nav class="simple-navbar" :class="{ 'scrolled': isScrolled }">
    <div class="navbar-container">
      <router-link to="/" class="logo">
        <span class="logo-accent">PETRU</span>WORKOUT
      </router-link>

      <button class="mobile-toggle" @click="menuOpen = !menuOpen" :class="{ 'active': menuOpen }">
        <span></span>
        <span></span>
        <span></span>
      </button>

      <ul class="nav-links" :class="{ 'open': menuOpen }">
        <li>
        <a
            href="https://calendly.com/petruworkout/reunion"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-cta"
            @click="trackCalendlyClick"
          >
            📅 Agendar Llamada
          </a>
        </li>
        <li>
          <router-link
            to="/info"
            class="btn-info"
            @click="trackMoreInfoClick"
          >
            📋 Más Información
          </router-link>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'SimpleNavbar',
  data() {
    return {
      isScrolled: false,
      menuOpen: false
    }
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll)
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll)
  },
  methods: {
    handleScroll() {
      this.isScrolled = window.scrollY > 50
    },

    // Evento para el botón de Calendly
    trackCalendlyClick() {
      this.menuOpen = false

      if (window.gtag) {
        window.gtag('event', 'button_click', {
          'button_name': 'Agendar Llamada',
          'page_path': window.location.pathname,
          'button_location': 'navbar'
        })
      } else {
        console.log('GA - Evento: Agendar Llamada desde navbar')
      }
    },

    // 🆕 Evento NUEVO específico para "Más Información"
    trackMoreInfoClick() {
      this.menuOpen = false

      if (window.gtag) {
        window.gtag('event', 'view_more_info', {
          'source': 'navbar',
          'from_page': window.location.pathname
        })
      } else {
        console.log('GA - Evento: Más Información desde navbar')
      }
    }
  }
}
</script>

<style scoped>
/* El CSS permanece igual */
.simple-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 1rem 0;
  transition: all 0.3s ease;
  background: transparent;
}

.simple-navbar.scrolled {
  background: rgba(13, 13, 13, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
  padding: 0.75rem 0;
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 900;
  text-decoration: none;
  color: white;
  letter-spacing: -0.02em;
}

.logo-accent {
  color: var(--color-accent);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.btn-cta,
.btn-info {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-cta {
  background: var(--gradient-primary);
  color: white;
  box-shadow: 0 4px 15px rgba(6, 214, 160, 0.3);
}

.btn-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(6, 214, 160, 0.5);
}

.btn-info {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-info:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.mobile-toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
}

.mobile-toggle span {
  width: 25px;
  height: 2px;
  background: white;
  transition: all 0.3s ease;
}

.mobile-toggle.active span:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.mobile-toggle.active span:nth-child(2) {
  opacity: 0;
}

.mobile-toggle.active span:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

@media (max-width: 768px) {
  .mobile-toggle {
    display: flex;
  }

  .nav-links {
    position: fixed;
    top: 70px;
    left: 0;
    right: 0;
    background: rgba(13, 13, 13, 0.98);
    flex-direction: column;
    padding: 2rem;
    gap: 1.5rem;
    transform: translateY(-150%);
    opacity: 0;
    transition: all 0.3s ease;
  }

  .nav-links.open {
    transform: translateY(0);
    opacity: 1;
  }

  .btn-cta,
  .btn-info {
    width: 100%;
    justify-content: center;
  }
}
</style>
