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

        <!-- Puntos de la partida actual -->
        <div class="jugador-puntos">
          <div class="puntos-partida">
            🎯 {{ puntosPartidaActual }} pts (esta partida)
          </div>
          <div v-if="jugadorTurno?.tipo === 'individual'" class="puntos-totales">
            ⭐ {{ jugadorTurno.puntos }} pts totales
          </div>
        </div>
      </div>

      <div class="turno-info">
        Turno {{ turnoActual + 1 }}
      </div>
    </div>

    <!-- Audio Player -->
    <div v-if="!esperandoRespuesta && cancion" class="audio-section">
      <h3>🎧 Escucha y coloca la canción en la Línea de Tiempo</h3>
      <p class="instruccion">Ordena por año ascendente (del más antiguo al más reciente)</p>
      <audio v-if="cancion.preview_url" controls :src="cancion.preview_url" class="audio-player"></audio>
    </div>

    <!-- Línea de Tiempo Visual -->
    <div class="linea-tiempo-container">
      <h3>📊 Línea de Tiempo Musical</h3>
      <p class="orden-explicacion">COLOCACIÓN: ⬆Más antiguas abajo | Más recientes arriba</p>
      <div class="linea-tiempo-lista">
        <!-- Casilla inicial (si está vacío) -->
        <div v-if="lineaTiempoInvertida.length === 0" class="linea-casilla vacia" @click="seleccionarPosicion(0)">
          <div class="casilla-numero">1</div>
          <div class="casilla-placeholder">🎵 Primera canción - Haz clic aquí</div>
        </div>

        <!-- Casillas con canciones (INVERTIDAS) -->
        <template v-for="(item, idx) in lineaTiempoInvertida" :key="`cancion-${item.posicionOriginal}`">
          <!-- Botón para insertar ANTES (en la vista invertida) -->
          <button
            v-if="!esperandoRespuesta"
            class="btn-insertar"
            @click="seleccionarPosicion(item.posicionOriginal)"
            :disabled="esperandoRespuesta"
          >
            ➕ Insertar aquí
          </button>

          <!-- Canción existente -->
          <div class="linea-casilla ocupada">
            <div class="casilla-numero">{{ lineaTiempoInvertida.length - idx }}</div>
            <div class="casilla-contenido">
              <div class="cancion-titulo">{{ item.cancion.titulo }}</div>
              <div class="cancion-artista">{{ item.cancion.artista }}</div>
              <div class="cancion-anio visible">
                📅 {{ item.cancion.anio }}
              </div>
            </div>
          </div>
        </template>

        <!-- Botón para insertar AL FINAL (más antigua = abajo) -->
        <button
          v-if="!esperandoRespuesta && lineaTiempo.length > 0"
          class="btn-insertar"
          @click="seleccionarPosicion(lineaTiempo.length)"
          :disabled="esperandoRespuesta"
        >
          ➕ Insertar aquí (más antigua)
        </button>
      </div>

      <div v-if="posicionSeleccionada !== null && !esperandoRespuesta" class="posicion-seleccionada">
        ✅ Posición seleccionada: {{ obtenerTextoMensajePosicion() }}
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
      lineaTiempo: [], // Lista original ordenada ascendentemente por año
      puntosPartidaActual: 0, // ✅ Puntos de esta partida
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
  computed: {
    // ✅ Invertir la línea de tiempo para mostrar más recientes arriba
    lineaTiempoInvertida() {
      return this.lineaTiempo
        .map((cancion, idx) => ({
          cancion,
          posicionOriginal: idx
        }))

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
          this.cargando = false
          return
        }

        this.cancion = dataCancion
        this.jugadorTurno = dataCancion.jugador_info
        this.turnoActual = dataCancion.turno_actual

        // ✅ CORRECCIÓN: Asegurarse de que jugadorIndex esté definido antes de cargar
        this.jugadorIndex = this.turnoActual

        console.log('🎮 Turno cargado:', {
          turno: this.turnoActual,
          jugadorIndex: this.jugadorIndex,
          jugador: this.jugadorTurno
        })

        // Cargar Línea de Tiempo del jugador actual
        await this.cargarLineaTiempo()

      } catch (error) {
        console.error('Error cargando turno:', error)
        alert('Error al cargar el turno')
      } finally {
        this.cargando = false
      }
    },

    async cargarLineaTiempo() {
      try {
        const resp = await fetch(`http://localhost:5000/api/tablero/${this.partidaId}/linea-tiempo/${this.jugadorIndex}`)
        const data = await resp.json()

        console.log('📦 Línea de tiempo cargada:', data)

        // ✅ CORRECCIÓN: Usar "canciones_ordenadas" en lugar de "canciones"
        this.lineaTiempo = data.canciones_ordenadas || []

        // ✅ Cargar puntos de la partida actual
        this.puntosPartidaActual = data.puntos || 0

      } catch (error) {
        console.error('Error cargando línea de tiempo:', error)
      }
    },

   obtenerTextoMensajePosicion() {
  // Como el array viene invertido del backend, la lógica es:
  // posicion alta en BD = se ve abajo (antigua)
  // posicion baja en BD = se ve arriba (reciente)

  if (this.posicionSeleccionada === this.lineaTiempo.length) {
    return 'Abajo del todo (más antigua)'
  } else if (this.posicionSeleccionada === 0) {
    return 'Arriba del todo (más reciente)'
  } else {
    // Calcular años según posición en BD
    const posVisual = this.lineaTiempo.length - this.posicionSeleccionada
    const anioSuperior = this.lineaTiempo[posVisual - 1]?.anio
    const anioInferior = this.lineaTiempo[posVisual]?.anio
    return `Entre ${anioSuperior} (arriba) y ${anioInferior} (abajo)`
  }
},

    seleccionarPosicion(pos) {
  // Convertir posición visual a posición en array del backend
  // Visual: [0=arriba más reciente, n=abajo más antigua]
  // Backend: [0=más antigua, n=más reciente]
  const posicionBackend = this.lineaTiempo.length - pos

  this.posicionSeleccionada = posicionBackend
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

        console.log('✅ Respuesta del servidor:', data)

        // ✅ CORRECCIÓN CRÍTICA: Usar "canciones_ordenadas"
        this.lineaTiempo = data.canciones_ordenadas || []

        // ✅ Actualizar puntos de la partida actual
        this.puntosPartidaActual = data.puntos_totales || 0

        // Mostrar resultado
        let mensaje = ''
        let tipo = 'incorrecto'

        if (data.correcto_anio && data.correcto_titulo && data.correcto_artista) {
          tipo = 'correcto'
          mensaje = `🎉 ¡Perfecto! +${data.puntos_ganados} puntos<br>`
          mensaje += `<strong>${data.titulo_real}</strong> - ${data.artista_real} (${data.anio_real})`
        } else if (data.correcto_anio && (data.correcto_titulo || data.correcto_artista)) {
          tipo = 'parcial'
          mensaje = `⚡ `
          if (data.correcto_titulo) {
            mensaje += 'Título correcto, pero '
          }
          if (data.correcto_artista) {
            mensaje += 'Artista correcto, pero '
          }
          if (!data.correcto_titulo) {
            mensaje += 'título incorrecto. '
          }
          if (!data.correcto_artista) {
            mensaje += 'artista incorrecto. '
          }
          mensaje += `Año bien colocado. +${data.puntos_ganados} puntos<br>`
          mensaje += `Era: <strong>${data.titulo_real}</strong> - ${data.artista_real} (${data.anio_real})`
        } else if (data.correcto_anio) {
          tipo = 'parcial'
          mensaje = `📅 Solo el año es correcto (+${data.puntos_ganados} punto)<br>`
          mensaje += `Era: <strong>${data.titulo_real}</strong> - ${data.artista_real} (${data.anio_real})`
        } else {
          mensaje = `❌ Año mal colocado (0 puntos)<br>`
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
/* Todos los estilos anteriores se mantienen igual */
.game-tablero {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  animation: fadeIn 0.5s ease;
}

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
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.puntos-partida {
  font-size: 1.3rem;
  color: #00c851;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0, 200, 81, 0.3);
}

.puntos-totales {
  font-size: 1rem;
  color: #ffd700;
  font-weight: 600;
}

.orden-explicacion {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin: -0.5rem 0 1rem 0;
  font-style: italic;
}

.turno-info {
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-weight: 700;
  color: white;
}

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
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.instruccion {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.audio-player {
  width: 100%;
  max-width: 500px;
  border-radius: 16px;
}

.linea-tiempo-container {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 24px;
  padding: 2rem;
  border: 2px solid rgba(156, 39, 176, 0.3);
}

.linea-tiempo-container h3 {
  color: white;
  margin-bottom: 1.5rem;
  text-align: center;
  font-size: 1.3rem;
}

.linea-tiempo-lista {
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

.linea-casilla {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 1rem 1.5rem;
  transition: all 0.3s ease;
}

.linea-casilla.vacia {
  border-style: dashed;
  cursor: pointer;
  min-height: 80px;
  justify-content: center;
}

.linea-casilla.vacia:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #9c27b0;
}

.linea-casilla.ocupada {
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
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.cancion-anio.visible {
  opacity: 1;
  max-height: none;
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

.resultado-container.parcial {
  background: linear-gradient(135deg, #f39c12, #f1c40f);
  border: 2px solid #f39c12;
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

.controles {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

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
