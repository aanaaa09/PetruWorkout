<template>
  <nav class="simple-navbar" :class="{ 'scrolled': isScrolled }">
    <div class="navbar-container">
      <router-link to="/" class="logo" @click="scrollToTop">
        <span class="logo-accent">PETRU</span>WORKOUT
      </router-link>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'SimpleNavbar',
  data() {
    return {
      isScrolled: false
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
    }
  }
}
</script>

<style scoped>
/* ===== NAVBAR BASE ===== */
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
  justify-content: center;
  align-items: center;
}

/* ===== LOGO ===== */
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

@media (max-width: 768px) {
  .logo {
    font-size: 1.25rem;
  }
}
</style>
