<template>
  <footer class="simple-footer">
    <div class="footer-container">
      <div class="footer-brand">
        <h3 class="logo">
          <span class="logo-accent">PETRU</span>WORKOUT
        </h3>
        <p>Entrenador personal especializado en calistenia y transformación física.</p>
      </div>

      <div class="footer-actions">
      <a
          href="https://calendly.com/petruworkout/reunion"
          target="_blank"
          rel="noopener noreferrer"
          class="btn btn-primary"
        >
          📅 Agendar Llamada Gratuita
        </a>
        <router-link to="/info" class="btn btn-secondary">
          📋 Más Información
        </router-link>
      </div>

      <div class="footer-legal">
        <button @click="$emit('show-legal', 'privacy')" class="legal-link">
          Política de Privacidad
        </button>
        <span class="separator">•</span>
        <button @click="$emit('show-legal', 'terms')" class="legal-link">
          Términos y Condiciones
        </button>
        <span class="separator">•</span>
        <button @click="$emit('show-legal', 'legal-notice')" class="legal-link">
          Aviso Legal
        </button>
      </div>

      <div class="footer-bottom">
        <p class="copyright">
          © {{ currentYear }} PetruWorkout. Todos los derechos reservados.
        </p>
        <p class="credits">
          Desarrollado por
          <a
            href="https://linkedin.com/in/ana-seseña-4290891bb"
            target="_blank"
            rel="noopener noreferrer"
          >
            Ana Seseña
          </a>
        </p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'SimpleFooter',
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
.simple-footer {
  background: rgba(0, 0, 0, 0.6);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding: 3rem 2rem 2rem;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.footer-brand {
  text-align: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 900;
  color: white;
  margin: 0 0 1rem 0;
}

.logo-accent {
  color: var(--color-accent);
}

.footer-brand p {
  color: var(--color-text-muted);
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0;
  max-width: 500px;
  margin: 0 auto;
}

.footer-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--gradient-primary);
  color: white;
  box-shadow: 0 4px 15px rgba(6, 214, 160, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(6, 214, 160, 0.5);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.footer-legal {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1.5rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.legal-link {
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  cursor: pointer;
  transition: color 0.3s ease;
  padding: 0;
  font-family: inherit;
}

.legal-link:hover {
  color: var(--color-accent);
  text-decoration: underline;
}

.separator {
  color: var(--color-text-muted);
  font-size: 0.8rem;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  flex-wrap: wrap;
  gap: 1rem;
}

.copyright,
.credits {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin: 0;
}

.credits a {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.credits a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .simple-footer {
    padding: 2rem 1rem;
  }

  .footer-actions {
    flex-direction: column;
    width: 100%;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .footer-legal {
    flex-direction: column;
    gap: 0.75rem;
  }

  .separator {
    display: none;
  }

  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
}
</style>
