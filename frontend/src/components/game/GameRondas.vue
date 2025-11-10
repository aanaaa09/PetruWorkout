<template>
  <div class="game-wrapper">

    <!-- Playlist Badge con progreso de ronda -->
    <div class="playlist-badge">
      <div class="playlist-icon">🎵</div>
      <div class="playlist-info">
        <div class="playlist-name">{{ playlistInfo.nombre }}</div>
        <div class="ronda-progreso" v-if="estadoRonda">
          Pregunta {{ estadoRonda.pregunta_numero || 0 }}/{{ estadoRonda.total_preguntas || 10 }}
          | 💰 {{ estadoRonda.puntos_actuales || 0 }} pts
          <span v-if="estadoRonda.racha_actual > 0" class="racha-badge">
            🔥 x{{ estadoRonda.racha_actual }}
          </span>
        </div>
      </div>
    </div>

    <!-- Iniciar Ronda -->
    <div v-if="!rondaIniciada && !rondaMostradaUnaVez && !loading" class="iniciar-ronda-card">
      <h2>🎮 ¡Comienza una nueva ronda!</h2>
      <p>10 preguntas aleatorias te esperan</p>
      <button class="btn btn-verificar" @click="iniciarRonda">
        🎲 Iniciar Ronda
      </button>
    </div>

    <!-- Durante la ronda -->
    <template v-if="rondaIniciada && !rondaTerminada">
      <!-- Dado con tipo de pregunta -->
      <div v-if="tipoPregunta" class="dado-pregunta">
        <div class="dado-icon">🎲</div>
        <div class="pregunta-texto">
          <span v-if="tipoPregunta === 'solo_titulo'">
            🎵 Adivina solo el <strong>Título</strong>
          </span>
          <span v-else-if="tipoPregunta === 'solo_anio'">
            📅 Adivina solo el <strong>Año</strong>
          </span>
          <span v-else-if="tipoPregunta === 'solo_artista'">
            🎤 Adivina solo el <strong>Artista</strong>
          </span>
          <span v-else>
            ⚠️ Tipo desconocido: "{{ tipoPregunta }}"
          </span>
        </div>
      </div>

      <!-- Audio Player -->
      <AudioPlayer
        v-if="cancion"
        :preview-url="cancion.preview_url"
        :loading="loading"
        @retry="cargarCancionRonda"
      />

      <!-- Formulario de pregunta -->
      <QuestionFormRondas
        v-if="!yaRespondido && cancion && cancion.preview_url && tipoPregunta"
        v-model:titulo="titulo"
        v-model:artista="artista"
        v-model:anio="anio"
        :tipo-pregunta="tipoPregunta"
        :disabled="yaRespondido"
        @submit="verificarRespuesta"
      />

      <!-- Results -->
      <Resultado v-if="resultado" :resultado="resultado" />
      <QR v-if="qr" :qr="qr" />

      <!-- Controls -->
      <GameControlsRondas
        v-if="cancion"
        :ya-respondido="yaRespondido"
        :ronda-terminada="rondaTerminada"
        @verificar="verificarRespuesta"
        @rendirse="rendirse"
        @siguiente="cargarCancionRonda"
      />
    </template>

    <!-- Ronda Terminada -->
    <div v-else-if="rondaTerminada" class="ronda-terminada-card">
      <h2>🎉 ¡Ronda Completada!</h2>
      <div class="resultado-final">
        <div class="puntos-finales">
          <span class="label">Puntos de esta ronda:</span>
          <span class="valor">{{ puntosRonda }} pts</span>
        </div>
        <div class="puntos-totales">
          <span class="label">Total acumulado:</span>
          <span class="valor">⭐ {{ puntosTotales }} pts</span>
        </div>
      </div>
      <div class="botones-finales">
        <button class="btn btn-verificar" @click="nuevaRonda">
          🔄 Nueva Ronda
        </button>
        <button class="btn btn-volver" @click="$emit('volver')">
          ⬅️ Volver al Menú
        </button>
      </div>
    </div>

    <!-- Botón volver (solo visible si NO terminó la ronda) -->
    <button v-if="rondaIniciada && !rondaTerminada" class="btn btn-volver" @click="volverConConfirmacion">
      ⬅️ Volver al Menú
    </button>

    <!-- Loading -->
    <div v-if="loading" style="text-align: center; padding: 20px;">
      <div style="font-size: 2rem;">⏳</div>
      <div>Cargando...</div>
    </div>
  </div>
</template>

<script>
import AudioPlayer from './AudioPlayer.vue'
import QuestionFormRondas from './QuestionFormRondas.vue'
import GameControlsRondas from './GameControlsRondas.vue'
import Resultado from '../shared/Resultado.vue'
import QR from '../shared/QR.vue'
import { PLAYLISTS } from '../../config/playlists'

export default {
  name: 'GameRondas',
  props: {
    usuario: Object,
    playlist: {
      type: String,
      required: true
    },
    token: {
      type: String,
      required: true
    }
  },
  emits: ['volver', 'actualizar-usuario'],
  components: {
    AudioPlayer,
    QuestionFormRondas,
    GameControlsRondas,
    Resultado,
    QR
  },
  data() {
    return {
      rondaIniciada: false,
      rondaTerminada: false,
      cancion: null,
      tipoPregunta: null,
      titulo: '',
      artista: '',
      anio: '',
      resultado: null,
      qr: null,
      yaRespondido: false,
      loading: false,
      estadoRonda: null,
      puntosRonda: 0,
      puntosTotales: 0,
      rondaMostradaUnaVez: false,

    }
  },
  computed: {
    playlistInfo() {
      return PLAYLISTS[this.playlist] || { nombre: 'Playlist', icon: '🎵' }
    }
  },
  mounted() {
    console.log('🎮 GameRondas montado con playlist:', this.playlist)
  },
  watch: {
    tipoPregunta(newVal, oldVal) {
      console.log('🎲 tipoPregunta cambió de', oldVal, 'a', newVal)
    }
  },
  methods: {
    async iniciarRonda() {
      console.log('🎲 Iniciando ronda...')
      this.loading = true
      try {
        const resp = await fetch(`/ronda/${this.playlist}/iniciar`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        })

        if (!resp.ok) {
          console.error('❌ Error iniciando ronda:', resp.status)
          return
        }

        const data = await resp.json()
        console.log('✅ Ronda iniciada:', data)

        this.rondaIniciada = true
        this.rondaMostradaUnaVez = true
        this.rondaTerminada = false

        await this.cargarCancionRonda()
      } catch (error) {
        console.error('❌ Error iniciando ronda:', error)
      } finally {
        this.loading = false
      }
    },

    async cargarCancionRonda() {
      console.log('🎵 Cargando canción...')
      this.limpiarEstado()
      this.loading = true

      try {
        const resp = await fetch(`/ronda/${this.playlist}/cancion`, {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })

        if (!resp.ok) {
          console.error('❌ Error cargando canción:', resp.status)
          return
        }

        const data = await resp.json()
        console.log('📦 Datos recibidos:', data)

        // Si la ronda terminó
        if (data.finalizar || data.error) {
          console.log('🏁 Ronda terminada o error:', data)
          this.finalizarRonda()
          return
        }

        // Asignar datos
        this.cancion = data
        this.tipoPregunta = data.tipo_pregunta

        console.log('✅ Canción cargada:', {
          preview: data.preview_url,
          tipo: data.tipo_pregunta
        })

        this.estadoRonda = {
          pregunta_numero: data.pregunta_numero,
          total_preguntas: data.total_preguntas,
          puntos_actuales: data.puntos_actuales || 0,
          racha_actual: data.racha_actual || 0
        }

        // Force update
        this.$forceUpdate()

      } catch (error) {
        console.error('❌ Error cargando canción:', error)
      } finally {
        this.loading = false
      }
    },

    limpiarEstado() {
      console.log('🧹 Limpiando estado...')
      this.resultado = null
      this.qr = null
      this.yaRespondido = false
      this.titulo = ''
      this.artista = ''
      this.anio = ''
    },

    async verificarRespuesta() {
  console.log('✅ Verificando respuesta...')
  if (!this.cancion || this.yaRespondido) {
    console.log('⚠️ No se puede verificar:', { cancion: !!this.cancion, yaRespondido: this.yaRespondido })
    return
  }

  try {
    const body = {}

    // Enviar SOLO el campo que corresponde
    if (this.tipoPregunta === 'solo_titulo') {
      if (!this.titulo.trim()) {
        this.resultado = { tipo: 'incorrecto', mensaje: '❌ Debes escribir un título' }
        return
      }
      body.titulo = this.titulo.trim()
      body.artista = ''
      body.anio = ''

    } else if (this.tipoPregunta === 'solo_anio') {
  const anioStr = String(this.anio || '').trim()
  if (!anioStr) {
    this.resultado = {
      tipo: 'incorrecto',
      mensaje: '❌ Debes escribir un año'
    }
    return
  }
  body.titulo = ''
  body.artista = ''
  body.anio = anioStr

    } else if (this.tipoPregunta === 'solo_artista') {
      if (!this.artista.trim()) {
        this.resultado = { tipo: 'incorrecto', mensaje: '❌ Debes escribir un artista' }
        return
      }
      body.titulo = ''
      body.artista = this.artista.trim()
      body.anio = ''
    }

    console.log('📤 Enviando al backend:', body)

    const resp = await fetch(`/ronda/${this.playlist}/verificar`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })

    // 👇 Esto permite ver si el backend responde con error JSON
    let data = null
    try {
      data = await resp.json()
    } catch (err) {
      console.warn('⚠️ No se pudo parsear JSON:', err)
    }

    console.log('📥 Respuesta del backend:', resp.status, data)

    // Mostrar mensaje si el backend devolvió error
    if (!resp.ok) {
      const mensaje = data?.mensaje || data?.error || `❌ Error HTTP ${resp.status}`
      console.error('⚠️ Backend devolvió error:', mensaje)
      this.resultado = { tipo: 'incorrecto', mensaje }
      return
    }

    // A partir de aquí solo si todo va bien
    this.yaRespondido = true
    this.estadoRonda = {
      pregunta_numero: data.pregunta_numero,
      total_preguntas: data.total_preguntas,
      puntos_actuales: data.puntos_totales,
      racha_actual: data.racha_actual
    }

    if (data.correcto) {
      this.resultado = { tipo: 'correcto', mensaje: data.mensaje }
      if (data.qr_code) {
        this.qr = {
          img: data.qr_code,
          url: data.spotify_url,
          titulo: data.titulo_real,
          artista: data.artista_real
        }
      }
    } else {
      this.resultado = { tipo: 'incorrecto', mensaje: data.mensaje }
    }

    if (data.ronda_terminada) {
      this.puntosRonda = data.puntos_totales
      this.puntosTotales = data.puntos_finales_usuario
      if (this.usuario) {
        this.usuario.puntos = data.puntos_finales_usuario
      }

      setTimeout(() => this.finalizarRonda(), 2000)
    }

  } catch (error) {
    console.error('❌ Error verificando respuesta (bloque catch):', error)
    this.resultado = {
      tipo: 'incorrecto',
      mensaje: '⚠️ Error inesperado verificando respuesta (ver consola)'
    }
  }
},

    async rendirse() {
      if (!this.cancion || this.yaRespondido) return

      try {
        const resp = await fetch(`/ronda/${this.playlist}/rendirse`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })

        if (!resp.ok) throw new Error('HTTP ' + resp.status)
        const data = await resp.json()

        this.yaRespondido = true
        this.resultado = {
          tipo: 'incorrecto',
          mensaje: `🏳️ Te rendiste. La respuesta era:<br><strong>${data.titulo_real}</strong> - ${data.artista_real}${data.anio_real ? ` (${data.anio_real})` : ''}`
        }

        if (data.qr_code) {
          this.qr = {
            img: data.qr_code,
            url: data.spotify_url,
            titulo: data.titulo_real,
            artista: data.artista_real
          }
        }

        this.estadoRonda = {
          pregunta_numero: data.pregunta_numero,
          total_preguntas: data.total_preguntas,
          puntos_actuales: data.puntos_totales,
          racha_actual: 0
        }

        if (data.ronda_terminada) {
          this.puntosRonda = data.puntos_totales
          this.puntosTotales = data.puntos_finales_usuario
          // 👇 avisa al componente padre (App.vue)
          this.$emit('actualizar-usuario', {
          ...this.usuario,
      puntos: data.puntos_finales_usuario
    })

          setTimeout(() => {
            this.finalizarRonda()
          }, 2000)
        }
      } catch (error) {
        console.error('Error al rendirse:', error)
      }
    },

    finalizarRonda() {
      console.log('🏁 Finalizando ronda')
      this.rondaTerminada = true
      this.rondaIniciada = false
    },

    nuevaRonda() {
      this.rondaTerminada = false
      this.estadoRonda = null
      this.puntosRonda = 0
      this.cancion = null
      this.tipoPregunta = null
      this.iniciarRonda()
    },

    volverConConfirmacion() {
      if (this.rondaIniciada && !this.rondaTerminada) {
        if (confirm('¿Seguro que quieres salir? Perderás el progreso de la ronda actual.')) {
          this.$emit('volver')
        }
      } else {
        this.$emit('volver')
      }
    }
  }
}
</script>


<style scoped>
.game-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  max-width: 100%;
}

.playlist-badge {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-radius: 20px;
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 50%, #fad0c4 100%);
  border: 1px solid rgba(255,255,255,0.2);
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}

.playlist-info {
  flex: 1;
}

.playlist-name {
  font-weight: 700;
  font-size: 1.1rem;
  color: #3b1e77;
}

.ronda-progreso {
  font-size: 0.9rem;
  color: #6a1b9a;
  font-weight: 600;
  margin-top: 0.25rem;
}

.racha-badge {
  display: inline-block;
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 8px;
  font-size: 0.8rem;
  margin-left: 0.5rem;
  animation: pulse 1s infinite;
}

.iniciar-ronda-card,
.ronda-terminada-card {
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.2), rgba(103, 58, 183, 0.2));
  border-radius: 24px;
  padding: 3rem 2rem;
  text-align: center;
  border: 1px solid rgba(255,255,255,0.3);
  backdrop-filter: blur(10px);
}

.iniciar-ronda-card h2,
.ronda-terminada-card h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: white;
}

.iniciar-ronda-card p {
  font-size: 1.1rem;
  color: rgba(255,255,255,0.8);
  margin-bottom: 2rem;
}

.dado-pregunta {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 20px;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  animation: fadeIn 0.5s ease;
}

.dado-icon {
  font-size: 2rem;
  animation: spin 2s ease-in-out;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.resultado-final {
  background: rgba(0,0,0,0.3);
  border-radius: 16px;
  padding: 2rem;
  margin: 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.puntos-finales,
.puntos-totales {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255,255,255,0.1);
  border-radius: 12px;
}

.label {
  color: rgba(255,255,255,0.8);
  font-weight: 600;
}

.valor {
  font-size: 1.5rem;
  font-weight: 800;
  color: #ffd700;
}

.botones-finales {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .dado-pregunta {
    flex-direction: column;
    text-align: center;
  }

  .botones-finales {
    flex-direction: column;
  }

  .botones-finales .btn {
    width: 100%;
  }
}
</style>
