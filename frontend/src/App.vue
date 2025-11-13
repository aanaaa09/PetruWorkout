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

        <Game
          v-else-if="modoYPlaylist.modo === 'tablero'"
          :playlist="modoYPlaylist.playlist"
          @volver="volverSeleccion"
        />

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

    <!-- MODAL FUERA DEL main-content -->
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
      this.mostrarRanking = false
    },
    seleccionarModoYPlaylist(data) {
      this.modoYPlaylist = data
    },
    volverSeleccion() {
      this.modoYPlaylist = null
    }
  }
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body, html {
  font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
  height: 100vh;
  overflow-x: hidden;
  color: white;
  background: linear-gradient(135deg, #2c1a4a 0%, #4a2cd4 50%, #2c1a4a 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

#app {
  height: 100vh;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  width: 100%;
  backdrop-filter: blur(20px);
}

.blur-layer {
  position: fixed;
  inset: 0;
  backdrop-filter: blur(20px);
  z-index: 0;
  pointer-events: none;
}

.main-content {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  gap: 1.5rem;
}

.btn {
  padding: 0.875rem 2rem;
  border: none;
  border-radius: 16px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-transform: none;
  letter-spacing: -0.01em;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255,255,255,0.1), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.btn:hover::before {
  opacity: 1;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}

.btn:active {
  transform: translateY(0);
}

.btn-verificar {
  background: linear-gradient(135deg, #00c851, #007e33);
  color: white;
  box-shadow: 0 8px 32px rgba(0, 200, 81, 0.3);
}

.btn-rendirse {
  background: linear-gradient(135deg, #ff4444, #cc0000);
  color: white;
  box-shadow: 0 8px 32px rgba(255, 68, 68, 0.3);
}

.btn-siguiente {
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  color: white;
  box-shadow: 0 8px 32px rgba(156, 39, 176, 0.3);
}

.btn-volver {
  background: linear-gradient(135deg, #2196f3, #0d47a1);
  color: white;
  box-shadow: 0 8px 32px rgba(33, 150, 243, 0.3);
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem 0.75rem;
    gap: 1rem;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 0.75rem 0.5rem;
    gap: 0.875rem;
  }

  .btn {
    padding: 0.625rem 1.25rem;
    font-size: 0.85rem;
    border-radius: 12px;
  }
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
</style>
