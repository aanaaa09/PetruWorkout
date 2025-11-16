<template>
  <div class="game-tablero">
    <!-- Header con info del turno -->
    <div class="header-turno">
      <div class="info-jugador">
        <div class="jugador-nombre">
          <span v-if="jugadorTurno?.tipo === 'individual'">
            👤 {{ jugadorTurno.nombre }}
          </span>
          <span v-else-if="jugadorTurno?.tipo === 'pareja'">
            👥 {{ jugadorTurno.nombre_pareja }}
          </span>
        </div>
        <div v-if="jugadorTurno?.tipo === 'individual'" class="jugador-puntos">
          ⭐ {{ jugadorTurno.puntos }} puntos
        </div>
      </div>

      <div class="turno-info">
        Turno {{ turnoActual + 1 }}
      </div>
    </div>

    <!-- Audio Player -->
    <div v-if="!esperandoRespuesta && cancion" class="audio-section">
      <h3>🎧 Escucha y coloca la canción en el TreeMap</h3>
      <audio v-if="cancion.preview_url" controls :src="cancion.preview_url" class="audio-player"></audio>
    </div>

    <!-- TreeMap Visual -->
    <div class="treemap-container">
      <h3>📊 TreeMap - Ordena por año (ascendente)</h3>

      <div class="treemap-lista">
        <!-- Casilla inicial (si está vacío) -->
        <div v-if="treemap.length === 0" class="treemap-casilla vacia" @click="seleccionarPosicion(0)">
          <div class="casilla-numero">1</div>
          <div class="casilla-placeholder">Haz clic para colocar aquí</div>
        </div>

        <!-- Casillas con canciones -->
        <template v-for="(cancion, idx) in treemap" :key="idx">
          <!-- Botón para insertar ANTES -->
          <button
            v-if="!esperandoRespuesta"
            class="btn-insertar"
            @click="seleccionarPosicion(idx)"
            :disabled="esperandoRespuesta"
          >
            ➕ Insertar aquí
          </button>

          <!-- Canción existente -->
          <div class="treemap-casilla ocupada">
            <div class="casilla-numero">{{ idx + 1 }}</div>
            <div class="casilla-contenido">
              <div class="cancion-titulo">{{ cancion.titulo }}</div>
              <div class="cancion-artista">{{ cancion.artista }}</div>
              <div class="cancion-anio" :class="{ mostrar: esperandoRespuesta }">
                📅 {{ cancion.anio }}
              </div>
            </div>
          </div>
        </template>

        <!-- Botón para insertar AL FINAL -->
        <button
          v-if="!esperandoRespuesta && treemap.length > 0"
          class="btn-insertar"
          @click="seleccionarPosicion(treemap.length)"
          :disabled="esperandoRespuesta"
        >
          ➕ Insertar al final
        </button>
      </div>

      <div v-if="posicionSeleccionada !== null && !esperandoRespuesta" class="posicion-seleccionada">
        ✅ Posición seleccionada: {{ posicionSeleccionada + 1 }}
      </div>
    </div>

    <!-- Formulario de respuesta -->
    <div v-if="posicionSeleccionada !== null && !esperandoRespuesta" class="form-respuesta">
      <h3>¿Cuál es el título y el artista?</h3>

      <div class="form-inputs">
        <input
          v-model="tituloUsuario"
          type="text"
          placeholder="Título de la canción"
          class="input-respuesta"
          @keypress.enter="validarRespuesta"
        />
        <input
          v-model="artistaUsuario"
          type="text"
          placeholder="Artista"
          class="input-respuesta"
          @keypress.enter="validarRespuesta"
        />
      </div>

      <button
        class="btn btn-verificar"
        @click="validarRespuesta"
        :disabled="!tituloUsuario.trim() || !artistaUsuario.trim() || validando"
      >
        {{ validando ? '⏳ Validando...' : '✅ Validar y Colocar' }}
      </button>
    </div>

    <!-- Resultado -->
    <div v-if="resultado" class="resultado-container" :class="resultado.tipo">
      <div class="resultado-mensaje" v-html="resultado.mensaje"></div>

      <div v-if="resultado.qr" class="qr-container">
        <img :src="resultado.qr" alt="QR Code" class="qr-image" />
      </div>
    </div>

    <!-- Botones de control -->
    <div class="controles">
      <button
        v-if="esperandoRespuesta"
        class="btn btn-siguiente"
        @click="siguienteTurno"
      >
        ➡️ Siguiente Turno
      </button>

      <button class="btn btn-volver" @click="$emit('volver')">
        ⬅️ Volver al Menú
      </button>
    </div>

    <!-- Loading -->
    <div v-if="cargando" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>Cargando...</p>
    </div>
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
  },
  data() {
    return {
      cargando: false,
      cancion: null,
      treemap: [],
      posicionSeleccionada: null,
      tituloUsuario: '',
      artistaUsuario: '',
      validando: false,
      esperandoRespuesta: false,
      resultado: null,
      turnoActual: 0,
      jugadorTurno: null,
      jugadorIndex: 0
    }
  },
  mounted() {
    this.cargarTurno()
  },
  methods: {
    async cargarTurno() {
      this.cargando = true
      this.limpiarEstado()

      try {
        // Obtener canción del turno
        const respCancion = await fetch(`http://localhost:5000/api/tablero/${this.partidaId}/cancion`)
        const dataCancion = await respCancion.json()

        if (dataCancion.error) {
          alert(dataCancion.error)
          return
        }

        this.cancion = dataCancion
        this.jugadorTurno = dataCancion.jugador_info
        this.turnoActual = dataCancion.turno_actual

        // Determinar el jugador_index actual
        this.jugadorIndex = this.turnoActual

        // Cargar TreeMap del jugador actual
        await this.cargarTreeMap()

      } catch (error) {
        console.error('Error cargando turno:', error)
        alert('Error al cargar el turno')
      } finally {
        this.cargando = false
      }
    },

    async cargarTreeMap() {
      try {
        const resp = await fetch(`http://localhost:5000/api/tablero/${this.partidaId}/treemap/${this.jugadorIndex}`)
        const data = await resp.json()

        this.treemap = data.canciones || []
      } catch (error) {
        console.error('Error cargando TreeMap:', error)
      }
    },

    seleccionarPosicion(pos) {
      this.posicionSeleccionada = pos
      this.resultado = null
    },

    async validarRespuesta() {
  if (this.validando) return

  if (!this.tituloUsuario.trim() || !this.artistaUsuario.trim()) {
    alert('Por favor completa título y artista')
    return
  }

  this.validando = true

  try {
    const resp = await fetch('http://localhost:5000/api/tablero/colocar-cancion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        partida_id: this.partidaId,
        jugador_index: this.jugadorIndex,
        posicion: this.posicionSeleccionada,
        titulo: this.tituloUsuario.trim(),
        artista: this.artistaUsuario.trim()
      })
    })

    if (!resp.ok) {
      const errorData = await resp.json()
      alert(`Error: ${errorData.detail || 'Error al validar'}`)
      return
    }

    const data = await resp.json()

    console.log('Respuesta del servidor:', data) // 👈 Para debug

    // Actualizar TreeMap
    this.treemap = data.treemap_actualizado || []

    // Mostrar resultado
    let mensaje = ''
    let tipo = 'incorrecto'

    if (data.correcto_anio && data.correcto_titulo && data.correcto_artista) {
      tipo = 'correcto'
      mensaje = `🎉 ¡Perfecto! +${data.puntos_ganados} puntos<br>`
      mensaje += `<strong>${data.titulo_real}</strong> - ${data.artista_real} (${data.anio_real})`
    } else if (data.correcto_anio && (data.correcto_titulo || data.correcto_artista)) {
      tipo = 'parcial'
      mensaje = `⚡ Año correcto pero `
      if (!data.correcto_titulo) mensaje += 'el título no. '
      if (!data.correcto_artista) mensaje += 'el artista no. '
      mensaje += `+${data.puntos_ganados} puntos<br>`
      mensaje += `Era: <strong>${data.titulo_real}</strong> - ${data.artista_real} (${data.anio_real})`
    } else if (data.correcto_anio) {
      tipo = 'parcial'
      mensaje = `📅 Solo el año es correcto. +${data.puntos_ganados} punto<br>`
      mensaje += `Era: <strong>${data.titulo_real}</strong> - ${data.artista_real} (${data.anio_real})`
    } else {
      mensaje = `❌ Posición incorrecta en el TreeMap<br>`
      mensaje += `La canción era: <strong>${data.titulo_real}</strong> - ${data.artista_real} (${data.anio_real})`
    }

    this.resultado = {
      tipo,
      mensaje,
      qr: data.qr_code || null
    }

    this.esperandoRespuesta = true

  } catch (error) {
    console.error('Error validando respuesta:', error)
    alert('Error de conexión al validar la respuesta')
  } finally {
    this.validando = false
  }
},

    async siguienteTurno() {
      this.cargando = true

      try {
        const resp = await fetch(`http://localhost:5000/api/tablero/${this.partidaId}/avanzar-turno`, {
          method: 'POST'
        })

        const data = await resp.json()

        if (data.error) {
          alert(data.error)
          return
        }

        // Cargar nuevo turno
        await this.cargarTurno()

      } catch (error) {
        console.error('Error avanzando turno:', error)
        alert('Error al avanzar al siguiente turno')
      } finally {
        this.cargando = false
      }
    },

    limpiarEstado() {
      this.posicionSeleccionada = null
      this.tituloUsuario = ''
      this.artistaUsuario = ''
      this.resultado = null
      this.esperandoRespuesta = false
    }
  }
}
</script>

<style scoped>
.resultado-container.parcial {
  background: linear-gradient(135deg, #f39c12, #f1c40f);
  border: 2px solid #f39c12;
}
.game-tablero {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  animation: fadeIn 0.5s ease;
}

/* Header del turno */
.header-turno {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.jugador-nombre {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
}

.jugador-puntos {
  font-size: 1.2rem;
  color: #ffd700;
  font-weight: 600;
}

.turno-info {
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-weight: 700;
  color: white;
}

/* Audio */
.audio-section {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
  border-radius: 24px;
  padding: 2rem;
  border: 1px solid rgba(255,255,255,0.2);
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  text-align: center;
}

.audio-section h3 {
  color: white;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.audio-player {
  width: 100%;
  max-width: 500px;
  border-radius: 16px;
}

/* TreeMap */
.treemap-container {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 24px;
  padding: 2rem;
  border: 2px solid rgba(156, 39, 176, 0.3);
}

.treemap-container h3 {
  color: white;
  margin-bottom: 1.5rem;
  text-align: center;
  font-size: 1.3rem;
}

.treemap-lista {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn-insertar {
  background: rgba(0, 200, 81, 0.2);
  border: 2px dashed rgba(0, 200, 81, 0.5);
  border-radius: 12px;
  padding: 0.75rem;
  color: #00c851;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-insertar:hover:not(:disabled) {
  background: rgba(0, 200, 81, 0.3);
  border-color: #00c851;
  transform: scale(1.02);
}

.btn-insertar:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.treemap-casilla {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 1rem 1.5rem;
  transition: all 0.3s ease;
}

.treemap-casilla.vacia {
  border-style: dashed;
  cursor: pointer;
  min-height: 80px;
  justify-content: center;
}

.treemap-casilla.vacia:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #9c27b0;
}

.treemap-casilla.ocupada {
  border-color: rgba(156, 39, 176, 0.5);
}

.casilla-numero {
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.casilla-placeholder {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.casilla-contenido {
  flex: 1;
}

.cancion-titulo {
  font-weight: 700;
  color: white;
  font-size: 1.1rem;
  margin-bottom: 0.25rem;
}

.cancion-artista {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
}

.cancion-anio {
  color: #ffd700;
  font-weight: 600;
  margin-top: 0.5rem;
  opacity: 0;
  max-height: 0;
  overflow: hidden;
  transition: all 0.3s ease;
}

.cancion-anio.mostrar {
  opacity: 1;
  max-height: 50px;
}

.posicion-seleccionada {
  text-align: center;
  color: #00c851;
  font-weight: 700;
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 200, 81, 0.1);
  border-radius: 12px;
}

/* Formulario */
.form-respuesta {
  background: linear-gradient(135deg, #ffd6a5, #ffb6b9);
  border-radius: 24px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.form-respuesta h3 {
  color: #6a1b9a;
  margin-bottom: 1.5rem;
  text-align: center;
}

.form-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.input-respuesta {
  padding: 1rem;
  border-radius: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.6);
  color: #4a235a;
  font-weight: 500;
  font-size: 1rem;
}

.input-respuesta:focus {
  outline: none;
  border-color: #9c27b0;
  box-shadow: 0 0 0 4px rgba(156, 39, 176, 0.2);
}

/* Resultado */
.resultado-container {
  padding: 2rem;
  border-radius: 20px;
  text-align: center;
  animation: slideIn 0.5s ease;
}

.resultado-container.correcto {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  border: 2px solid #27ae60;
}

.resultado-container.incorrecto {
  background: linear-gradient(135deg, #c0392b, #e74c3c);
  border: 2px solid #c0392b;
}

.resultado-mensaje {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.qr-container {
  margin-top: 1.5rem;
}

.qr-image {
  width: 200px;
  height: 200px;
  border-radius: 16px;
  background: white;
  padding: 1rem;
}

/* Controles */
.controles {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

/* Loading */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@media (max-width: 768px) {
  .form-inputs {
    grid-template-columns: 1fr;
  }

  .header-turno {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
