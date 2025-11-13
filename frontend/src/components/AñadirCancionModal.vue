<template>
  <div v-if="mostrar" class="modal-overlay" @click.self="cerrar">
    <div class="modal-content">
      <div class="modal-header">
        <h2>➕ Añadir Canción</h2>
        <button class="btn-close" @click="cerrar">✕</button>
      </div>

      <div class="modal-body">
        <!-- Selector de Playlist -->
        <div class="form-group">
          <label>Playlist de Destino</label>
          <select v-model="playlistSeleccionada" class="form-select">
            <option value="">Selecciona una playlist...</option>
            <option value="juego_clasico">🎵 Juego Clásico</option>
            <option value="urban_hits">🔥 Urban Hits</option>
            <option value="ochenta_noventa">📻 Ochenta y Noventa</option>
            <option value="flamenco_rumba">💃 Flamenco y Rumba</option>
            <option value="pop_espanol">🎤 Pop Español</option>
          </select>
        </div>

        <!-- URL o ID de Spotify -->
        <div class="form-group">
          <label>URL o ID de Spotify</label>
          <input
            v-model="spotifyInput"
            type="text"
            class="form-input"
            placeholder="https://open.spotify.com/track/... o solo el ID"
            @input="limpiarError"
          />
          <small class="form-hint">
            Pega la URL completa de Spotify o solo el ID de la canción
          </small>
        </div>

        <!-- Botón para buscar -->
        <button
          class="btn-buscar"
          @click="buscarCancion"
          :disabled="!spotifyInput || !playlistSeleccionada || cargando"
        >
          {{ cargando ? '🔍 Buscando...' : '🔍 Buscar Canción' }}
        </button>

        <!-- Mensaje de error -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- Información de la canción encontrada -->
        <div v-if="cancionEncontrada" class="cancion-info">
          <h3>✅ Canción Encontrada</h3>

          <div class="info-item">
            <strong>Título:</strong>
            <span>{{ cancionEncontrada.titulo }}</span>
          </div>

          <div class="info-item">
            <strong>Artista:</strong>
            <span>{{ cancionEncontrada.artista }}</span>
          </div>

          <div class="info-item">
            <strong>Año (Spotify):</strong>
            <span>{{ cancionEncontrada.anio_spotify || 'No disponible' }}</span>
          </div>

          <!-- Campo para año manual -->
          <div class="form-group">
            <label>
              <input type="checkbox" v-model="usarAnioManual" />
              Usar año personalizado
            </label>
            <input
              v-if="usarAnioManual"
              v-model.number="anioManual"
              type="number"
              class="form-input"
              placeholder="Ej: 2023"
              min="1900"
              :max="new Date().getFullYear()"
            />
          </div>

          <!-- Preview del audio -->
          <div v-if="cancionEncontrada.preview_url" class="preview-container">
            <audio controls :src="cancionEncontrada.preview_url" class="audio-player">
              Tu navegador no soporta audio.
            </audio>
          </div>

          <!-- Botón para añadir -->
          <button
            class="btn-añadir"
            @click="añadirCancion"
            :disabled="añadiendo"
          >
            {{ añadiendo ? '⏳ Añadiendo...' : '✅ Añadir a Playlist' }}
          </button>
        </div>

        <!-- Mensaje de éxito -->
        <div v-if="exitoMensaje" class="success-message">
          {{ exitoMensaje }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AñadirCancionModal',
  props: {
    mostrar: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      playlistSeleccionada: '',
      spotifyInput: '',
      cancionEncontrada: null,
      usarAnioManual: false,
      anioManual: null,
      cargando: false,
      añadiendo: false,
      error: '',
      exitoMensaje: ''
    }
  },
  methods: {
    cerrar() {
      this.$emit('cerrar')
      this.resetear()
    },

    resetear() {
      this.playlistSeleccionada = ''
      this.spotifyInput = ''
      this.cancionEncontrada = null
      this.usarAnioManual = false
      this.anioManual = null
      this.error = ''
      this.exitoMensaje = ''
    },

    limpiarError() {
      this.error = ''
      this.cancionEncontrada = null
      this.exitoMensaje = ''
    },

    extraerSpotifyId(input) {
      // Si es una URL completa
      const urlMatch = input.match(/track\/([a-zA-Z0-9]+)/)
      if (urlMatch) {
        return urlMatch[1]
      }
      // Si ya es solo el ID
      return input.trim()
    },

    async buscarCancion() {
      this.error = ''
      this.cancionEncontrada = null
      this.exitoMensaje = ''
      this.cargando = true

      try {
        const spotifyId = this.extraerSpotifyId(this.spotifyInput)

        const response = await axios.post('/api/buscar-cancion', {
          spotify_id: spotifyId,
          playlist_key: this.playlistSeleccionada
        })

        if (response.data.error) {
          this.error = response.data.error
        } else {
          this.cancionEncontrada = response.data
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al buscar la canción'
      } finally {
        this.cargando = false
      }
    },

    async añadirCancion() {
      this.error = ''
      this.añadiendo = true

      try {
        const anioFinal = this.usarAnioManual && this.anioManual
          ? this.anioManual
          : this.cancionEncontrada.anio_spotify

        const response = await axios.post('/api/añadir-cancion', {
          playlist_key: this.playlistSeleccionada,
          spotify_id: this.cancionEncontrada.spotify_id,
          anio: anioFinal
        })

        if (response.data.success) {
          this.exitoMensaje = '✅ ¡Canción añadida correctamente!'

          // Cerrar el modal después de 2 segundos
          setTimeout(() => {
            this.cerrar()
          }, 2000)
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al añadir la canción'
      } finally {
        this.añadiendo = false
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 20px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h2 {
  margin: 0;
  color: white;
  font-size: 1.5rem;
}

.btn-close {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  color: white;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.form-select,
.form-input {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}
.form-input {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

/* Estilos específicos para las opciones del select */
.form-select option {
  background: #1a1a2e;
  color: white;
  padding: 0.5rem;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #8b5cf6;
  background: rgba(255, 255, 255, 0.15);
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #8b5cf6;
  background: rgba(255, 255, 255, 0.15);
}

.form-hint {
  display: block;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.btn-buscar,
.btn-añadir {
  width: 100%;
  padding: 0.875rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.btn-buscar:hover:not(:disabled),
.btn-añadir:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.btn-buscar:disabled,
.btn-añadir:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #fca5a5;
  padding: 1rem;
  border-radius: 10px;
  margin-top: 1rem;
}

.success-message {
  background: rgba(34, 197, 94, 0.2);
  border: 1px solid rgba(34, 197, 94, 0.5);
  color: #86efac;
  padding: 1rem;
  border-radius: 10px;
  margin-top: 1rem;
  text-align: center;
  font-weight: 600;
}

.cancion-info {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.cancion-info h3 {
  color: white;
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.info-item:last-of-type {
  border-bottom: none;
}

.info-item strong {
  color: rgba(255, 255, 255, 0.7);
}

.info-item span {
  color: white;
  font-weight: 500;
}

.preview-container {
  margin: 1.5rem 0;
}

.audio-player {
  width: 100%;
  border-radius: 10px;
}

/* Checkbox personalizado */
.form-group label input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
  cursor: pointer;
}

/* Scrollbar personalizado */
.modal-content::-webkit-scrollbar {
  width: 8px;
}

.modal-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* Responsive */
@media (max-width: 768px) {
  .modal-content {
    max-width: 95%;
    margin: 1rem;
  }

  .modal-header h2 {
    font-size: 1.25rem;
  }

  .info-item {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>
