<template>
  <div class="app-container">
    <div class="blur-layer"></div>

    <AppHeader
      :usuario-logueado="!!usuarioActual"
      @mostrar-ranking="mostrarRanking = true"
      @mostrar-añadir-cancion="modalAñadirCancion = true"
    />

    <div class="main-content">
      <Auth v-if="!usuarioActual" @login="iniciarSesion" />

      <Ranking v-else-if="mostrarRanking" @cerrar="mostrarRanking = false" />

      <template v-else>
        <UserInfo
          :usuario="usuarioActual"
          @logout="cerrarSesion"
        />

        <PlaylistSelector
          v-if="!modoYPlaylist"
          @select="seleccionarModoYPlaylist"
        />

        <!-- NUEVO: Configuración de jugadores para modo tablero -->
        <PlayerSetup
          v-else-if="modoYPlaylist.modo === 'tablero' && !jugadoresTablero"
          :playlist="modoYPlaylist.playlist"
          @jugadores-listos="iniciarTablero"
        />

        <!-- Game Individual -->
        <Game
          v-else-if="modoYPlaylist.modo === 'tablero' && jugadoresTablero"
          :playlist="modoYPlaylist.playlist"
          :jugadores="jugadoresTablero"
          @volver="volverSeleccion"
        />

        <!-- Game Rondas -->
        <GameRondas
          v-else-if="modoYPlaylist.modo === 'individual'"
          :playlist="modoYPlaylist.playlist"
          :token="token"
          :usuario="usuarioActual"
          @volver="volverSeleccion"
          @actualizar-usuario="usuarioActual = $event"
        />
      </template>
    </div>

    <AñadirCancionModal
      :mostrar="modalAñadirCancion"
      @cerrar="modalAñadirCancion = false"
    />
  </div>
</template>

<script>
import AppHeader from './components/layout/AppHeader.vue'
import UserInfo from './components/layout/UserInfo.vue'
import Auth from './components/auth/Auth.vue'
import PlaylistSelector from './components/playlist/PlaylistSelector.vue'
import PlayerSetup from './components/tablero/PlayerSetup.vue'
import Game from './components/game/Game.vue'
import GameRondas from './components/game/GameRondas.vue'
import Ranking from './components/ranking/Ranking.vue'
import AñadirCancionModal from './components/AñadirCancionModal.vue'

export default {
  components: {
    AppHeader,
    UserInfo,
    Auth,
    PlaylistSelector,
    PlayerSetup,
    Game,
    GameRondas,
    Ranking,
    AñadirCancionModal
  },
  data() {
    return {
      usuarioActual: null,
      token: null,
      modoYPlaylist: null,
      jugadoresTablero: null,
      mostrarRanking: false,
      modalAñadirCancion: false
    }
  },
  methods: {
    iniciarSesion(data) {
      this.usuarioActual = data.usuario
      this.token = data.token
    },

    async cerrarSesion() {
      if (this.token) {
        try {
          await fetch('http://localhost:5000/api/auth/logout', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token: this.token })
          })
        } catch (err) {
          console.error('Error cerrando sesión:', err)
        }
      }
      this.usuarioActual = null
      this.token = null
      this.modoYPlaylist = null
      this.jugadoresTablero = null
      this.mostrarRanking = false
    },

    seleccionarModoYPlaylist(data) {
      this.modoYPlaylist = data

      // Si es modo individual, no necesita configuración de jugadores
      if (data.modo === 'individual') {
        this.jugadoresTablero = null
      }
    },

    iniciarTablero(data) {
      console.log('🎮 Jugadores configurados:', data)
      this.jugadoresTablero = data
    },

    volverSeleccion() {
      // Cerrar sesiones de jugadores temporales (invitados y secundarios)
      if (this.jugadoresTablero) {
        this.cerrarSesionesTemporales()
      }

      this.modoYPlaylist = null
      this.jugadoresTablero = null
    },

    async cerrarSesionesTemporales() {
      if (!this.jugadoresTablero) return

      const { jugadores } = this.jugadoresTablero

      for (const jugador of jugadores) {
        if (jugador.esPareja) {
          // Cerrar sesión de miembros de pareja (excepto el usuario principal)
          if (jugador.miembro1 && jugador.miembro1.token && jugador.miembro1.email !== this.usuarioActual?.email) {
            await this.cerrarSesionToken(jugador.miembro1.token)
          }
          if (jugador.miembro2 && jugador.miembro2.token && jugador.miembro2.email !== this.usuarioActual?.email) {
            await this.cerrarSesionToken(jugador.miembro2.token)
          }
        } else {
          // Cerrar sesión de jugador individual (excepto el usuario principal)
          if (jugador.token && jugador.email !== this.usuarioActual?.email) {
            await this.cerrarSesionToken(jugador.token)
          }
        }
      }
    },

    async cerrarSesionToken(token) {
      try {
        await fetch('http://localhost:5000/api/auth/logout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token })
        })
      } catch (err) {
        console.error('Error cerrando sesión temporal:', err)
      }
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
