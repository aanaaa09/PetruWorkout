<template>
  <div class="app-container">
    <AppHeader
      :usuario-logueado="!!usuarioActual"
      @mostrar-login="mostrarLogin = true"
      @logout="cerrarSesion"
    />

    <div class="main-content">
      <LandingView v-if="!usuarioActual" />
      <DashboardView v-else :usuario="usuarioActual" />
    </div>

    <Auth
      v-if="mostrarLogin && !usuarioActual"
      @login="iniciarSesion"
      @close="mostrarLogin = false"
    />
  </div>
</template>

<script>
import AppHeader from './components/layout/AppHeader.vue'
import LandingView from './views/LandingView.vue'
import DashboardView from './views/DashboardView.vue'
import Auth from './components/auth/Auth.vue'

export default {
  components: {
    AppHeader,
    LandingView,
    DashboardView,
    Auth
  },
  data() {
    return {
      usuarioActual: null,
      token: null,
      mostrarLogin: false
    }
  },
  methods: {
    iniciarSesion(data) {
      this.usuarioActual = data.usuario
      this.token = data.token
      this.mostrarLogin = false
    },

    async cerrarSesion() {
      if (this.token) {
        try {
          await fetch('http://localhost:5000/api/auth/logout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: this.token })
          })
        } catch (err) {
          console.error('Error cerrando sesión:', err)
        }
      }
      this.usuarioActual = null
      this.token = null
    }
  }
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body, html {
  font-family: var(--font-family);
  height: 100vh;
  overflow-x: hidden;
  color: var(--color-text-primary);
  background: var(--bg-primary);
  position: relative;
}

/* Fondo con textura sutil */
body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(230, 57, 70, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(43, 45, 66, 0.1) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

#app {
  height: 100vh;
  position: relative;
  z-index: 1;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  width: 100%;
  position: relative;
}

.main-content {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
}

/* Botones globales */
.btn {
  padding: 0.875rem 2rem;
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--font-size-base);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
  text-transform: none;
  letter-spacing: -0.01em;
  position: relative;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  text-decoration: none;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s ease;
}

.btn:hover::before {
  left: 100%;
}

.btn:hover {
  transform: translateY(-2px);
}

.btn:active {
  transform: translateY(0);
}

.btn-primary {
  background: var(--gradient-primary);
  color: white;
  box-shadow: var(--shadow-accent);
}

.btn-primary:hover {
  box-shadow: 0 12px 40px rgba(230, 57, 70, 0.5);
}

.btn-secondary {
  background: var(--glass-bg);
  border: 2px solid var(--glass-border);
  color: white;
  backdrop-filter: var(--glass-blur);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Scrollbar personalizada */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--color-secondary-light);
  border-radius: var(--radius-sm);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-accent);
}

/* Responsive */
@media (max-width: 768px) {
  .btn {
    padding: 0.75rem 1.5rem;
    font-size: var(--font-size-sm);
  }
}

@media (max-width: 480px) {
  .btn {
    padding: 0.625rem 1.25rem;
    font-size: var(--font-size-sm);
  }
}
</style>
