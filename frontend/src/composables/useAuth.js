// Composable para gestionar la autenticación
export function useAuth() {
  const API_URL = 'http://localhost:5001/api/auth'

  async function login(email, password) {
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        return {
          success: true,
          token: data.token,
          usuario: data.usuario
        }
      } else {
        return {
          success: false,
          error: data.error || '❌ Error al iniciar sesión'
        }
      }
    } catch (err) {
      console.error('Error en login:', err)
      return {
        success: false,
        error: '❌ Error de conexión. ¿El servidor está corriendo?'
      }
    }
  }

  async function register(nombre, email, password) {
    try {
      const response = await fetch(`${API_URL}/registro`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nombre, email, password })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        return {
          success: true,
          token: data.token,
          usuario: data.usuario
        }
      } else {
        return {
          success: false,
          error: data.error || '❌ Error al registrar usuario'
        }
      }
    } catch (err) {
      console.error('Error en registro:', err)
      return {
        success: false,
        error: '❌ Error de conexión. ¿El servidor está corriendo?'
      }
    }
  }

  async function logout(token) {
    try {
      await fetch(`${API_URL}/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token })
      })
      return { success: true }
    } catch (err) {
      console.error('Error cerrando sesión:', err)
      return { success: false }
    }
  }

  return {
    login,
    register,
    logout
  }
}
