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

      <div class="users-table">
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Email</th>
              <th>Tipo</th>
              <th>Newsletter</th>
              <th>Registro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id">
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
              <td>
        <button
          @click="handleDeleteClick(user)"
          class="btn-delete"
          :disabled="loading"
          title="Eliminar usuario"
        >
          🗑️
        </button>
      </td>
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
<transition name="modal-fade">
  <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
    <div class="modal-content">
      <button @click="closeDeleteModal" class="modal-close" :disabled="deleting">✕</button>

      <h2 class="modal-title">⚠️ Confirmar Eliminación</h2>

      <p class="modal-description">
        ¿Estás seguro de que quieres eliminar al usuario:
      </p>

      <div class="user-info-box">
        <p><strong>Nombre:</strong> {{ userToDelete?.nombre }}</p>
        <p><strong>Email:</strong> {{ userToDelete?.email }}</p>
      </div>

      <p class="modal-warning">
        ⚠️ Esta acción es <strong>permanente</strong> y no se puede deshacer.
      </p>

      <div v-if="deleteError" class="error-message">
        {{ deleteError }}
      </div>

      <div class="modal-buttons">
        <button
          @click="closeDeleteModal"
          class="btn-cancel"
          :disabled="deleting"
        >
          Cancelar
        </button>

        <button
          @click="handleConfirmDelete"
          class="btn-confirm-delete"
          :disabled="deleting"
        >
          {{ deleting ? '🗑️ Eliminando...' : '🗑️ Eliminar Usuario' }}
        </button>
      </div>
    </div>
  </div>
</transition>
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
      searchTimeout: null,
      showDeleteModal: false,
      userToDelete: null,
      deleting: false,
      deleteError: ''
    }
  },
  computed: {
    totalUsers() {
      return this.users.length
    },
    filteredUsers() {
      let filtered = this.users

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
            'token': token
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
    },

  handleDeleteClick(user) {
    this.userToDelete = user
    this.showDeleteModal = true
    this.deleteError = ''
  },


  closeDeleteModal() {
    this.showDeleteModal = false
    this.userToDelete = null
    this.deleteError = ''
  },

  async handleConfirmDelete() {
    if (!this.userToDelete) return

    this.deleting = true
    this.deleteError = ''

    try {
      const token = localStorage.getItem('admin_token')

      const response = await fetch(
        `https://petruworkout-production.up.railway.app/api/admin/users/${this.userToDelete.id}`,
        {
          method: 'DELETE',
          headers: { 'token': token }
        }
      )

      const data = await response.json()

      if (response.ok && data.success) {

        this.users = this.users.filter(u => u.id !== this.userToDelete.id)

        // Cerrar modal
        this.closeDeleteModal()

        console.log('Usuario eliminado:', data.message)
      } else {
        this.deleteError = data.detail || 'Error al eliminar usuario'
      }
    } catch (error) {
      console.error('Error eliminando usuario:', error)
      this.deleteError = 'Error de conexión al eliminar usuario'
    } finally {
      this.deleting = false
    }
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
  background: rgba(255, 255, 255, 0.08);
}

/* ✅ Arreglar opciones del select */
.filter-group select option {
  background: #1a1a1a;
  color: white;
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
    min-width: 700px;
  }

  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
  /* Botón eliminar en tabla */
.btn-delete {
  background: rgba(239, 35, 60, 0.2);
  border: 1px solid rgba(239, 35, 60, 0.4);
  border-radius: 6px;
  color: #ff6b6b;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.1rem;
}

.btn-delete:hover:not(:disabled) {
  background: rgba(239, 35, 60, 0.3);
  transform: scale(1.1);
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-content {
  background: rgba(26, 26, 26, 0.98);
  border: 1px solid rgba(239, 35, 60, 0.3);
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 500px;
  width: 100%;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.5rem;
  transition: all 0.3s ease;
}

.modal-close:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

.modal-close:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-title {
  font-size: 1.75rem;
  color: white;
  margin: 0 0 1rem 0;
  text-align: center;
}

.modal-description {
  font-size: 1rem;
  color: var(--color-text-secondary);
  text-align: center;
  margin: 0 0 1.5rem 0;
}

.user-info-box {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.user-info-box p {
  color: var(--color-text-secondary);
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

.user-info-box strong {
  color: white;
}

.modal-warning {
  background: rgba(255, 193, 7, 0.15);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 8px;
  padding: 1rem;
  color: #ffc107;
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.modal-warning strong {
  color: #ff9800;
}

.modal-buttons {
  display: flex;
  gap: 1rem;
}

.btn-cancel,
.btn-confirm-delete {
  flex: 1;
  padding: 1rem;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-cancel:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
}

.btn-confirm-delete {
  background: rgba(239, 35, 60, 0.2);
  border: 1px solid rgba(239, 35, 60, 0.4);
  color: #ff6b6b;
}

.btn-confirm-delete:hover:not(:disabled) {
  background: rgba(239, 35, 60, 0.3);
}

.btn-cancel:disabled,
.btn-confirm-delete:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  padding: 0.875rem;
  background: rgba(239, 35, 60, 0.2);
  border: 1px solid rgba(239, 35, 60, 0.4);
  border-radius: 10px;
  color: #ff6b6b;
  font-weight: 600;
  text-align: center;
  margin-bottom: 1rem;
}

@media (max-width: 640px) {
  .modal-content {
    padding: 2rem 1.5rem;
  }

  .modal-buttons {
    flex-direction: column;
  }
}
}
</style>
