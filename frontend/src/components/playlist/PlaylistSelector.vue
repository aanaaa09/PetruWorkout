<template>
  <div class="selector-container">
    <!-- Columna izquierda: Selector de modo -->
    <ModeSelector
      :modo-seleccionado="modoSeleccionado"
      @select="seleccionarModo"
    />

    <!-- Columna derecha: Contenido dinámico -->
    <div class="contenido-area">
      <!-- Mensaje inicial -->
      <div v-if="!modoSeleccionado" class="mensaje-inicial">
        <div class="mensaje-icono">👈</div>
        <h2>Elige un modo de juego</h2>
        <p>Selecciona una opción de la izquierda para comenzar</p>
      </div>

      <!-- Instrucciones -->
      <InstructionsCard
        v-else-if="mostrarInstrucciones"
        :titulo="tituloInstrucciones"
        :show-continue="modoSeleccionado !== 'online'"
        @close="volverModos"
        @continue="mostrarInstrucciones = false"
      >
        <!-- Individual -->
        <template v-if="modoSeleccionado === 'individual'">
          <h3>📋 Cómo funciona:</h3>
          <ul>
            <li>Elige una playlist de canciones</li>
            <li>Escucha fragmentos de 30 segundos</li>
            <li>Adivina el título y el artista</li>
            <li>Gana puntos por cada acierto</li>
            <li>Compite en el ranking global</li>
          </ul>
        </template>

        <!-- Tablero -->
        <template v-else-if="modoSeleccionado === 'tablero'">
          <div class="proximamente-banner">
            🚧 PRÓXIMAMENTE 🚧
          </div>
          <h3>🎲 Características futuras:</h3>
          <ul>
            <li>Tablero interactivo con casillas especiales</li>
            <li>Modo multijugador local (hasta 4 jugadores)</li>
            <li>Casillas con retos y bonificaciones</li>
            <li>Preguntas de diferentes tipos</li>
            <li>Sistema de turnos y puntuación</li>
          </ul>
          <p class="proximamente-info">
            Estamos trabajando en esta modalidad. ¡Vuelve pronto!
          </p>
        </template>

        <!-- Online -->
        <template v-else-if="modoSeleccionado === 'online'">
          <div class="proximamente-banner">
            🚧 PRÓXIMAMENTE 🚧
          </div>
          <h3>🌐 Características futuras:</h3>
          <ul>
            <li>Partidas en tiempo real con jugadores de todo el mundo</li>
            <li>Salas públicas y privadas</li>
            <li>Chat en vivo durante las partidas</li>
            <li>Rankings internacionales</li>
            <li>Torneos y eventos especiales</li>
          </ul>
          <p class="proximamente-info">
            El modo online llegará en futuras actualizaciones
          </p>
        </template>
      </InstructionsCard>

      <!-- Selector de playlist -->
      <PlaylistGrid
        v-else
        :playlists="playlists"
        @select="seleccionarPlaylist"
        @back="mostrarInstrucciones = true"
      />
    </div>
  </div>
</template>

<script>
import ModeSelector from './ModeSelector.vue'
import InstructionsCard from './InstructionsCard.vue'
import PlaylistGrid from './PlaylistGrid.vue'
import { PLAYLISTS } from '../../config/playlists'

export default {
  name: 'PlaylistSelector',
  components: {
    ModeSelector,
    InstructionsCard,
    PlaylistGrid
  },
  data() {
    return {
      modoSeleccionado: null,
      mostrarInstrucciones: false,
      playlists: PLAYLISTS
    }
  },
  computed: {
    tituloInstrucciones() {
      const titulos = {
        individual: '🎵 Modo Individual',
        tablero: '🎲 Modo Tablero',
        online: '🌐 Modo Online'
      }
      return titulos[this.modoSeleccionado] || 'Instrucciones'
    }
  },
  methods: {
    seleccionarModo(modo) {
      this.modoSeleccionado = modo
      this.mostrarInstrucciones = true
    },

    volverModos() {
      this.modoSeleccionado = null
      this.mostrarInstrucciones = false
    },

    seleccionarPlaylist(playlistKey) {
      this.$emit('select', {
        modo: this.modoSeleccionado,
        playlist: playlistKey
      })
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
