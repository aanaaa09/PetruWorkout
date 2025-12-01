<template>
  <nav class="navbar" :class="{ 'scrolled': isScrolled }">
    <div class="navbar-container">
      <router-link to="/info" class="logo" @click="scrollToTop">
        <span class="logo-accent">PETRU</span>WORKOUT
      </router-link>

      <button class="mobile-toggle" @click="menuOpen = !menuOpen" :class="{ 'active': menuOpen }">
        <span></span>
        <span></span>
        <span></span>
      </button>

      <ul class="nav-links" :class="{ 'open': menuOpen }">
        <li><a href="#sobre-mi" @click.prevent="navigateTo('sobre-mi')">Sobre mí</a></li>
        <li><a href="#servicios" @click.prevent="navigateTo('servicios')">Servicios</a></li>
        <li><a href="#testimonios" @click.prevent="navigateTo('testimonios')">Reseñas</a></li>
        <li><a href="#contacto" @click.prevent="navigateTo('contacto')">Contacto</a></li>
         <li class="nav-cta">
    <!-- ✅ CAMBIAR A LINK DIRECTO -->
    <a
      href="https://calendly.com/petruworkout/reunion"
      target="_blank"
      rel="noopener noreferrer"
      class="btn-cta"
    >
      📅 Agendar Llamada
    </a>
  </li>
      </ul>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'FullNavbar',
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
    scrollToTop() {
      this.$nextTick(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' })
      })
    },
    navigateTo(section) {
      this.menuOpen = false
      this.$emit('scroll-to', section)
    }
  }
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 1rem 0;
  transition: all 0.3s ease;
  background: transparent;
}

.navbar.scrolled {
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
  gap: 2rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-links a {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.3s ease;
  position: relative;
}

.nav-links a::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--color-accent);
  transition: width 0.3s ease;
}

.nav-links a:hover {
  color: white;
}

.nav-links a:hover::after {
  width: 100%;
}

.btn-cta {
  background: var(--gradient-primary);
  padding: 0.75rem 1.5rem !important;
  border-radius: 8px;
  color: white !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 15px rgba(230, 57, 70, 0.3);
  transition: all 0.3s ease !important;
}

.btn-cta::after {
  display: none !important;
}

.btn-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(230, 57, 70, 0.5);
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

@media (max-width: 968px) {
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

  .nav-cta {
    width: 100%;
  }

  .btn-cta {
    display: block;
    text-align: center;
    width: 100%;
  }
}
</style>
