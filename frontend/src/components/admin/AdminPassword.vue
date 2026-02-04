<template>
  <div class="admin-password">
    <div class="password-header">
      <h2>🔐 Cambiar Contraseña</h2>
      <p>Modifica tu contraseña de acceso al panel</p>
    </div>

    <div class="password-content">
      <form @submit.prevent="handleChangePassword" class="password-form">
        <div class="form-group">
          <label>Contraseña Actual</label>
          <div class="password-input">
            <input
              v-model="currentPassword"
              :type="showCurrent ? 'text' : 'password'"
              placeholder="••••••••"
              required
              :disabled="loading"
            />
            <button
              type="button"
              class="toggle-password"
              @click="showCurrent = !showCurrent"
              :disabled="loading"
            >
              {{ showCurrent ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label>Nueva Contraseña</label>
          <div class="password-input">
            <input
              v-model="newPassword"
              :type="showNew ? 'text' : 'password'"
              placeholder="••••••••"
              required
              minlength="6"
              :disabled="loading"
            />
            <button
              type="button"
              class="toggle-password"
              @click="showNew = !showNew"
              :disabled="loading"
            >
              {{ showNew ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <span class="hint">Mínimo 6 caracteres</span>
        </div>

        <div class="form-group">
          <label>Confirmar Nueva Contraseña</label>
          <div class="password-input">
            <input
              v-model="confirmPassword"
              :type="showConfirm ? 'text' : 'password'"
              placeholder="••••••••"
              required
              :disabled="loading"
            />
            <button
              type="button"
              class="toggle-password"
              @click="showConfirm = !showConfirm"
              :disabled="loading"
            >
              {{ showConfirm ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>

        <div v-if="error" class="error-message">
          ❌ {{ error }}
        </div>

        <div v-if="success" class="success-message">
          ✅ {{ success }}
        </div>

        <button
          type="submit"
          class="btn-submit"
          :disabled="loading || !isFormValid"
        >
          {{ loading ? '⏳ Guardando...' : '💾 Cambiar Contraseña' }}
        </button>
      </form>

      <div class="security-tips">
        <h3>💡 Consejos de Seguridad</h3>
        <ul>
          <li>Usa al menos 8 caracteres</li>
          <li>Combina letras mayúsculas y minúsculas</li>
          <li>Incluye números y símbolos</li>
          <li>No uses información personal</li>
          <li>Cambia tu contraseña periódicamente</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminPassword',
  data() {
    return {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
      showCurrent: false,
      showNew: false,
      showConfirm: false,
      loading: false,
      error: '',
      success: ''
    }
  },
  computed: {
    isFormValid() {
      return this.newPassword.length >= 6 &&
             this.newPassword === this.confirmPassword
    }
  },
  methods: {
    async handleChangePassword() {
      this.error = ''
      this.success = ''

      // Validar que las contraseñas coincidan
      if (this.newPassword !== this.confirmPassword) {
        this.error = 'Las contraseñas no coinciden'
        return
      }

      // Validar longitud mínima
      if (this.newPassword.length < 6) {
        this.error = 'La contraseña debe tener al menos 6 caracteres'
        return
      }

      this.loading = true

      try {
        const token = localStorage.getItem('admin_token')

        const response = await fetch('https://petruworkout-production.up.railway.app/api/admin/change-password', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'token': token
          },
          body: JSON.stringify({
            current_password: this.currentPassword,
            new_password: this.newPassword
          })
        })

        const data = await response.json()

        if (response.ok && data.success) {
          this.success = 'Contraseña actualizada correctamente'
          this.currentPassword = ''
          this.newPassword = ''
          this.confirmPassword = ''
          this.showCurrent = false
          this.showNew = false
          this.showConfirm = false
        } else {
          this.error = data.detail || 'Error al cambiar la contraseña'
        }
      } catch (error) {
        console.error('Error:', error)
        this.error = 'Error de conexión. Intenta de nuevo.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.admin-password {
  max-width: 800px;
  margin: 0 auto;
}

.password-header {
  margin-bottom: 2rem;
}

.password-header h2 {
  font-size: 2rem;
  color: white;
  margin: 0 0 0.5rem 0;
}

.password-header p {
  color: var(--color-text-muted);
  font-size: 1rem;
  margin: 0;
}

.password-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.password-form {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.password-input {
  position: relative;
}

.password-input input {
  width: 100%;
  padding: 1rem;
  padding-right: 3rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.password-input input:focus {
  outline: none;
  border-color: var(--color-accent);
  background: rgba(255, 255, 255, 0.08);
}

.password-input input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-password {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  transition: all 0.3s ease;
}

.toggle-password:hover:not(:disabled) {
  transform: translateY(-50%) scale(1.1);
}

.toggle-password:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hint {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.error-message {
  padding: 1rem;
  background: rgba(239, 35, 60, 0.15);
  border: 1px solid rgba(239, 35, 60, 0.3);
  border-radius: 10px;
  color: #ff6b6b;
  font-weight: 600;
  text-align: center;
}

.success-message {
  padding: 1rem;
  background: rgba(6, 214, 160, 0.15);
  border: 1px solid rgba(6, 214, 160, 0.3);
  border-radius: 10px;
  color: var(--color-accent);
  font-weight: 600;
  text-align: center;
}

.btn-submit {
  padding: 1.25rem 2rem;
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.6);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.security-tips {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
}

.security-tips h3 {
  font-size: 1.25rem;
  color: white;
  margin: 0 0 1rem 0;
}

.security-tips ul {
  margin: 0;
  padding-left: 1.5rem;
  color: var(--color-text-secondary);
  line-height: 2;
}

.security-tips li {
  margin-bottom: 0.5rem;
}

@media (max-width: 640px) {
  .password-header h2 {
    font-size: 1.5rem;
  }

  .password-form,
  .security-tips {
    padding: 1.5rem;
  }
}
</style>
