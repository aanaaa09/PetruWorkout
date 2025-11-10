<template>
  <div class="resultado-container" :class="resultado.tipo">
    <div class="resultado-icon">
      <div class="icon-wrapper">
        <span v-if="resultado.tipo === 'correcto'">🎉</span>
        <span v-else-if="resultado.tipo === 'parcial'">⚡</span>
        <span v-else>❌</span>
      </div>
    </div>

    <div class="resultado-content">
      <div class="resultado-message" v-html="resultado.mensaje"></div>
    </div>

    <div class="resultado-decoration">
      <div class="decoration-particle" v-for="n in 6" :key="n"></div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['resultado']
}
</script>

<style scoped>
.resultado-container {
  position: relative;
  margin: 1.5rem 0;
  padding: 2rem;
  border-radius: 24px;
  font-weight: 600;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0,0,0,0.15);
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  animation: resultSlideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  text-align: left;
  background-color: rgba(0,0,0,0.85); /* Fondo sólido semi-opaco para visibilidad */
  color: #fff; /* Letras blancas para resaltar */
}

/* Correcto */
.resultado-container.correcto {
  background: linear-gradient(135deg, #27ae60, #2ecc71); /* Verde vibrante */
  color: #fff;
  border-color: #27ae60;
  box-shadow: 0 8px 32px rgba(39,174,96,0.4);
}

/* Incorrecto */
.resultado-container.incorrecto {
  background: linear-gradient(135deg, #c0392b, #e74c3c); /* Rojo vibrante */
  color: #fff;
  border-color: #c0392b;
  box-shadow: 0 8px 32px rgba(231,76,60,0.4);
}

/* Parcial */
.resultado-container.parcial {
  background: linear-gradient(135deg, #f39c12, #f1c40f); /* Naranja vibrante */
  color: #fff;
  border-color: #f39c12;
  box-shadow: 0 8px 32px rgba(243,156,18,0.4);
}


.resultado-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-wrapper {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 2rem;
  position: relative;
  background: rgba(255, 255, 255, 0.1); /* Fondo ligero para resaltar el emoji */
  backdrop-filter: blur(10px);
  animation: iconBounce 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  box-shadow: 0 2px 12px rgba(0,0,0,0.3); /* Sombra para dar contraste */
}

.resultado-container.incorrecto .icon-wrapper {
  background: rgba(255, 255, 255, 0.2); /* Fondo claro detrás del emoji */
  border: 2px solid #c0392b;
  box-shadow: 0 4px 16px rgba(231, 76, 60, 0.4);
}

.resultado-container.incorrecto .icon-wrapper span {
  text-shadow: 0 2px 8px rgba(0,0,0,0.6), 0 0 2px rgba(255,255,255,0.5); /* Resalta el emoji */
  font-size: 2.2rem; /* Un poquito más grande */
}

@keyframes iconBounce {
  0% { opacity: 0; transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { opacity: 1; transform: scale(1); }
}

.resultado-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.resultado-message {
  font-size: 1.1rem;
  line-height: 1.5;
  text-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.resultado-message strong {
  font-weight: 800;
  text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.resultado-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
  border-radius: 24px;
}

.decoration-particle {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  opacity: 0.6;
}

.resultado-container.correcto .decoration-particle {
  background: #27ae60;
  animation: floatUp 3s ease-in-out infinite;
}

.resultado-container.incorrecto .decoration-particle {
  background: #c0392b;
  animation: floatSide 2s ease-in-out infinite;
}

.resultado-container.parcial .decoration-particle {
  background: #f39c12;
  animation: sparkle 2.5s ease-in-out infinite;
}

.decoration-particle:nth-child(1) { top: 20%; left: 10%; animation-delay: 0s; }
.decoration-particle:nth-child(2) { top: 60%; left: 20%; animation-delay: 0.5s; }
.decoration-particle:nth-child(3) { top: 30%; right: 15%; animation-delay: 1s; }
.decoration-particle:nth-child(4) { bottom: 40%; left: 80%; animation-delay: 1.5s; }
.decoration-particle:nth-child(5) { top: 80%; right: 25%; animation-delay: 2s; }
.decoration-particle:nth-child(6) { bottom: 20%; right: 10%; animation-delay: 2.5s; }

@keyframes floatUp {
  0%, 100% { transform: translateY(0px) scale(1); opacity: 0.6; }
  50% { transform: translateY(-20px) scale(1.2); opacity: 1; }
}

@keyframes floatSide {
  0%, 100% { transform: translateX(0px) scale(1); opacity: 0.6; }
  50% { transform: translateX(20px) scale(1.2); opacity: 1; }
}

@keyframes sparkle {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.5); opacity: 1; }
}
</style>
