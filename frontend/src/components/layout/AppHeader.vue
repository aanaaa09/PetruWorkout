<template>
  <header class="app-header">
    <div class="header-content">
      <h1 class="app-title">SongByte</h1>

      <div class="header-actions">
        <button
          class="btn-header"
          @click="abrirRanking"
          :disabled="!usuarioLogueado"
        >
          <span class="icon">🏆</span>
          Ranking
        </button>
        <button class="btn-header" @click="abrirAñadirCancion" disabled>
          <span class="icon">➕</span>
          Añadir Canción
        </button>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'AppHeader',
  props: {
    usuarioLogueado: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    abrirRanking() {
      if (this.usuarioLogueado) {
        this.$emit('mostrar-ranking')
      }
    },
    abrirAñadirCancion() {
      console.log('Añadir canción')
    }
  }
}
</script>

<style scoped>
.app-header {
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  padding: 1rem 0;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  position: relative;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.app-title {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, #e0c3fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-header:not(:disabled):hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.btn-header:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-header .icon {
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .app-header {
    padding: 0.875rem 0;
  }

  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
    padding: 0 1rem;
  }

  .app-title {
    font-size: 1.5rem;
    text-align: center;
  }

  .header-actions {
    justify-content: center;
    flex-wrap: wrap;
  }

  .btn-header {
    flex: 1;
    min-width: 140px;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0 0.75rem;
  }

  .app-title {
    font-size: 1.25rem;
  }

  .btn-header {
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
  }

  .btn-header .icon {
    font-size: 1rem;
  }
}
</style>
