<template>
  <div class="modos-columna">
    <h2 class="modos-titulo">🎮 Modo de Juego</h2>

    <div class="modos-lista">
      <button
        @click="$emit('select', 'individual')"
        :class="['modo-card', { selected: modoSeleccionado === 'individual' }]"
      >
        <div class="modo-icon">🎵</div>
        <div class="modo-info">
          <h3>Individual</h3>
          <p>A tu ritmo</p>
        </div>
      </button>

      <button
        @click="$emit('select', 'tablero')"
        :class="['modo-card', { selected: modoSeleccionado === 'tablero' }]"
      >
        <div class="modo-icon">🎲</div>
        <div class="modo-info">
          <h3>Tablero</h3>
          <p>Con casillas</p>
        </div>
      </button>

      <button
        @click="$emit('select', 'online')"
        :class="['modo-card', { selected: modoSeleccionado === 'online' }]"
      >
        <div class="modo-icon">🌐</div>
        <div class="modo-info">
          <h3>Online</h3>
          <p>Multijugador</p>
        </div>
        <span class="badge-pronto">Pronto</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    modoSeleccionado: {
      type: String,
      default: null
    }
  }
}
</script>

<style scoped>
.modos-columna {
  width: 280px;
  flex-shrink: 0;
}

.modos-titulo {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-align: center;
  color: white;
}

.modos-lista {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.modo-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  text-align: left;
}

.modo-card:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateX(5px);
}

.modo-card.selected {
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.3), rgba(103, 58, 183, 0.3));
  border-color: #9c27b0;
  box-shadow: 0 8px 32px rgba(156, 39, 176, 0.3);
}

.modo-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.modo-info h3 {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
  color: white;
}

.modo-info p {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.badge-pronto {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: linear-gradient(135deg, #f39c12, #e67e22);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 700;
}

@media (max-width: 968px) {
  .modos-columna {
    width: 100%;
  }

  .modos-lista {
    flex-direction: row;
    overflow-x: auto;
  }

  .modo-card {
    min-width: 200px;
  }
}

@media (max-width: 480px) {
  .modo-card {
    min-width: 160px;
  }
}
</style>
