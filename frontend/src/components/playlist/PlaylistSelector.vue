<template>
  <div class="selector-container">
    <ModeSelector
      :modo-seleccionado="modoSeleccionado"
      @select="seleccionarModo"
    />

    <div class="contenido-area">
      <div v-if="!modoSeleccionado" class="mensaje-inicial">
        <div class="mensaje-icono">🎮</div>
        <h2>Selecciona un modo de juego</h2>
        <p>Elige cómo quieres jugar desde el menú de la izquierda</p>
      </div>

      <!-- NUEVO: Instrucciones del Modo Individual (Rondas) -->
      <InstructionsCard
        v-else-if="modoSeleccionado === 'individual' && !playlistVisible"
        titulo="🎵 Juego Individual - Rondas"
        :show-continue="true"
        @close="volverModos"
        @continue="mostrarPlaylists"
      >
        <h3>📋 Cómo jugar:</h3>
        <ul>
          <li><strong>10 Preguntas:</strong> Cada ronda tiene 10 canciones</li>
          <li><strong>Dado Aleatorio:</strong> Se tira un dado que decide qué adivinar:
            <ul style="margin-top: 0.5rem; padding-left: 1rem;">
              <li>🎵 <strong>Título y Artista</strong> (2 pts cada uno)</li>
              <li>📅 <strong>Solo el Año</strong> (4 pts)</li>
              <li>🎤 <strong>Solo el Artista</strong> (2 pts)</li>
            </ul>
          </li>
          <li><strong>Racha de Aciertos:</strong> Respuestas correctas consecutivas suman bonus (+1 pt por cada una)</li>
          <li><strong>Puntuación Final:</strong> Al terminar la ronda, los puntos se suman a tu cuenta</li>
        </ul>

        <h3>💡 Consejos:</h3>
        <ul>
          <li>Mantén la racha para multiplicar tus puntos</li>
          <li>El sistema acepta variaciones en el título/artista</li>
          <li>Puedes rendirte si no sabes la respuesta</li>
        </ul>
      </InstructionsCard>

      <!-- NUEVO: Instrucciones Modo Tablero (Juego Clásico) -->
      <InstructionsCard
        v-else-if="modoSeleccionado === 'tablero' && !playlistVisible"
        titulo="🎲 Modo Tablero - Clásico"
        :show-continue="true"
        @close="volverModos"
        @continue="mostrarPlaylistsTablero"
      >
        <h3>📋 Cómo jugar:</h3>
        <ul>
          <li><strong>Escucha:</strong> Se reproducirá un fragmento de 30 segundos</li>
          <li><strong>Adivina:</strong> Escribe el título y artista de la canción</li>
          <li><strong>Verifica:</strong> No necesitas ser exacto, aceptamos similitudes</li>
          <li><strong>Juego Libre:</strong> Sin límite de canciones, juega a tu ritmo</li>
        </ul>

        <h3>💡 Consejos:</h3>
        <ul>
          <li>El sistema acepta variaciones en el título</li>
          <li>Si hay varios artistas, escribe al menos uno</li>
          <li>Puedes rendirte para ver la respuesta</li>
        </ul>
      </InstructionsCard>

      <!-- Modo Online sin cambios -->
      <InstructionsCard
        v-else-if="modoSeleccionado === 'online' && !playlistVisible"
        titulo="🌐 Modo Online"
        @close="volverModos"
      >
        <div class="proximamente-banner">
          <span>🚧 Próximamente disponible 🚧</span>
        </div>
        <!-- ... resto igual ... -->
      </InstructionsCard>

      <!-- Selector de Playlists para Individual -->
      <PlaylistGrid
        v-else-if="modoSeleccionado === 'individual' && playlistVisible"
        @back="volverInstrucciones"
        @select="selectIndividual"
      />

      <!-- Selector de Playlists para Tablero -->
      <PlaylistGrid
        v-else-if="modoSeleccionado === 'tablero' && playlistVisible"
        @back="volverInstrucciones"
        @select="selectTablero"
      />
    </div>
  </div>
</template>

<script>
import ModeSelector from './ModeSelector.vue'
import InstructionsCard from './InstructionsCard.vue'
import PlaylistGrid from './PlaylistGrid.vue'

export default {
  components: {
    ModeSelector,
    InstructionsCard,
    PlaylistGrid
  },
  data() {
    return {
      modoSeleccionado: null,
      playlistVisible: false
    }
  },
  methods: {
    seleccionarModo(modo) {
      this.modoSeleccionado = modo
      this.playlistVisible = false
    },

    volverModos() {
      this.modoSeleccionado = null
      this.playlistVisible = false
    },

    mostrarPlaylists() {
      this.playlistVisible = true
    },

    mostrarPlaylistsTablero() {
      this.playlistVisible = true
    },

    volverInstrucciones() {
      this.playlistVisible = false
    },

    selectIndividual(key) {
      this.$emit('select', { modo: 'individual', playlist: key })
    },

    selectTablero(key) {
      this.$emit('select', { modo: 'tablero', playlist: key })
    }
  }
}
</script>

<style scoped>
.selector-container {
  display: flex;
  gap: 1.5rem;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.contenido-area {
  flex: 1;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mensaje-inicial {
  text-align: center;
  padding: 3rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 24px;
  backdrop-filter: blur(20px);
  border: 2px dashed rgba(255, 255, 255, 0.2);
}

.mensaje-icono {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.mensaje-inicial h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: white;
}

.mensaje-inicial p {
  color: rgba(255, 255, 255, 0.7);
}

@media (max-width: 968px) {
  .selector-container {
    flex-direction: column;
  }
}
</style>
