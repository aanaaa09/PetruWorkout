<template>
  <div class="playlists-container">
    <button @click="$emit('back')" class="btn-volver-instrucciones">
      ← Ver Instrucciones
    </button>

    <h2 class="playlists-titulo">🎵 Elige tu Playlist</h2>

    <div class="playlist-selector">
      <button
        v-for="(playlist, key) in playlists"
        :key="key"
        class="playlist-btn"
        @click="$emit('select', key)"
        :style="{
          background: playlist.gradient,
          boxShadow: `0 8px 32px ${playlist.shadow}`
        }"
      >
        <span class="icono">{{ playlist.icon }}</span>
        <span class="nombre">{{ playlist.nombre }}</span>
      </button>
    </div>
  </div>
</template>

<script>
import { PLAYLISTS } from '../../config/playlists'

export default {
  data() {
    return {
      playlists: PLAYLISTS
    }
  }
}
</script>

<style scoped>
.playlists-container {
  width: 100%;
  text-align: center;
  animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.btn-volver-instrucciones {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
}
.btn-volver-instrucciones:hover {
  background: rgba(255,255,255,0.2);
}

.playlists-titulo {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: white;
}

.playlist-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.playlist-btn {
  border: none;
  border-radius: 18px;
  padding: 1.25rem 1rem;
  font-size: 1.05rem;
  font-weight: 600;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  text-shadow: 0 2px 6px rgba(0,0,0,0.25);
}

/* 🎮 El botón de Juego Clásico ocupa las dos columnas */
.playlist-btn:first-child {
  grid-column: 1 / 3;
}

.playlist-btn:hover {
  transform: translateY(-4px);
  filter: brightness(1.1);
}

.icono {
  font-size: 1.6rem;
  margin-bottom: 0.4rem;
}

@media (max-width: 768px) {
  .playlist-selector {
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }

  .playlist-btn {
    padding: 1rem;
    font-size: 0.9rem;
  }

  .playlist-btn:first-child {
    grid-column: 1 / 3;
  }
}

@media (max-width: 480px) {
  .playlist-selector {
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }

  .playlist-btn {
    padding: 0.6rem;
    font-size: 0.85rem;
    border-radius: 12px;
  }

  .playlist-btn:first-child {
    grid-column: 1 / 3;
  }
}
</style>

