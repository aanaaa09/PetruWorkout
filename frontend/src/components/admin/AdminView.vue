<template>
  <div class="admin-view">
    <!-- Vista de Login si no está autenticado -->
    <AdminLogin
      v-if="!isAuthenticated"
      @login-success="handleLoginSuccess"
    />

    <!-- Panel de administración si está autenticado -->
    <div v-else class="admin-panel">
      <AdminNavbar
        :admin="currentAdmin"
        @logout="handleLogout"
      />

      <div class="admin-container">
        <AdminSidebar
          :active-section="activeSection"
          @change-section="changeSection"
        />

        <div class="admin-content">
          <!-- Dashboard -->
          <AdminDashboard
            v-if="activeSection === 'dashboard'"
          />

          <!-- Gestión de Contraseña -->
          <AdminPassword
            v-if="activeSection === 'password'"
          />

          <!-- Gestión de Emails -->
          <AdminEmails
            v-if="activeSection === 'emails'"
          />

          <!-- Gestión de Usuarios (opcional futuro) -->
          <AdminUsers
            v-if="activeSection === 'users'"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdminLogin from '@/components/admin/AdminLogin.vue'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import AdminDashboard from '@/components/admin/AdminDashboard.vue'
import AdminPassword from '@/components/admin/AdminPassword.vue'
import AdminEmails from '@/components/admin/AdminEmails.vue'
import AdminUsers from '@/components/admin/AdminUsers.vue'

export default {
  name: 'AdminView',
  components: {
    AdminLogin,
    AdminNavbar,
    AdminSidebar,
    AdminDashboard,
    AdminPassword,
    AdminEmails,
    AdminUsers
  },
  data() {
    return {
      isAuthenticated: false,
      currentAdmin: null,
      activeSection: 'dashboard'
    }
  },
  mounted() {
    this.checkAuth()
  },
  methods: {
    async checkAuth() {
      const token = localStorage.getItem('admin_token')

      if (!token) {
        this.isAuthenticated = false
        return
      }

      try {
        const response = await fetch('https://petruworkout-production.up.railway.app/api/admin/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token })
        })

        const data = await response.json()

        if (data.valid) {
          this.isAuthenticated = true
          this.currentAdmin = data.admin
        } else {
          this.isAuthenticated = false
          localStorage.removeItem('admin_token')
        }
      } catch (error) {
        console.error('Error verificando autenticación:', error)
        this.isAuthenticated = false
        localStorage.removeItem('admin_token')
      }
    },

    handleLoginSuccess(data) {
      localStorage.setItem('admin_token', data.token)
      this.currentAdmin = data.admin
      this.isAuthenticated = true
    },

    async handleLogout() {
      const token = localStorage.getItem('admin_token')

      try {
        await fetch('https://petruworkout-production.up.railway.app/api/admin/logout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token })
        })
      } catch (error) {
        console.error('Error al cerrar sesión:', error)
      }

      localStorage.removeItem('admin_token')
      this.isAuthenticated = false
      this.currentAdmin = null
      this.activeSection = 'dashboard'
    },

    changeSection(section) {
      this.activeSection = section
    }
  }
}
</script>

<style scoped>
.admin-view {
  min-height: 100vh;
  background: var(--bg-primary);
}

.admin-panel {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.admin-container {
  display: flex;
  flex: 1;
  max-width: 1800px;
  margin: 0 auto;
  width: 100%;
}

.admin-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

@media (max-width: 968px) {
  .admin-container {
    flex-direction: column;
  }

  .admin-content {
    padding: 1rem;
  }
}
</style>
