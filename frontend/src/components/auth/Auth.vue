<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Toggle entre Login y Registro -->
      <div class="auth-tabs">
        <button
          @click="modo = 'login'"
          :class="['tab', { active: modo === 'login' }]"
        >
          Iniciar Sesión
        </button>
        <button
          @click="modo = 'registro'"
          :class="['tab', { active: modo === 'registro' }]"
        >
          Registrarse
        </button>
      </div>

      <!-- Formularios -->
      <LoginForm
        v-if="modo === 'login'"
        ref="loginForm"
        :loading="cargando"
        :error="error"
        @submit="login"
      />

      <RegisterForm
        v-else
        ref="registerForm"
        :loading="cargando"
        :error="error"
        @submit="registrar"
      />

      <!-- Nota informativa -->
      <div class="auth-note">
        <p>🔐 Tus datos se almacenan de forma segura</p>
      </div>
    </div>
  </div>
</template>

<script>
import LoginForm from './LoginForm.vue'
import RegisterForm from './RegisterForm.vue'

export default {
  components: {
    LoginForm,
    RegisterForm
  },
  data() {
    return {
      modo: 'login',
      error: null,
      cargando: false
    }
  },
  methods: {
    async login(data) {
      if (this.cargando) return;
      this.error = null
      this.cargando = true

      try {
        const response = await fetch('http://localhost:5000/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: data.email,
            password: data.password
          })
        })

        const result = await response.json()

        if (response.ok && result.success) {
          this.$emit('login', {
            token: result.token,
            usuario: result.usuario
          })
          this.limpiarFormularios()
        } else {
          this.error = result.error || '❌ Error al iniciar sesión'
        }
      } catch (err) {
        console.error('Error en login:', err)
        this.error = '❌ Error de conexión. ¿El servidor está corriendo?'
      } finally {
        this.cargando = false
      }
    },

    async registrar(data) {
      this.error = null

      if (data.password !== data.confirmPassword) {
        this.error = '❌ Las contraseñas no coinciden'
        return
      }

      if (data.password.length < 6) {
        this.error = '❌ La contraseña debe tener al menos 6 caracteres'
        return
      }

      this.cargando = true

      try {
        const response = await fetch('http://localhost:5000/api/auth/registro', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            nombre: data.nombre,
            email: data.email,
            password: data.password
          })
        })

        const result = await response.json()

        if (response.ok && result.success) {
          this.$emit('login', {
            token: result.token,
            usuario: result.usuario
          })
          this.limpiarFormularios()
        } else {
          this.error = result.error || '❌ Error al registrar usuario'
        }
      } catch (err) {
        console.error('Error en registro:', err)
        this.error = '❌ Error de conexión. ¿El servidor está corriendo?'
      } finally {
        this.cargando = false
      }
    },

    limpiarFormularios() {
      this.error = null
      if (this.$refs.loginForm) {
        this.$refs.loginForm.clear()
      }
      if (this.$refs.registerForm) {
        this.$refs.registerForm.clear()
      }
    }
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 1rem;
  animation: fadeIn 0.5s ease;
}

.auth-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  width: 100%;
  max-width: 450px;
  animation: slideIn 0.5s ease;
}

.auth-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.5rem;
  border-radius: 16px;
}

.tab {
  flex: 1;
  padding: 0.875rem;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab.active {
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  color: white;
  box-shadow: 0 4px 16px rgba(156, 39, 176, 0.3);
}

.auth-note {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.auth-note p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .auth-card {
    padding: 1.5rem;
  }
}
</style>
