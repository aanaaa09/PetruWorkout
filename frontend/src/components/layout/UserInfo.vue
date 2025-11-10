<template>
  <div class="user-info">
    <div class="user-details">
      <span class="user-name">👤 {{ usuario.nombre }}</span>
      <span class="user-points">⭐ {{ usuario.puntos }} puntos</span>
    </div>
    <button @click="$emit('logout')" class="btn btn-logout">
      Cerrar Sesión
    </button>
  </div>
</template>

<script>
export default {
  props: {
    usuario: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.user-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  margin-bottom: 1.5rem;
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

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  font-weight: 600;
  font-size: 1rem;
  color: white;
}

.user-points {
  font-weight: 700;
  font-size: 1.1rem;
  color: #ffd700;
  text-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
}

.btn-logout {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(231, 76, 60, 0.3);
}

.btn-logout:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
}

@media (max-width: 768px) {
  .user-info {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .btn-logout {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .user-name {
    font-size: 0.9rem;
  }

  .user-points {
    font-size: 1rem;
  }
}
</style>
