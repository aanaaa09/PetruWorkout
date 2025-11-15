<template>
  <div class="game-tablero">
    <h2>🎲 Modo Tablero - En construcción</h2>

    <div class="info-partida">
      <p>Partida ID: {{ partidaId }}</p>
      <p>Playlist: {{ playlist }}</p>
      <p>Tipo: {{ configuracion.tipo_juego }}</p>
    </div>

    <button class="btn btn-volver" @click="$emit('volver')">
      ← Volver al menú
    </button>
  </div>
</template>

<script>
export default {
  name: 'GameTablero',
  props: {
    partidaId: {
      type: Number,
      required: true
    },
    configuracion: {
      type: Object,
      required: true
    },
    playlist: {
      type: String,
      required: true
    }
  }
}
</script>

<style scoped>
.game-tablero {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  text-align: center;
}

.game-tablero h2 {
  color: white;
  margin-bottom: 2rem;
}

.info-partida {
  background: rgba(0, 0, 0, 0.2);
  padding: 1.5rem;
  border-radius: 16px;
  margin-bottom: 2rem;
}

.info-partida p {
  color: white;
  margin: 0.5rem 0;
  font-size: 1.1rem;
}
</style>
