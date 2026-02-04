<template>
  <nav class="admin-navbar">
    <div class="navbar-content">
      <div class="navbar-brand">
        <h1>🎯 Panel de Administración</h1>
        <p>PetruWorkout</p>
      </div>

      <div class="navbar-user">
        <div class="user-info">
          <span class="user-icon">👤</span>
          <div class="user-details">
            <span class="user-name">{{ admin.nombre }}</span>
            <span class="user-email">{{ admin.email }}</span>
          </div>
        </div>

        <button @click="$emit('logout')" class="btn-logout">
          🚪 Cerrar Sesión
        </button>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'AdminNavbar',
  props: {
    admin: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.admin-navbar {
  background: rgba(0, 0, 0, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.navbar-content {
  max-width: 1800px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.navbar-brand h1 {
  font-size: 1.5rem;
  color: white;
  margin: 0;
  font-weight: 800;
}

.navbar-brand p {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin: 0;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.user-icon {
  font-size: 1.5rem;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.user-email {
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.btn-logout {
  padding: 0.75rem 1.5rem;
  background: rgba(239, 35, 60, 0.2);
  border: 1px solid rgba(239, 35, 60, 0.4);
  border-radius: 8px;
  color: #ff6b6b;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-logout:hover {
  background: rgba(239, 35, 60, 0.3);
  transform: translateY(-2px);
}

@media (max-width: 968px) {
  .admin-navbar {
    padding: 1rem;
  }

  .navbar-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .navbar-brand {
    text-align: center;
  }

  .navbar-user {
    flex-direction: column;
    align-items: stretch;
  }

  .user-info {
    justify-content: center;
  }

  .btn-logout {
    width: 100%;
  }
}
</style>
