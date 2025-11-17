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
      <p class="orden-explicacion">COLOCACIÓN: Más antiguas abajo | Más recientes arriba</p>
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

  <div class="botones-validacion">
    <button
      class="btn btn-verificar"
      @click="validarRespuesta"
      :disabled="!tituloUsuario.trim() || !artistaUsuario.trim() || validando"
    >
      {{ validando ? '⏳ Validando...' : '✅ Validar Todo' }}
    </button>

    <button
      class="btn btn-solo-anio"
      @click="validarSoloAnio"
      :disabled="validando"
    >
      📅 Solo validar año
    </button>
  </div>

  <p class="nota-solo-anio">
    💡 Si no sabes el título o artista, puedes validar solo el año
  </p>
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
    <!-- ✅ AÑADIR ESTA SECCIÓN DESPUÉS DEL RESULTADO Y ANTES DE LOS CONTROLES -->

<!-- Karaoke Section -->
<div v-if="mostrarKaraoke" class="karaoke-container">
  <div class="karaoke-header">
    <h2>🎤 ¡Prueba de Karaoke!</h2>
    <p>Has completado 10 canciones. Canta y gana hasta 20 puntos extra</p>
  </div>

  <div class="cancion-karaoke">
    <h3>{{ cancionKaraoke.titulo }}</h3>
    <p>{{ cancionKaraoke.artista }}</p>
  </div>

  <div v-if="!grabando && !evaluandoKaraoke" class="karaoke-instrucciones">
    <p>📱 Presiona el botón para grabar tu interpretación</p>
    <button class="btn btn-grabar" @click="iniciarGrabacion">
      🎤 Comenzar a Grabar
    </button>
  </div>

  <div v-if="grabando" class="grabando-estado">
    <div class="grabando-indicador"></div>
    <p>🔴 Grabando...</p>
    <button class="btn btn-detener" @click="detenerGrabacion">
      ⏹️ Detener Grabación
    </button>
  </div>

  <div v-if="audioGrabado && !evaluandoKaraoke" class="audio-grabado">
    <audio controls :src="audioGrabado" class="audio-player"></audio>
    <div class="botones-karaoke">
      <button class="btn btn-regrabar" @click="regrabar">
        🔄 Grabar de Nuevo
      </button>
      <button class="btn btn-enviar-karaoke" @click="enviarKaraoke">
        ✅ Enviar para Evaluación
      </button>
    </div>
  </div>

  <div v-if="evaluandoKaraoke" class="evaluando-container">
    <div class="loading-spinner"></div>
    <p>🤖 La IA está evaluando tu interpretación...</p>
  </div>

  <div v-if="resultadoKaraoke" class="resultado-karaoke">
    <h3>📊 Resultado del Karaoke</h3>

    <div class="puntos-karaoke">
      <span class="puntos-numero">+{{ resultadoKaraoke.puntos }}</span>
      <span class="puntos-label">puntos</span>
    </div>

    <div v-if="resultadoKaraoke.desglose" class="desglose">
      <div class="desglose-item">
        <span>📝 Letra:</span>
        <span>{{ resultadoKaraoke.desglose.letra }}/10</span>
      </div>
      <div class="desglose-item">
        <span>🎵 Ritmo:</span>
        <span>{{ resultadoKaraoke.desglose.ritmo }}/10</span>
      </div>
    </div>

    <div class="feedback-ia">
      {{ resultadoKaraoke.feedback }}
    </div>

    <button class="btn btn-continuar-karaoke" @click="continuarDespuesKaraoke">
      ➡️ Continuar Partida
    </button>
  </div>
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
      jugadorIndex: 0,
      mostrarKaraoke: false,
      cancionKaraoke: null,
      grabando: false,
      audioGrabado: null,
      mediaRecorder: null,
      audioChunks: [],
      evaluandoKaraoke: false,
      resultadoKaraoke: null
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

    async validarSoloAnio() {
  if (this.validando) return

  this.validando = true

  try {
    const resp = await fetch('http://localhost:5000/api/tablero/colocar-cancion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        partida_id: this.partidaId,
        jugador_index: this.jugadorIndex,
        posicion: this.posicionSeleccionada,
        titulo: '',  // ✅ Enviar vacío
        artista: ''  // ✅ Enviar vacío
      })
    })

    if (!resp.ok) {
      const errorData = await resp.json()
      alert(`Error: ${errorData.detail || 'Error al validar'}`)
      return
    }

    const data = await resp.json()

    console.log('✅ Respuesta del servidor (solo año):', data)

    // ✅ Actualizar línea de tiempo
    this.lineaTiempo = data.canciones_ordenadas || []

    // ✅ Actualizar puntos de la partida actual
    this.puntosPartidaActual = data.puntos_totales || 0

    // Mostrar resultado
    let mensaje = ''
    let tipo = 'incorrecto'

    if (data.correcto_anio) {
      tipo = 'parcial'
      mensaje = `📅 Año colocado correctamente (+${data.puntos_ganados} punto)<br>`
      mensaje += `La canción era: <strong>${data.titulo_real}</strong> - ${data.artista_real} (${data.anio_real})`
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
    console.error('Error validando solo año:', error)
    alert('Error de conexión al validar')
  } finally {
    this.validando = false
  }
},

     async cargarLineaTiempo() {
    try {
      const resp = await fetch(`http://localhost:5000/api/tablero/${this.partidaId}/linea-tiempo/${this.jugadorIndex}`)
      const data = await resp.json()

      this.lineaTiempo = data.canciones_ordenadas || []
      this.puntosPartidaActual = data.puntos || 0

      // ✅ DETECTAR SI NECESITA KARAOKE
      if (data.necesita_karaoke) {
        this.mostrarKaraoke = true
        // Usar la última canción agregada para el karaoke
        if (this.cancion) {
          this.cancionKaraoke = {
            titulo: this.cancion.titulo_real || this.cancion.titulo,
            artista: this.cancion.artista_real || this.cancion.artista
          }
        }
      }

    } catch (error) {
      console.error('Error cargando línea de tiempo:', error)
    }
  },
    async iniciarGrabacion() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      this.mediaRecorder = new MediaRecorder(stream)
      this.audioChunks = []

      this.mediaRecorder.ondataavailable = (event) => {
        this.audioChunks.push(event.data)
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' })
        this.audioGrabado = URL.createObjectURL(audioBlob)
      }

      this.mediaRecorder.start()
      this.grabando = true

    } catch (error) {
      console.error('Error accediendo al micrófono:', error)
      alert('No se pudo acceder al micrófono. Verifica los permisos.')
    }
  },

  detenerGrabacion() {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop()

      // Detener todos los tracks del stream
      this.mediaRecorder.stream.getTracks().forEach(track => track.stop())

      this.grabando = false
    }
  },

  regrabar() {
    this.audioGrabado = null
    this.audioChunks = []
  },

  async enviarKaraoke() {
    if (!this.audioGrabado) {
      alert('No hay audio grabado')
      return
    }

    this.evaluandoKaraoke = true

    try {
      // Convertir audio a base64
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' })
      const reader = new FileReader()

      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1] // Remover prefijo data:audio/webm;base64,

        // Enviar al backend
        const resp = await fetch('http://localhost:5000/api/tablero/karaoke', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            partida_id: this.partidaId,
            jugador_index: this.jugadorIndex,
            audio_base64: base64Audio
          })
        })

        if (!resp.ok) {
          const errorData = await resp.json()
          throw new Error(errorData.detail || 'Error al procesar karaoke')
        }

        const data = await resp.json()

        console.log('✅ Resultado karaoke:', data)

        // Actualizar puntos
        this.puntosPartidaActual = data.puntos_totales || this.puntosPartidaActual

        // Mostrar resultado
        this.resultadoKaraoke = {
          puntos: data.puntos_karaoke || 0,
          desglose: data.evaluacion_ia?.desglose,
          feedback: data.evaluacion_ia?.feedback || data.mensaje
        }

        this.evaluandoKaraoke = false

      }

      reader.readAsDataURL(audioBlob)

    } catch (error) {
      console.error('Error enviando karaoke:', error)
      alert('Error al evaluar el karaoke: ' + error.message)
      this.evaluandoKaraoke = false
    }
  },

  continuarDespuesKaraoke() {
    // Limpiar estado del karaoke
    this.mostrarKaraoke = false
    this.cancionKaraoke = null
    this.audioGrabado = null
    this.audioChunks = []
    this.resultadoKaraoke = null

    // Continuar al siguiente turno
    this.siguienteTurno()
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
    },

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
  .botones-validacion {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.botones-validacion .btn {
  flex: 1;
}

.btn-solo-anio {
  background: linear-gradient(135deg, #f39c12, #e67e22);
  color: white;
  padding: 1rem;
  font-size: 1rem;
  font-weight: 700;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(243, 156, 18, 0.3);
}

.btn-solo-anio:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(243, 156, 18, 0.4);
}

.btn-solo-anio:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.nota-solo-anio {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-top: 1rem;
  font-style: italic;
}

@media (max-width: 768px) {
  .botones-validacion {
    flex-direction: column;
  }
}
  /* ========== ESTILOS KARAOKE ========== */

.karaoke-container {
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.2), rgba(230, 126, 34, 0.1));
  border: 2px solid rgba(243, 156, 18, 0.5);
  border-radius: 24px;
  padding: 2rem;
  animation: fadeIn 0.5s ease;
}

.karaoke-header {
  text-align: center;
  margin-bottom: 2rem;
}

.karaoke-header h2 {
  color: #f39c12;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.karaoke-header p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

.cancion-karaoke {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 16px;
  padding: 1.5rem;
  text-align: center;
  margin-bottom: 2rem;
}

.cancion-karaoke h3 {
  color: white;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.cancion-karaoke p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  margin: 0;
}

.karaoke-instrucciones {
  text-align: center;
}

.karaoke-instrucciones p {
  color: white;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.btn-grabar {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  padding: 1.25rem 2rem;
  font-size: 1.2rem;
  font-weight: 700;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(231, 76, 60, 0.4);
}

.btn-grabar:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(231, 76, 60, 0.6);
}

.grabando-estado {
  text-align: center;
  padding: 2rem;
}

.grabando-indicador {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #e74c3c;
  margin: 0 auto 1rem;
  animation: pulse 1.5s ease-in-out infinite;
  box-shadow: 0 0 30px rgba(231, 76, 60, 0.6);
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
}

.grabando-estado p {
  color: #e74c3c;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.btn-detener {
  background: linear-gradient(135deg, #34495e, #2c3e50);
  color: white;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-detener:hover {
  background: linear-gradient(135deg, #2c3e50, #1a252f);
  transform: translateY(-2px);
}

.audio-grabado {
  text-align: center;
}

.audio-grabado .audio-player {
  width: 100%;
  max-width: 500px;
  margin: 0 auto 1.5rem;
  border-radius: 16px;
}

.botones-karaoke {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-regrabar {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
  color: white;
  padding: 1rem 2rem;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-regrabar:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(149, 165, 166, 0.4);
}

.btn-enviar-karaoke {
  background: linear-gradient(135deg, #00c851, #007e33);
  color: white;
  padding: 1rem 2rem;
  font-weight: 700;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(0, 200, 81, 0.3);
}

.btn-enviar-karaoke:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 200, 81, 0.5);
}

.evaluando-container {
  text-align: center;
  padding: 3rem;
}

.evaluando-container .loading-spinner {
  width: 60px;
  height: 60px;
  margin: 0 auto 1.5rem;
}

.evaluando-container p {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
}

.resultado-karaoke {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
}

.resultado-karaoke h3 {
  color: white;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.puntos-karaoke {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.puntos-numero {
  font-size: 4rem;
  font-weight: 800;
  background: linear-gradient(135deg, #00c851, #00ff6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.puntos-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.desglose {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

.desglose-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.desglose-item span:first-child {
  font-size: 1.5rem;
}

.desglose-item span:last-child {
  color: white;
  font-size: 1.3rem;
  font-weight: 700;
}

.feedback-ia {
  background: rgba(243, 156, 18, 0.2);
  border: 1px solid rgba(243, 156, 18, 0.4);
  border-radius: 12px;
  padding: 1.5rem;
  color: white;
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
  font-style: italic;
}

.btn-continuar-karaoke {
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  color: white;
  padding: 1.25rem 2.5rem;
  font-size: 1.1rem;
  font-weight: 700;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(156, 39, 176, 0.3);
}

.btn-continuar-karaoke:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(156, 39, 176, 0.5);
}

/* Responsive */
@media (max-width: 768px) {
  .karaoke-header h2 {
    font-size: 1.5rem;
  }

  .botones-karaoke {
    flex-direction: column;
  }

  .desglose {
    flex-direction: column;
    gap: 1rem;
  }

  .puntos-numero {
    font-size: 3rem;
  }
}
}
</style>
