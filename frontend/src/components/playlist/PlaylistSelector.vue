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
  <div class="instrucciones-grid">
    <div class="seccion-instrucciones">
      <h4>👥 Jugadores</h4>
      <ul>
        <li>Individual (hasta 4) o Parejas (hasta 3)</li>
        <li>Registrados o invitados</li>
      </ul>
    </div>

    <div class="seccion-instrucciones">
      <h4>🎵 Juego</h4>
      <ul>
        <li>Coloca canciones por orden cronológico</li>
        <li>Crea casillas entre canciones</li>
      </ul>
    </div>

    <div class="seccion-instrucciones">
      <h4>🎯 Puntos</h4>
      <ul>
        <li>+1 punto si aciertas el año</li>
        <li>+5 puntos si aciertas título y artista</li>
      </ul>
    </div>

    <div class="seccion-instrucciones destacada">
      <h4>🎤 Karaoke</h4>
      <ul>
        <li>Al completar 10 canciones</li>
        <li>La IA te evalúa (hasta +20 puntos)</li>
      </ul>
    </div>

    <div class="seccion-instrucciones">
      <h4>🏆 Final</h4>
      <ul>
        <li>Gana quien tenga más puntos</li>
        <li>Puntos se guardan si estás registrado</li>
      </ul>
    </div>

    <div class="seccion-instrucciones">
      <h4>💡 Consejo</h4>
      <ul>
        <li>Organiza las canciones por décadas</li>
        <li>Valida solo el año si no sabes la canción</li>
      </ul>
    </div>
  </div>
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

/* Secciones de instrucciones */
.seccion-instrucciones {
  background: rgba(255, 255, 255, 0.03);
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  border-left: 3px solid rgba(156, 39, 176, 0.5);
}

.seccion-instrucciones.destacada {
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.1), rgba(230, 126, 34, 0.05));
  border-left-color: #f39c12;
  box-shadow: 0 4px 12px rgba(243, 156, 18, 0.2);
}

.seccion-instrucciones h4 {
  font-size: 1rem;
  margin: 0 0 0.75rem 0;
  color: white;
  font-weight: 700;
}

.seccion-instrucciones.destacada h4 {
  color: #f39c12;
  text-shadow: 0 2px 8px rgba(243, 156, 18, 0.3);
}

.seccion-instrucciones ul {
  margin: 0;
  padding-left: 1.5rem;
}

.seccion-instrucciones li {
  padding: 0.4rem 0;
  line-height: 1.5;
}

.seccion-instrucciones strong {
  color: #9c27b0;
  font-weight: 700;
}

.seccion-instrucciones.destacada strong {
  color: #f39c12;
}

/* Responsive */
@media (max-width: 768px) {
  .seccion-instrucciones {
    padding: 0.75rem;
  }

  .seccion-instrucciones h4 {
    font-size: 0.95rem;
  }

  .seccion-instrucciones li {
    font-size: 0.9rem;
  }
}
</style>
