<template>
  <div class="team-view">
    <SimpleNavbar />

    <div class="team-container">
      <div class="team-content">
        <!-- Header -->
        <div class="team-header">
          <div class="success-icon">🎉</div>
          <h1>¡Bienvenido al equipo!</h1>
        </div>

        <div class="email-reminder">
          <div class="reminder-icon">📧</div>
          <div class="reminder-content">
            <h3>¡No olvides revisar tu correo!</h3>
            <p>
              ¡Ey, te acabo de escribir! 📩<br><br>
              Te he enviado un email con acceso a tu <strong>calculadora de calorías personalizada</strong>.
              A partir de ahora te iré enseñando cómo ponerte en forma con calistenia, de manera simple y sin complicaciones.<br><br>
              Si no ves el email, revisa la carpeta de <strong>spam</strong> o <strong>promociones</strong> 😉
            </p>
          </div>
        </div>

        <!-- CTA Principal -->
        <div class="cta-section">
          <a
            href="https://chat.whatsapp.com/EPtwBr6DqUk0Y9kfUF0YB1"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-whatsapp-main"
            @click="trackWhatsAppClick"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
            </svg>
            UNIRME AL GRUPO DE WHATSAPP
          </a>

          <p class="privacy-note">
            🔒 Tu privacidad está protegida. Solo miembros del grupo pueden ver tu número.
          </p>
        </div>

        <!-- Beneficios del grupo -->
        <div class="benefits-section">
          <h2>🎁 Lo que encontrarás en el grupo:</h2>
          <div class="benefits-grid">
            <div class="benefit-card">
              <span class="benefit-icon">💪</span>
              <h3>Rutinas Exclusivas</h3>
              <p>Acceso a entrenamientos que no están en ningún otro lugar</p>
            </div>

            <div class="benefit-card">
              <span class="benefit-icon">🍎</span>
              <h3>Tips de Nutrición</h3>
              <p>Consejos semanales para optimizar tu alimentación</p>
            </div>

            <div class="benefit-card">
              <span class="benefit-icon">👥</span>
              <h3>Comunidad Activa</h3>
              <p>Comparte tu progreso y motiva a otros</p>
            </div>

            <div class="benefit-card">
              <span class="benefit-icon">📹</span>
              <h3>Contenido Premium</h3>
              <p>Videos y tutoriales antes que nadie</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <SimpleFooter />
  </div>
</template>

<script>
import SimpleNavbar from '@/components/navigation/SimpleNavbar.vue'
import SimpleFooter from '@/components/navigation/SimpleFooter.vue'

export default {
  name: 'TeamView',
  components: {
    SimpleNavbar,
    SimpleFooter
  },
  methods: {
    trackWhatsAppClick() {
      // Tracking del click al grupo de WhatsApp
      console.log('🎯 Usuario accediendo al grupo de WhatsApp')
    }
  }
}
</script>

<style scoped>
.team-view {
  min-height: 100vh;
  background: var(--bg-primary);
}

.team-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 8rem 2rem 4rem;
}

.team-content {
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

/* ===== HEADER ===== */
.team-header {
  text-align: center;
}

.success-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: bounce 2s infinite;
}

.team-header h1 {
  font-size: 3rem;
  font-weight: 900;
  color: white;
  margin: 0 0 1rem 0;
  background: linear-gradient(135deg, var(--color-accent) 0%, #4dffb8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  max-width: 700px;
  margin: 0 auto;
}

/* ===== NUEVO: RECORDATORIO DE EMAIL ===== */
.email-reminder {
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.15) 0%, rgba(6, 214, 160, 0.08) 100%);
  border: 2px solid rgba(6, 214, 160, 0.3);
  border-radius: 20px;
  padding: 2.5rem;
  display: flex;
  align-items: flex-start;
  gap: 2rem;
  animation: fadeIn 0.5s ease;
}

.reminder-icon {
  font-size: 3.5rem;
  flex-shrink: 0;
  animation: pulse 2s infinite;
}

.reminder-content {
  flex: 1;
}

.reminder-content h3 {
  font-size: 1.5rem;
  color: white;
  margin: 0 0 1rem 0;
  font-weight: 700;
}

.reminder-content p {
  font-size: 1.05rem;
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin: 0 0 1.5rem 0;
}

.reminder-content strong {
  color: var(--color-accent);
  font-weight: 700;
}

.btn-calculator-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: var(--gradient-primary);
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(6, 214, 160, 0.3);
}

.btn-calculator-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.5);
}

/* ===== BENEFICIOS ===== */
.benefits-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  padding: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.benefits-section h2 {
  font-size: 2rem;
  color: white;
  text-align: center;
  margin: 0 0 2rem 0;
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.benefit-card {
  background: rgba(255, 255, 255, 0.05);
  padding: 2rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.benefit-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-5px);
  border-color: var(--color-accent);
}

.benefit-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.benefit-card h3 {
  font-size: 1.25rem;
  color: white;
  margin: 0 0 0.5rem 0;
}

.benefit-card p {
  font-size: 0.95rem;
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.5;
}

/* ===== CTA PRINCIPAL ===== */
.cta-section {
  text-align: center;
  background: linear-gradient(135deg, rgba(37, 211, 102, 0.15) 0%, rgba(18, 140, 126, 0.1) 100%);
  border: 2px solid rgba(37, 211, 102, 0.3);
  border-radius: 20px;
  padding: 3rem 2rem;
}

.intro-text {
  font-size: 1.2rem;
  font-weight: 600;
  color: white;
  margin: 0 0 2rem 0;
  line-height: 1.6;
}

.btn-whatsapp-main {
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 3rem;
  background: linear-gradient(135deg, #25D366, #128C7E);
  color: white;
  text-decoration: none;
  border-radius: 16px;
  font-weight: 800;
  font-size: 1.25rem;
  transition: all 0.3s ease;
  box-shadow: 0 10px 40px rgba(37, 211, 102, 0.4);
  border: none;
  cursor: pointer;
}

.btn-whatsapp-main:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 50px rgba(37, 211, 102, 0.6);
  background: linear-gradient(135deg, #2ce878, #15a589);
}

.btn-whatsapp-main svg {
  width: 28px;
  height: 28px;
}

.privacy-note {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin-top: 1.5rem;
}

/* ===== ANIMACIONES ===== */
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
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

/* ===== RESPONSIVE ===== */
@media (max-width: 968px) {
  .team-container {
    padding: 6rem 1.5rem 3rem;
  }

  .team-header h1 {
    font-size: 2.25rem;
  }

  .benefits-grid {
    grid-template-columns: 1fr;
  }

  .email-reminder {
    flex-direction: column;
    text-align: center;
    padding: 2rem;
  }

  .reminder-icon {
    font-size: 3rem;
  }
}

@media (max-width: 640px) {
  .success-icon {
    font-size: 4rem;
  }

  .team-header h1 {
    font-size: 1.75rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .email-reminder {
    padding: 1.5rem;
  }

  .reminder-content h3 {
    font-size: 1.25rem;
  }

  .reminder-content p {
    font-size: 0.95rem;
  }

  .btn-calculator-link {
    width: 100%;
    justify-content: center;
  }

  .benefits-section {
    padding: 2rem 1.5rem;
  }

  .cta-section {
    padding: 2rem 1.5rem;
  }

  .intro-text {
    font-size: 1rem;
  }

  .btn-whatsapp-main {
    width: 100%;
    justify-content: center;
    font-size: 1rem;
    padding: 1.25rem 2rem;
  }

  .btn-whatsapp-main svg {
    width: 24px;
    height: 24px;
  }
}
</style>
