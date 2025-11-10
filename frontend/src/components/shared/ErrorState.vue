<template>
  <div class="error-container">
    <div class="error-icon">{{ icon }}</div>
    <p class="error-message">{{ message }}</p>
    <button v-if="showRetry" class="btn btn-retry" @click="$emit('retry')">
      🔄 {{ retryText }}
    </button>
  </div>
</template>

<script>
export default {
  props: {
    message: {
      type: String,
      default: 'Ha ocurrido un error'
    },
    icon: {
      type: String,
      default: '😢'
    },
    showRetry: {
      type: Boolean,
      default: true
    },
    retryText: {
      type: String,
      default: 'Intentar de nuevo'
    }
  }
}
</script>

<style scoped>
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  background: rgba(231, 76, 60, 0.1);
  border: 1px solid rgba(231, 76, 60, 0.3);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.error-icon {
  font-size: 3rem;
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.error-message {
  color: white;
  font-weight: 600;
  text-align: center;
  margin: 0;
  font-size: 1rem;
}

.btn-retry {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(231, 76, 60, 0.3);
}

.btn-retry:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
}
</style>
