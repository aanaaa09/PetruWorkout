<template>
  <div class="controls-wrapper">
    <!-- Botones de acción durante el juego -->
    <div class="action-buttons" v-if="!yaRespondido">
      <button class="btn btn-verificar" @click="$emit('verificar')">
        ✅ Verificar
      </button>
      <button class="btn btn-rendirse" @click="$emit('rendirse')">
        🏳️ Rendirse
      </button>
    </div>

    <!-- Botón siguiente (solo si ya respondió y la ronda NO terminó) -->
    <div class="navigation-controls" v-if="yaRespondido && !rondaTerminada">
      <button class="btn btn-siguiente" @click="$emit('siguiente')">
        ➡️ Siguiente Pregunta
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    yaRespondido: {
      type: Boolean,
      default: false
    },
    rondaTerminada: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.controls-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.navigation-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .action-buttons,
  .navigation-controls {
    gap: 0.75rem;
  }
}

@media (max-width: 480px) {
  .action-buttons,
  .navigation-controls {
    gap: 0.5rem;
    flex-direction: column;
  }

  .action-buttons .btn,
  .navigation-controls .btn {
    width: 100%;
    max-width: 280px;
  }
}
</style>
