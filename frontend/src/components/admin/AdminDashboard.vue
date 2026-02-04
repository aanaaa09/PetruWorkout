<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h2>📊 Dashboard</h2>
      <p>Panel de control principal</p>
    </div>

    <div class="dashboard-content">
      <div class="coming-soon">
        <span class="icon">🚧</span>
        <h3>Próximamente</h3>
        <p>Estadísticas y métricas del sistema estarán disponibles aquí.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard'
}
</script>

<style scoped>
.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h2 {
  font-size: 2rem;
  color: white;
  margin: 0 0 0.5rem 0;
}

.dashboard-header p {
  color: var(--color-text-muted);
  font-size: 1rem;
  margin: 0;
}

.dashboard-content {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 4rem 2rem;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.coming-soon {
  text-align: center;
  max-width: 500px;
}

.coming-soon .icon {
  font-size: 5rem;
  display: block;
  margin-bottom: 1.5rem;
  animation: pulse 2s infinite;
}

.coming-soon h3 {
  font-size: 1.75rem;
  color: white;
  margin: 0 0 1rem 0;
}

.coming-soon p {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@media (max-width: 640px) {
  .dashboard-header h2 {
    font-size: 1.5rem;
  }

  .dashboard-content {
    padding: 3rem 1.5rem;
  }

  .coming-soon .icon {
    font-size: 4rem;
  }

  .coming-soon h3 {
    font-size: 1.5rem;
  }

  .coming-soon p {
    font-size: 1rem;
  }
}
</style>
