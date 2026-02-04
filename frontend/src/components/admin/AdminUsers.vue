<template>
  <div class="admin-users">
    <div class="page-header">
      <h1>👥 Gestión de Usuarios</h1>
      <p>Administra los usuarios registrados en la plataforma</p>
    </div>

    <!-- Filtros -->
    <div class="filters-section">
      <div class="filter-group">
        <label>Tipo de usuario:</label>
        <select v-model="filterType" @change="loadUsers">
          <option value="">Todos</option>
          <option value="newsletter">Newsletter</option>
          <option value="admin">Administradores</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Buscar:</label>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Email o nombre..."
          @input="debouncedSearch"
        />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando usuarios...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state">
      <p>❌ {{ error }}</p>
      <button @click="loadUsers" class="btn-retry">Reintentar</button>
    </div>

    <!-- Lista de usuarios -->
    <div v-else class="users-section">
      <div class="users-stats">
        <div class="stat-card">
          <span class="stat-number">{{ totalUsers }}</span>
          <span class="stat-label">Total Usuarios</span>
        </div>
        <div class="stat-card">
          <span class="stat-number">{{ filteredUsers.length }}</span>
          <span class="stat-label">Mostrando</span>
        </div>
      </div>

      <div class="users-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Email</th>
              <th>Tipo</th>
              <th>Newsletter</th>
              <th>Registro</th>
              <th>Última Conexión</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.nombre }}</td>
              <td>{{ user.email }}</td>
              <td>
                <span class="badge" :class="`badge-${user.tipo_usuario}`">
                  {{ user.tipo_usuario }}
                </span>
              </td>
              <td>
                <span class="status" :class="user.suscrito_newsletter ? 'status-active' : 'status-inactive'">
                  {{ user.suscrito_newsletter ? '✓ Suscrito' : '✗ No suscrito' }}
                </span>
              </td>
              <td>{{ formatDate(user.fecha_registro) }}</td>
              <td>{{ user.ultima_conexion ? formatDate(user.ultima_conexion) : 'Nunca' }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Paginación -->
        <div class="pagination" v-if="totalPages > 1">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="btn-page"
          >
            ← Anterior
          </button>
          <span class="page-info">
            Página {{ currentPage }} de {{ totalPages }}
          </span>
          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="btn-page"
          >
            Siguiente →
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminUsers',
  data() {
    return {
      users: [],
      loading: false,
      error: null,
      filterType: '',
      searchQuery: '',
      currentPage: 1,
      usersPerPage: 20,
      searchTimeout: null
    }
  },
  computed: {
    totalUsers() {
      return this.users.length
    },
    filteredUsers() {
      let filtered = this.users

      // Filtrar por búsqueda
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(user =>
          user.email.toLowerCase().includes(query) ||
          user.nombre.toLowerCase().includes(query)
        )
      }

      return filtered
    },
    paginatedUsers() {
      const start = (this.currentPage - 1) * this.usersPerPage
      const end = start + this.usersPerPage
      return this.filteredUsers.slice(start, end)
    },
    totalPages() {
      return Math.ceil(this.filteredUsers.length / this.usersPerPage)
    }
  },
  mounted() {
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      this.error = null

      try {
        const token = localStorage.getItem('admin_token')
        const url = new URL('https://petruworkout-production.up.railway.app/api/admin/users')

        if (this.filterType) {
          url.searchParams.append('tipo', this.filterType)
        }

        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        const data = await response.json()

        if (response.ok && data.success) {
          this.users = data.usuarios
        } else {
          throw new Error(data.error || 'Error al cargar usuarios')
        }
      } catch (err) {
        console.error('Error cargando usuarios:', err)
        this.error = err.message
      } finally {
        this.loading = false
      }
    },

    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1
      }, 300)
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.admin-users {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  color: white;
  margin: 0 0 0.5rem 0;
}

.page-header p {
  color: var(--color-text-muted);
  margin: 0;
}

.filters-section {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.filter-group select,
.filter-group input {
  padding: 0.75rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 0.95rem;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.loading-state,
.error-state {
  text-align: center;
  padding: 3rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-left-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state p {
  color: #ff6b6b;
  margin-bottom: 1rem;
}

.btn-retry {
  padding: 0.75rem 1.5rem;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-retry:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 214, 160, 0.3);
}

.users-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.1), rgba(6, 214, 160, 0.05));
  border: 1px solid rgba(6, 214, 160, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-accent);
  margin-bottom: 0.5rem;
}

.stat-label {
  display: block;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.users-table {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: rgba(255, 255, 255, 0.05);
}

th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

td {
  padding: 1rem;
  color: var(--color-text-secondary);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: capitalize;
}

.badge-newsletter {
  background: rgba(6, 214, 160, 0.2);
  color: var(--color-accent);
}

.badge-admin {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.status {
  font-size: 0.9rem;
}

.status-active {
  color: var(--color-success);
}

.status-inactive {
  color: var(--color-text-muted);
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-page {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-page:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--color-accent);
}

.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

@media (max-width: 968px) {
  .users-table {
    overflow-x: auto;
  }

  table {
    min-width: 800px;
  }

  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
