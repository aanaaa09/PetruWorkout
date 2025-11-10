<template>
  <form @submit.prevent="handleSubmit" class="auth-form">
    <h2>🎉 Crea tu cuenta</h2>

    <div class="form-group">
      <label>👤 Nombre</label>
      <input
        v-model="nombre"
        type="text"
        placeholder="Tu nombre"
        required
        minlength="2"
        :disabled="loading"
      />
    </div>

    <div class="form-group">
      <label>📧 Email</label>
      <input
        v-model="email"
        type="email"
        placeholder="tu@email.com"
        required
        :disabled="loading"
      />
    </div>

    <div class="form-group">
      <label>🔒 Contraseña</label>
      <input
        v-model="password"
        type="password"
        placeholder="Mínimo 6 caracteres"
        required
        minlength="6"
        :disabled="loading"
      />
    </div>

    <div class="form-group">
      <label>🔒 Confirmar Contraseña</label>
      <input
        v-model="confirmPassword"
        type="password"
        placeholder="Repite tu contraseña"
        required
        :disabled="loading"
      />
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <button type="submit" class="btn btn-submit" :disabled="loading">
      <span v-if="loading">⏳ Creando cuenta...</span>
      <span v-else>Crear Cuenta</span>
    </button>
  </form>
</template>

<script>
export default {
  props: {
    loading: Boolean,
    error: String
  },
  data() {
    return {
      nombre: '',
      email: '',
      password: '',
      confirmPassword: ''
    }
  },
  methods: {
    handleSubmit() {
      this.$emit('submit', {
        nombre: this.nombre,
        email: this.email,
        password: this.password,
        confirmPassword: this.confirmPassword
      })
    },
    clear() {
      this.nombre = ''
      this.email = ''
      this.password = ''
      this.confirmPassword = ''
    }
  }
}
</script>

<style scoped>
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.auth-form h2 {
  font-size: 1.75rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 0.5rem;
  background: linear-gradient(45deg, #ffffff, #ddddff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.9);
}

.form-group input {
  padding: 0.875rem 1rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-group input:focus {
  outline: none;
  border-color: #9c27b0;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(156, 39, 176, 0.1);
}

.error-message {
  padding: 0.875rem;
  background: rgba(231, 76, 60, 0.2);
  border: 1px solid rgba(231, 76, 60, 0.4);
  border-radius: 12px;
  color: #ff6b6b;
  font-weight: 600;
  text-align: center;
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.btn-submit {
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  color: white;
  padding: 1rem;
  font-size: 1rem;
  font-weight: 700;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 32px rgba(156, 39, 176, 0.3);
  margin-top: 0.5rem;
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(156, 39, 176, 0.4);
}

.btn-submit:active {
  transform: translateY(0);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
</style>
