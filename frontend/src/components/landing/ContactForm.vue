<template>
  <section id="contacto" class="contact-section">
    <div class="contact-container">
      <div class="contact-header">
        <span class="section-tag">CONTACTO</span>
        <h2>💬 ¿Tienes dudas o sugerencias?</h2>
        <p>Envíame tu consulta y te responderé lo antes posible</p>
      </div>

      <div class="contact-content">
        <div class="contact-info">
          <div class="info-item">
            <span class="info-icon">📧</span>
            <div>
              <h4>Email</h4>
              <p>petruworkout@gmail.com</p>
            </div>
          </div>

          <div class="info-item">
            <span class="info-icon">📱</span>
            <div>
              <h4>WhatsApp</h4>
              <p>Disponible para clientes</p>
            </div>
          </div>

          <div class="info-item">
            <span class="info-icon">⏰</span>
            <div>
              <h4>Tiempo de respuesta</h4>
              <p>24-48 horas</p>
            </div>
          </div>

          <div class="social-links">
            <a href="#" class="social-link" title="Instagram">
              <span>📷</span>
            </a>
            <a href="#" class="social-link" title="YouTube">
              <span>▶️</span>
            </a>
            <a href="#" class="social-link" title="TikTok">
              <span>🎵</span>
            </a>
          </div>
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
  background: var(--bg-primary);
}

.contact-container {
  max-width: 1100px;
  margin: 0 auto;
}

.contact-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-tag {
  font-size: 0.85rem;
  color: var(--color-accent);
  font-weight: 700;
  letter-spacing: 0.15em;
  display: block;
  margin-bottom: 1rem;
}

.contact-header h2 {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  margin: 0 0 1rem 0;
}

.contact-header p {
  font-size: 1.1rem;
  color: var(--color-text-muted);
}

.contact-content {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 4rem;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.info-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.info-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.info-item h4 {
  font-size: 1rem;
  color: white;
  margin: 0 0 0.25rem 0;
}

.info-item p {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin: 0;
}

.social-links {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.social-link {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  text-decoration: none;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.social-link:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-3px);
}

.contact-form {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: white;
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

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: var(--color-text-muted);
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  background: rgba(255, 255, 255, 0.08);
}

.btn-submit {
  padding: 1rem 2rem;
  background: var(--gradient-primary);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(230, 57, 70, 0.3);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(230, 57, 70, 0.5);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.mensaje-exito {
  background: rgba(6, 214, 160, 0.15);
  border: 1px solid rgba(6, 214, 160, 0.3);
  color: var(--color-success);
  padding: 1rem;
  border-radius: 10px;
  text-align: center;
  font-weight: 600;
}

.mensaje-error {
  background: rgba(239, 35, 60, 0.15);
  border: 1px solid rgba(239, 35, 60, 0.3);
  color: var(--color-error);
  padding: 1rem;
  border-radius: 10px;
  text-align: center;
  font-weight: 600;
}

@media (max-width: 968px) {
  .contact-content {
    grid-template-columns: 1fr;
    gap: 3rem;
  }

  .social-links {
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .contact-section {
    padding: 4rem 1rem;
  }

  .contact-header h2 {
    font-size: 2rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .contact-form {
    padding: 1.5rem;
  }
}
</style>
