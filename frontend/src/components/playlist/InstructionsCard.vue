<template>
  <div class="instrucciones-card">
    <button @click="$emit('close')" class="btn-cerrar">✕</button>

    <div class="instrucciones-contenido">
      <h2>{{ titulo }}</h2>

      <div class="instrucciones-texto">
        <!-- Contenido específico según el modo -->
        <slot></slot>
      </div>

      <button
        v-if="showContinue"
        @click="$emit('continue')"
        class="btn btn-continuar"
      >
        Continuar a Playlists →
      </button>

      <button
        v-else
        @click="$emit('close')"
        class="btn btn-volver"
      >
        ← Volver a Modos
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    titulo: {
      type: String,
      required: true
    },
    showContinue: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.instrucciones-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  width: 100%;
  max-width: 600px;
  position: relative;
  animation: fadeIn 0.5s ease;
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

.btn-cerrar {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 1.25rem;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cerrar:hover {
  background: rgba(255, 68, 68, 0.3);
  transform: rotate(90deg);
}

.instrucciones-contenido h2 {
  font-size: 1.75rem;
  margin-bottom: 1.5rem;
  text-align: center;
  color: white;
}

.instrucciones-texto {
  margin-bottom: 1.5rem;
}

.instrucciones-texto h3 {
  font-size: 1.1rem;
  margin: 1rem 0 0.5rem;
  color: white;
}

.instrucciones-texto ul {
  list-style: none;
  padding-left: 0;
}

.instrucciones-texto li {
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
  color: rgba(255, 255, 255, 0.9);
}

.instrucciones-texto li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: #9c27b0;
  font-weight: bold;
}

.proximamente-banner {
  background: linear-gradient(135deg, #f39c12, #e67e22);
  padding: 1rem;
  border-radius: 12px;
  text-align: center;
  margin: 1rem 0;
  font-weight: 700;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

.proximamente-info {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-style: italic;
  margin-top: 1rem;
}

.btn-continuar,
.btn-volver {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-continuar {
  background: linear-gradient(135deg, #00c851, #007e33);
  color: white;
  box-shadow: 0 8px 32px rgba(0, 200, 81, 0.3);
}

.btn-continuar:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 200, 81, 0.4);
}

.btn-volver {
  background: linear-gradient(135deg, #2196f3, #0d47a1);
  color: white;
  box-shadow: 0 8px 32px rgba(33, 150, 243, 0.3);
}

.btn-volver:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(33, 150, 243, 0.4);
}

@media (max-width: 768px) {
  .instrucciones-card {
    padding: 1.5rem;
  }

  .instrucciones-contenido h2 {
    font-size: 1.5rem;
  }
}
</style>
