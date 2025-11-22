<script setup>
<template>
  <section class="contact-section">
    <div class="contact-container">
      <div class="contact-header">
        <h2>💬 ¿Tienes dudas o sugerencias?</h2>
        <p>Envíame tu consulta y te responderé lo antes posible</p>
      </div>

      <form @submit.prevent="enviarConsulta" class="contact-form">
        <div class="form-row">
          <div class="form-group">
            <label>Nombre</label>
            <input
              v-model="form.nombre"
              type="text"
              placeholder="Tu nombre completo"
              required
            />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input
              v-model="form.email"
              type="email"
              placeholder="tu@email.com"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label>Asunto</label>
          <input
            v-model="form.asunto"
            type="text"
            placeholder="¿Sobre qué quieres hablar?"
            required
          />
        </div>

        <div class="form-group">
          <label>Mensaje</label>
          <textarea
            v-model="form.mensaje"
            placeholder="Cuéntame tu duda o sugerencia..."
            rows="5"
            required
          ></textarea>
        </div>

        <button
          type="submit"
          class="btn-submit"
          :disabled="enviando"
        >
          {{ enviando ? '📤 Enviando...' : '📧 Enviar Mensaje' }}
        </button>

        <div v-if="mensajeExito" class="mensaje-exito">
          ✅ {{ mensajeExito }}
        </div>

        <div v-if="mensajeError" class="mensaje-error">
          ❌ {{ mensajeError }}
        </div>
      </form>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ContactForm',
  data() {
    return {
      form: {
        nombre: '',
        email: '',
        asunto: '',
        mensaje: ''
      },
      enviando: false,
      mensajeExito: '',
      mensajeError: ''
    }
  },
  methods: {
    async enviarConsulta() {
      this.enviando = true
      this.mensajeExito = ''
      this.mensajeError = ''

      try {
        const response = await fetch('http://localhost:5000/api/consultas/enviar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        })

        const data = await response.json()

        if (response.ok && data.success) {
          this.mensajeExito = 'Mensaje enviado correctamente. Te responderé pronto.'
          this.limpiarFormulario()
        } else {
          this.mensajeError = data.error || 'Error al enviar el mensaje'
        }
      } catch (error) {
        this.mensajeError = 'Error de conexión. Intenta de nuevo.'
      } finally {
        this.enviando = false
      }
    },

    limpiarFormulario() {
      this.form = {
        nombre: '',
        email: '',
        asunto: '',
        mensaje: ''
      }
    }
  }
}
</script>

<style scoped>
.contact-section {
  padding: 6rem 2rem;
}

.contact-container {
  max-width: 800px;
  margin: 0 auto;
}

.contact-header {
  text-align: center;
  margin-bottom: 3rem;
}

.contact-header h2 {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  margin-bottom: 1rem;
}

.contact-header p {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
}

.contact-form {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: white;
  font-size: 0.95rem;
}

.form-group input,
.form-group textarea {
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #9c27b0;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 4px rgba(156, 39, 176, 0.2);
}

.btn-submit {
  padding: 1.25rem 2rem;
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(156, 39, 176, 0.4);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(156, 39, 176, 0.6);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.mensaje-exito {
  background: rgba(0, 200, 81, 0.2);
  border: 1px solid rgba(0, 200, 81, 0.5);
  color: #00ff6b;
  padding: 1rem;
  border-radius: 12px;
  text-align: center;
  font-weight: 600;
}

.mensaje-error {
  background: rgba(231, 76, 60, 0.2);
  border: 1px solid rgba(231, 76, 60, 0.5);
  color: #ff6b6b;
  padding: 1rem;
  border-radius: 12px;
  text-align: center;
  font-weight: 600;
}

@media (max-width: 768px) {
  .contact-section {
    padding: 4rem 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .contact-form {
    padding: 1.5rem;
  }
}
</style>
