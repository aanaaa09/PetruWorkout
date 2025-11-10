<template>
  <div class="game-wrapper">
    <!-- Playlist Badge -->
    <div class="playlist-badge">
      <div class="playlist-icon">🎵</div>
      <div class="playlist-name">{{ playlistInfo.nombre }}</div>
    </div>

    <!-- Audio Player -->
    <AudioPlayer
      :preview-url="cancion?.preview_url"
      :loading="loading"
      @retry="cargarCancion"
    />

    <!-- Question Form -->
    <QuestionForm
      v-if="!yaRespondido && cancion?.preview_url"
      :titulo.sync="titulo"
      :artista.sync="artista"
      @submit="verificarRespuesta"
    />

    <!-- Results -->
    <Resultado v-if="resultado" :resultado="resultado" />
    <QR v-if="qr" :qr="qr" />

    <!-- Controls -->
    <GameControls
      :ya-respondido="yaRespondido"
      @verificar="verificarRespuesta"
      @rendirse="rendirse"
      @siguiente="cargarCancion"
      @volver="$emit('volver')"
    />
  </div>
</template>

<script>
import AudioPlayer from './AudioPlayer.vue'
import QuestionForm from './QuestionForm.vue'
import GameControls from './GameControls.vue'
import Resultado from '../shared/Resultado.vue'
import QR from '../shared/QR.vue'
import { PLAYLISTS } from '../../config/playlists'

export default {
  props: ['playlist'],
  components: {
    AudioPlayer,
    QuestionForm,
    GameControls,
    Resultado,
    QR
  },
  data() {
    return {
      cancion: null,
      titulo: '',
      artista: '',
      resultado: null,
      qr: null,
      yaRespondido: false,
      loading: false
    }
  },
  computed: {
    playlistInfo() {
      return PLAYLISTS[this.playlist] || { nombre: 'Playlist', icono: '🎵' }
    }
  },
  mounted() {
    this.sincronizarYcargar()
  },
  methods: {
    async sincronizarYcargar() {
      this.loading = true
      try {
        const resp = await fetch(`/sync/${this.playlist}`)
        if (!resp.ok) {
          console.warn('Sincronización devolvió status:', resp.status)
        }
        await this.cargarCancion()
      } catch (error) {
        console.error('Error sincronizando playlist:', error)
        await this.cargarCancion()
      } finally {
        this.loading = false
      }
    },

    async cargarCancion() {
      this.limpiarEstado()
      this.loading = true
      try {
        const resp = await fetch(`/cancion/${this.playlist}`)
        if (!resp.ok) {
          console.error('Error HTTP cargando canción:', resp.status)
          this.cancion = null
          return
        }
        const data = await resp.json()
        this.cancion = data
      } catch (error) {
        console.error('Error cargando canción:', error)
        this.cancion = null
      } finally {
        this.loading = false
      }
    },

    limpiarEstado() {
      this.resultado = null
      this.qr = null
      this.yaRespondido = false
      this.titulo = ''
      this.artista = ''
    },

    async verificarRespuesta() {
      if (!this.cancion || this.yaRespondido) return

      try {
        const resp = await fetch(`/verificar/${this.playlist}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            titulo: this.titulo.trim(),
            artista: this.artista.trim()
          })
        })

        if (!resp.ok) {
          throw new Error('HTTP ' + resp.status)
        }

        const data = await resp.json()

        if (data.correcto) {
          this.yaRespondido = true
          this.resultado = {
            tipo: 'correcto',
            mensaje: `🎉 ¡Correcto!<br><strong>${data.titulo_real}</strong> - ${data.artista_real}`
          }
          this.qr = {
            img: data.qr_code,
            url: data.spotify_url,
            titulo: data.titulo_real,
            artista: data.artista_real
          }
        } else {
          const tipoResultado = data.titulo_correcto || data.artista_correcto ? 'parcial' : 'incorrecto'
          this.resultado = {
            tipo: tipoResultado,
            mensaje: data.mensaje
          }
        }
      } catch (error) {
        console.error('Error verificando respuesta:', error)
        this.resultado = {
          tipo: 'incorrecto',
          mensaje: 'Error al verificar la respuesta 😞'
        }
      }
    },

    async rendirse() {
      if (!this.cancion || this.yaRespondido) return

      try {
        const resp = await fetch(`/rendirse/${this.playlist}`)
        if (!resp.ok) throw new Error('HTTP ' + resp.status)
        const data = await resp.json()

        this.yaRespondido = true
        this.resultado = {
          tipo: 'incorrecto',
          mensaje: `🏳️ Te rendiste. La respuesta era:<br><strong>${data.titulo_real}</strong> - ${data.artista_real}`
        }
        this.qr = {
          img: data.qr_code,
          url: data.spotify_url,
          titulo: data.titulo_real,
          artista: data.artista_real
        }
      } catch (error) {
        console.error('Error al rendirse:', error)
        this.resultado = {
          tipo: 'incorrecto',
          mensaje: 'Error al obtener la respuesta 😞'
        }
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

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  backdrop-filter: blur(10px);
}

.playlist-icon {
  font-size: 1.5rem;
}

.playlist-name {
  font-weight: 700;
  font-size: 1.1rem;
  color: #3b1e77;
  text-shadow: 1px 1px 4px rgba(255,255,255,0.3);
}

@media (max-width: 768px) {
  .game-wrapper {
    gap: 1.5rem;
  }

  .playlist-badge {
    padding: 0.875rem 1.25rem;
    gap: 0.75rem;
  }

  .playlist-name {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .game-wrapper {
    gap: 1rem;
  }

  .playlist-badge {
    padding: 0.75rem 1rem;
    border-radius: 16px;
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }

  .playlist-icon {
    font-size: 1.25rem;
  }

  .playlist-name {
    font-size: 0.9rem;
  }
}
</style>
