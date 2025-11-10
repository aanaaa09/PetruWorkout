<template>
  <div class="audio-section">
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>🎧 Cargando nueva canción...</p>
    </div>

    <div v-else-if="previewUrl" class="audio-player">
      <div class="audio-header">
        <h3>🎧 Escucha y adivina</h3>
      </div>
      <audio controls :src="previewUrl" class="modern-audio"></audio>
    </div>

    <div v-else class="error-state">
      <div class="error-icon">😢</div>
      <p>No se pudo cargar la canción</p>
      <button class="btn btn-siguiente" @click="$emit('retry')">
        🔄 Intentar otra
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    previewUrl: String,
    loading: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.audio-section {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
  border-radius: 24px;
  padding: 2rem;
  border: 1px solid rgba(255,255,255,0.2);
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  text-align: center;
}

.audio-header h3 {
  color: #ff6f61;
  font-weight: 700;
  font-size: 1.3rem;
  text-shadow: 0 2px 8px rgba(0,0,0,0.2);
  margin: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: white;
  font-weight: 500;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-left: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.audio-player {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.modern-audio {
  width: 100%;
  height: 60px;
  border-radius: 16px;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
}

.modern-audio::-webkit-media-controls-panel {
  background-color: rgba(0,0,0,0.3);
  border-radius: 16px;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: white;
}

.error-icon {
  font-size: 3rem;
}

@media (max-width: 768px) {
  .audio-section {
    padding: 1.5rem;
    border-radius: 20px;
  }

  .modern-audio {
    height: 50px;
  }
}

@media (max-width: 480px) {
  .audio-section {
    padding: 1rem;
    border-radius: 16px;
  }

  .modern-audio {
    height: 45px;
    border-radius: 12px;
  }
}
</style>
