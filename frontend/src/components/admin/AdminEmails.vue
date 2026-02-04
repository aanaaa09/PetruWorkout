<template>
  <div class="admin-emails">
    <div class="emails-header">
      <h2>📧 Enviar Emails</h2>
      <p>Envía emails a tus usuarios suscritos a la newsletter</p>
    </div>

    <div class="emails-content">
      <!-- Formulario de email -->
      <form @submit.prevent="handleSendEmail" class="email-form">
        <div class="form-section">
          <h3>📝 Contenido del Email</h3>

          <div class="form-group">
            <label>Asunto</label>
            <input
              v-model="subject"
              type="text"
              placeholder="Ej: Nuevos entrenamientos disponibles"
              required
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label>Mensaje</label>
            <textarea
              v-model="message"
              rows="10"
              placeholder="Escribe el contenido del email aquí..."
              required
              :disabled="loading"
            ></textarea>
            <span class="hint">El mensaje se enviará en formato HTML con el template de la marca</span>
          </div>
        </div>

        <div class="form-section">
          <h3>👥 Destinatarios</h3>

          <div class="recipients-options">
            <label class="radio-option">
              <input
                type="radio"
                v-model="sendTo"
                value="all"
                :disabled="loading"
              />
              <div class="option-content">
                <span class="option-title">📢 Todos los suscriptores</span>
                <span class="option-desc">Enviar a todos los usuarios de la newsletter</span>
              </div>
            </label>

            <label class="radio-option">
              <input
                type="radio"
                v-model="sendTo"
                value="selected"
                :disabled="loading"
              />
              <div class="option-content">
                <span class="option-title">🎯 Usuarios específicos</span>
                <span class="option-desc">Selecciona manualmente los destinatarios</span>
              </div>
            </label>
          </div>

          <!-- Selector de usuarios (solo si sendTo === 'selected') -->
          <div v-if="sendTo === 'selected'" class="users-selector">
            <button
              type="button"
              @click="loadUsers"
              class="btn-load-users"
              :disabled="loadingUsers"
            >
              {{ loadingUsers ? '⏳ Cargando...' : '👥 Cargar Lista de Usuarios' }}
            </button>

            <div v-if="users.length > 0" class="users-list">
              <div class="users-list-header">
                <input
                  type="checkbox"
                  @change="toggleAllUsers"
                  :checked="allUsersSelected"
                />
                <span>Seleccionar todos ({{ users.length }})</span>
              </div>

              <div class="users-items">
                <label
                  v-for="user in users"
                  :key="user.id"
                  class="user-item"
                >
                  <input
                    type="checkbox"
                    :value="user.id"
                    v-model="selectedUserIds"
                  />
                  <div class="user-info">
                    <span class="user-name">{{ user.nombre }}</span>
                    <span class="user-email">{{ user.email }}</span>
                  </div>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Adjuntos -->
        <div class="form-section">
          <h3>📎 Adjuntos (Opcional)</h3>

          <div class="file-upload">
            <input
              type="file"
              ref="fileInput"
              @change="handleFileSelect"
              multiple
              accept=".pdf,.jpg,.jpeg,.png,.gif"
              :disabled="loading"
              style="display: none;"
            />

            <button
              type="button"
              @click="$refs.fileInput.click()"
              class="btn-upload"
              :disabled="loading"
            >
              📁 Seleccionar Archivos
            </button>

            <span class="hint">PDF, imágenes (máx 5MB cada uno)</span>
          </div>

          <!-- Lista de archivos seleccionados -->
          <div v-if="attachments.length > 0" class="attachments-list">
            <div
              v-for="(file, index) in attachments"
              :key="index"
              class="attachment-item"
            >
              <span class="attachment-name">{{ file.name }}</span>
              <span class="attachment-size">{{ formatFileSize(file.size) }}</span>
              <button
                type="button"
                @click="removeAttachment(index)"
                class="btn-remove"
                :disabled="loading"
              >
                ✕
              </button>
            </div>
          </div>
        </div>

        <!-- Mensajes -->
        <div v-if="error" class="error-message">
          ❌ {{ error }}
        </div>

        <div v-if="success" class="success-message">
          ✅ {{ success }}
        </div>

        <!-- Botón de envío -->
        <button
          type="submit"
          class="btn-send"
          :disabled="loading || !canSend"
        >
          {{ loading ? '📤 Enviando...' : '📧 Enviar Email' }}
        </button>

        <!-- Confirmación de envío -->
        <div v-if="showConfirmation" class="confirmation-summary">
          <p>
            <strong>⚠️ ¿Estás seguro?</strong><br>
            {{ confirmationMessage }}
          </p>
          <div class="confirmation-buttons">
            <button
              type="button"
              @click="confirmSend"
              class="btn-confirm"
              :disabled="loading"
            >
              ✅ Confirmar y Enviar
            </button>
            <button
              type="button"
              @click="showConfirmation = false"
              class="btn-cancel"
              :disabled="loading"
            >
              ❌ Cancelar
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminEmails',
  data() {
    return {
      subject: '',
      message: '',
      sendTo: 'all',
      users: [],
      selectedUserIds: [],
      attachments: [],
      loading: false,
      loadingUsers: false,
      error: '',
      success: '',
      showConfirmation: false
    }
  },
  computed: {
    canSend() {
      const hasContent = this.subject && this.message
      const hasRecipients = this.sendTo === 'all' || this.selectedUserIds.length > 0
      return hasContent && hasRecipients && !this.showConfirmation
    },
    allUsersSelected() {
      return this.users.length > 0 && this.selectedUserIds.length === this.users.length
    },
    confirmationMessage() {
      if (this.sendTo === 'all') {
        return 'Vas a enviar este email a TODOS los usuarios suscritos a la newsletter.'
      } else {
        return `Vas a enviar este email a ${this.selectedUserIds.length} usuario(s) seleccionado(s).`
      }
    }
  },
  methods: {
    async loadUsers() {
      this.loadingUsers = true
      this.error = ''

      try {
        const token = localStorage.getItem('admin_token')

        const response = await fetch('https://petruworkout-production.up.railway.app/api/admin/users?tipo=newsletter&limit=1000', {
          headers: { 'token': token }
        })

        const data = await response.json()

        if (response.ok && data.success) {
          this.users = data.usuarios
        } else {
          this.error = 'Error al cargar usuarios'
        }
      } catch (error) {
        console.error('Error:', error)
        this.error = 'Error de conexión al cargar usuarios'
      } finally {
        this.loadingUsers = false
      }
    },

    toggleAllUsers(event) {
      if (event.target.checked) {
        this.selectedUserIds = this.users.map(u => u.id)
      } else {
        this.selectedUserIds = []
      }
    },

    handleFileSelect(event) {
      const files = Array.from(event.target.files)
      const maxSize = 5 * 1024 * 1024 // 5MB

      for (const file of files) {
        if (file.size > maxSize) {
          this.error = `El archivo "${file.name}" supera los 5MB`
          return
        }
      }

      this.attachments = [...this.attachments, ...files]
    },

    removeAttachment(index) {
      this.attachments.splice(index, 1)
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    },

    handleSendEmail(event) {
      event.preventDefault()
      this.error = ''
      this.success = ''
      this.showConfirmation = true
    },

    async confirmSend() {
      this.loading = true
      this.error = ''
      this.success = ''

      try {
        const token = localStorage.getItem('admin_token')
        const formData = new FormData()

        formData.append('subject', this.subject)
        formData.append('message', this.message)
        formData.append('send_to', this.sendTo)

        if (this.sendTo === 'selected') {
          formData.append('selected_ids', this.selectedUserIds.join(','))
        }

        // Adjuntar archivos
        this.attachments.forEach((file, index) => {
          formData.append('attachments', file)
        })

        const response = await fetch('https://petruworkout-production.up.railway.app/api/admin/send-email', {
          method: 'POST',
          headers: { 'token': token },
          body: formData
        })

        const data = await response.json()

        if (response.ok && data.success) {
          this.success = `Email enviado correctamente a ${data.enviados} usuario(s). ${data.errores > 0 ? `${data.errores} error(es).` : ''}`
          this.resetForm()
        } else {
          this.error = data.detail || 'Error al enviar emails'
        }
      } catch (error) {
        console.error('Error:', error)
        this.error = 'Error de conexión al enviar emails'
      } finally {
        this.loading = false
        this.showConfirmation = false
      }
    },

    resetForm() {
      this.subject = ''
      this.message = ''
      this.sendTo = 'all'
      this.selectedUserIds = []
      this.attachments = []
      this.users = []
    }
  }
}
</script>

<style scoped>
.admin-emails {
  max-width: 1000px;
  margin: 0 auto;
}

.emails-header {
  margin-bottom: 2rem;
}

.emails-header h2 {
  font-size: 2rem;
  color: white;
  margin: 0 0 0.5rem 0;
}

.emails-header p {
  color: var(--color-text-muted);
  font-size: 1rem;
  margin: 0;
}

.email-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
}

.form-section h3 {
  font-size: 1.25rem;
  color: white;
  margin: 0 0 1.5rem 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.form-group input,
.form-group textarea {
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  background: rgba(255, 255, 255, 0.08);
}

.form-group input:disabled,
.form-group textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-group textarea {
  resize: vertical;
  min-height: 200px;
}

.hint {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.recipients-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.radio-option {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.radio-option:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.radio-option input[type="radio"] {
  margin-top: 0.25rem;
  accent-color: var(--color-accent);
}

.option-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.option-title {
  color: white;
  font-weight: 600;
}

.option-desc {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.users-selector {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-load-users {
  padding: 1rem 1.5rem;
  background: rgba(6, 214, 160, 0.2);
  border: 1px solid var(--color-accent);
  border-radius: 10px;
  color: var(--color-accent);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-load-users:hover:not(:disabled) {
  background: rgba(6, 214, 160, 0.3);
}

.btn-load-users:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.users-list {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
}

.users-list-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  font-weight: 600;
}

.users-items {
  max-height: 400px;
  overflow-y: auto;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.user-item:last-child {
  border-bottom: none;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  color: white;
  font-weight: 500;
}

.user-email {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.file-upload {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.btn-upload {
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-upload:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--color-accent);
}

.btn-upload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}

.attachment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.attachment-name {
  color: white;
  font-weight: 500;
}

.attachment-size {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.btn-remove {
  background: rgba(239, 35, 60, 0.2);
  border: 1px solid rgba(239, 35, 60, 0.4);
  border-radius: 6px;
  color: #ff6b6b;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-remove:hover:not(:disabled) {
  background: rgba(239, 35, 60, 0.3);
}

.btn-remove:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.btn-send {
  padding: 1.25rem 2rem;
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
}

.btn-send:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.6);
}

.btn-send:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.confirmation-summary {
  background: rgba(255, 193, 7, 0.15);
  border: 2px solid rgba(255, 193, 7, 0.4);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.confirmation-summary p {
  color: white;
  margin: 0 0 1.5rem 0;
  line-height: 1.6;
}

.confirmation-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-confirm,
.btn-cancel {
  padding: 1rem 2rem;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-confirm {
  background: var(--gradient-primary);
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-cancel {
  background: rgba(239, 35, 60, 0.2);
  border: 1px solid rgba(239, 35, 60, 0.4);
  color: #ff6b6b;
}

.btn-cancel:hover:not(:disabled) {
  background: rgba(239, 35, 60, 0.3);
}

.btn-confirm:disabled,
.btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .emails-header h2 {
    font-size: 1.5rem;
  }

  .form-section {
    padding: 1.5rem;
  }

  .confirmation-buttons {
    flex-direction: column;
  }

  .btn-confirm,
  .btn-cancel {
    width: 100%;
  }
}
</style>
