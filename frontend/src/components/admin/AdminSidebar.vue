<template>
  <aside class="admin-sidebar">
    <nav class="sidebar-nav">
      <button
        v-for="item in menuItems"
        :key="item.id"
        @click="$emit('change-section', item.id)"
        class="nav-item"
        :class="{ 'active': activeSection === item.id }"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
      </button>
    </nav>
  </aside>
</template>

<script>
export default {
  name: 'AdminSidebar',
  props: {
    activeSection: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      menuItems: [
        {
          id: 'dashboard',
          icon: '📊',
          label: 'Dashboard'
        },
        {
          id: 'emails',
          icon: '📧',
          label: 'Enviar Emails'
        },
        {
          id: 'users',
          icon: '👥',
          label: 'Usuarios'
        },
        {
          id: 'password',
          icon: '🔐',
          label: 'Cambiar Contraseña'
        }
      ]
    }
  }
}
</script>

<style scoped>
.admin-sidebar {
  width: 280px;
  background: rgba(0, 0, 0, 0.4);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  padding: 2rem 1rem;
  position: sticky;
  top: 80px;
  height: calc(100vh - 80px);
  overflow-y: auto;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  color: var(--color-text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.2) 0%, rgba(6, 214, 160, 0.1) 100%);
  border-color: var(--color-accent);
  color: white;
}

.nav-icon {
  font-size: 1.5rem;
}

.nav-label {
  font-size: 0.95rem;
}

@media (max-width: 968px) {
  .admin-sidebar {
    width: 100%;
    height: auto;
    position: static;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 1rem;
  }

  .sidebar-nav {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .nav-item {
    flex: 1;
    min-width: 150px;
    justify-content: center;
  }

  .nav-label {
    display: none;
  }

  .nav-icon {
    font-size: 1.75rem;
  }
}
</style>
