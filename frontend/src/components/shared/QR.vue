<template>
  <div class="qr-section">
    <div class="qr-header">
      <div class="qr-icon">🎵</div>
      <h4>Escanea para abrir en Spotify</h4>
    </div>

    <div class="qr-content">
      <div class="qr-image-container">
        <img :src="qr.img" :alt="`QR Code para ${qr.titulo} - ${qr.artista}`" class="qr-image" />
        <div class="qr-overlay">
          <div class="scan-animation"></div>
        </div>
      </div>

      <div class="song-info">
        <h5>{{ qr.titulo }}</h5>
        <p>{{ qr.artista }}</p>
      </div>

      <a :href="qr.url" target="_blank" class="spotify-button">
        <svg class="spotify-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.42 1.56-.299.421-1.02.599-1.559.3z"/>
        </svg>
        Abrir en Spotify
      </a>
    </div>
  </div>
</template>

<script>
export default {
  props: ['qr']
}
</script>

<style scoped>
.qr-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  animation: slideInScale 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center;
}

@keyframes slideInScale {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.qr-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.qr-icon {
  font-size: 2rem;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3));
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.qr-header h4 {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.qr-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.qr-image-container {
  position: relative;
  display: inline-block;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  overflow: hidden;
}

.qr-image {
  display: block;
  width: 180px;
  height: 180px;
  border-radius: 12px;
  transition: transform 0.3s ease;
}

.qr-overlay {
  position: absolute;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  bottom: 1rem;
  border-radius: 12px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.qr-image-container:hover .qr-overlay {
  opacity: 1;
}

.qr-image-container:hover .qr-image {
  transform: scale(1.02);
}

.scan-animation {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #1db954, transparent);
  animation: scan 2s ease-in-out infinite;
}

@keyframes scan {
  0% { transform: translateY(0); }
  100% { transform: translateY(176px); }
}

.song-info {
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem 1.5rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  min-width: 200px;
}

.song-info h5 {
  color: white;
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
  text-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.song-info p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
  font-weight: 500;
  margin: 0;
  text-shadow: 0 1px 5px rgba(0,0,0,0.2);
}

.spotify-button {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  background: linear-gradient(135deg, #1db954, #1ed760);
  color: white;
  padding: 1rem 2rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 32px rgba(29, 185, 84, 0.3);
  position: relative;
  overflow: hidden;
}

.spotify-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s ease;
}

.spotify-button:hover::before {
  left: 100%;
}

.spotify-button:hover {
  background: linear-gradient(135deg, #1ed760, #17c653);
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(29, 185, 84, 0.4);
  text-decoration: none;
  color: white;
}

.spotify-button:active {
  transform: translateY(-1px);
}

.spotify-icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

/* Responsive Design */
@media (max-width: 768px) {
  .qr-section {
    padding: 1.5rem;
    border-radius: 20px;
  }

  .qr-image-container {
    padding: 0.75rem;
  }

  .qr-image {
    width: 150px;
    height: 150px;
  }

  .scan-animation {
    animation-name: scanMobile;
  }

  @keyframes scanMobile {
    0% { transform: translateY(0); }
    100% { transform: translateY(146px); }
  }

  .qr-header h4 {
    font-size: 1.1rem;
  }

  .spotify-button {
    padding: 0.875rem 1.75rem;
    font-size: 0.95rem;
  }

  .song-info {
    padding: 0.875rem 1.25rem;
    min-width: 180px;
  }
}

@media (max-width: 480px) {
  .qr-section {
    padding: 1rem;
    border-radius: 16px;
  }

  .qr-content {
    gap: 1rem;
  }

  .qr-image-container {
    padding: 0.5rem;
    border-radius: 16px;
  }

  .qr-image {
    width: 120px;
    height: 120px;
    border-radius: 8px;
  }

  .scan-animation {
    animation-name: scanSmall;
  }

  @keyframes scanSmall {
    0% { transform: translateY(0); }
    100% { transform: translateY(116px); }
  }

  .qr-icon {
    font-size: 1.5rem;
  }

  .qr-header h4 {
    font-size: 1rem;
  }

  .song-info {
    padding: 0.75rem 1rem;
    min-width: 160px;
    border-radius: 12px;
  }

  .song-info h5 {
    font-size: 1rem;
  }

  .song-info p {
    font-size: 0.9rem;
  }

  .spotify-button {
    padding: 0.75rem 1.5rem;
    font-size: 0.9rem;
    border-radius: 40px;
  }

  .spotify-icon {
    width: 18px;
    height: 18px;
  }
}
</style>
