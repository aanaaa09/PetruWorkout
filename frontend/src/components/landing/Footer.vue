<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-links">
        <a href="#" class="footer-link">Políticas de Privacidad</a>
        <span class="separator">•</span>
        <a href="#" class="footer-link">Aviso Legal</a>
      </div>

      <div class="footer-credits">
        Desarrollado por
        <a
          href="https://linkedin.com/in/ana-seseña-4290891bb"
          target="_blank"
          rel="noopener noreferrer"
          class="dev-link"
        >
          Ana Seseña
        </a>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer'
}
</script>

<style scoped>
.app-footer {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 2rem;
  margin-top: auto;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.footer-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: white;
}

.separator {
  color: rgba(255, 255, 255, 0.4);
}

.footer-credits {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  text-align: center;
}

.dev-link {
  color: #9c27b0;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.dev-link:hover {
  color: #673ab7;
  text-decoration: underline;
}

@media (max-width: 480px) {
  .footer-links {
    flex-direction: column;
    gap: 0.5rem;
  }

  .separator {
    display: none;
  }
}
</style>
