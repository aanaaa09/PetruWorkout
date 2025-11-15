<template>
  <div class="player-setup-container">
    <div class="setup-card">
      <!-- Paso 1: Tipo de juego -->
      <div v-if="paso === 'tipo'" class="paso-tipo">
        <h2>🎮 Modo de Juego</h2>
        <p>¿Cómo quieres jugar?</p>

        <div class="tipo-botones">
          <button class="btn-tipo" @click="seleccionarTipo('individual')">
            <div class="tipo-icon">👤</div>
            <h3>Individual</h3>
            <p>Hasta 4 jugadores</p>
          </button>

          <button class="btn-tipo" @click="seleccionarTipo('parejas')">
            <div class="tipo-icon">👥</div>
            <h3>Parejas</h3>
            <p>Hasta 3 parejas</p>
          </button>
        </div>
      </div>

      <!-- Paso 2: Cantidad -->
      <div v-else-if="paso === 'cantidad'" class="paso-cantidad">
        <button class="btn-volver-pequeno" @click="volverPaso">← Volver</button>

        <h2>{{ tipoJuego === 'individual' ? '👥 ¿Cuántos jugadores?' : '👥 ¿Cuántas parejas?' }}</h2>
        <p class="advertencia">⚠️ Máximo {{ maxCantidad }}</p>

        <div class="cantidad-selector">
          <button
            v-for="n in maxCantidad"
            :key="n"
            class="btn-cantidad"
            @click="seleccionarCantidad(n)"
          >
            {{ n }}
          </button>
        </div>
      </div>

      <!-- Paso 3: Registro Individual -->
      <div v-else-if="paso === 'registro-individual'" class="paso-registro">
        <button class="btn-volver-pequeno" @click="volverPaso">← Volver</button>

        <h2>Jugador {{ jugadorActual + 1 }} de {{ cantidadJugadores }}</h2>

        <div class="registro-opciones">
          <p>¿Estás registrado en el juego?</p>

          <div class="opciones-botones">
            <button class="btn-opcion" @click="mostrarLoginJugador = true">
              ✅ Sí, iniciar sesión
            </button>
            <button class="btn-opcion" @click="mostrarRegistroJugador = true">
              📝 No, registrarme ahora
            </button>
            <button class="btn-opcion invitado" @click="registrarInvitado">
              👤 Jugar como invitado
            </button>
          </div>
        </div>

        <!-- Modal Login -->
        <transition name="modal-fade">
          <div v-if="mostrarLoginJugador" class="modal-overlay" @click.self="cerrarModales">
            <div class="modal-login">
              <button class="btn-cerrar-modal" @click="cerrarModales">✕</button>
              <h3>Iniciar Sesión - Jugador {{ jugadorActual + 1 }}</h3>
              <input v-model="loginEmail" type="email" placeholder="Email" class="input-modal" @keypress.enter="loginJugador" />
              <input v-model="loginPassword" type="password" placeholder="Contraseña" class="input-modal" @keypress.enter="loginJugador" />
              <div v-if="errorLogin" class="error-mensaje">{{ errorLogin }}</div>
              <button class="btn-modal-confirmar" @click="loginJugador" :disabled="cargando">
                {{ cargando ? '⏳ Entrando...' : 'Entrar' }}
              </button>
            </div>
          </div>
        </transition>

        <!-- Modal Registro -->
        <transition name="modal-fade">
          <div v-if="mostrarRegistroJugador" class="modal-overlay" @click.self="cerrarModales">
            <div class="modal-login">
              <button class="btn-cerrar-modal" @click="cerrarModales">✕</button>
              <h3>Registrarse - Jugador {{ jugadorActual + 1 }}</h3>
              <input v-model="registroNombre" type="text" placeholder="Nombre" class="input-modal" />
              <input v-model="registroEmail" type="email" placeholder="Email" class="input-modal" />
              <input v-model="registroPassword" type="password" placeholder="Contraseña (mín. 6 caracteres)" class="input-modal" @keypress.enter="registrarJugador" />
              <div v-if="errorRegistro" class="error-mensaje">{{ errorRegistro }}</div>
              <button class="btn-modal-confirmar" @click="registrarJugador" :disabled="cargando">
                {{ cargando ? '⏳ Registrando...' : 'Crear Cuenta' }}
              </button>
            </div>
          </div>
        </transition>
      </div>

      <!-- Paso 4: Registro Parejas -->
      <div v-else-if="paso === 'registro-parejas'" class="paso-registro">
        <button class="btn-volver-pequeno" @click="volverPaso">← Volver</button>

        <h2>Pareja {{ parejaActual + 1 }} de {{ cantidadJugadores }}</h2>

        <!-- Nombre de pareja -->
        <div v-if="!nombreParejaActual" class="nombre-pareja-input">
          <p>¿Cuál es el nombre de la pareja?</p>
          <input
            v-model="nombreParejaTemp"
            type="text"
            placeholder="Ej: Los Campeones"
            class="input-nombre-pareja"
            @keypress.enter="guardarNombrePareja"
          />
          <button class="btn-confirmar-nombre" @click="guardarNombrePareja" :disabled="!nombreParejaTemp.trim()">
            Confirmar Nombre
          </button>
        </div>

        <!-- Registro miembros -->
        <div v-else class="registro-miembro">
          <h3>Miembro {{ miembroActual + 1 }} de "{{ nombreParejaActual }}"</h3>

          <div class="registro-opciones">
            <p>¿Estás registrado en el juego?</p>

            <div class="opciones-botones">
              <button class="btn-opcion" @click="mostrarLoginJugador = true">
                ✅ Sí, iniciar sesión
              </button>
              <button class="btn-opcion" @click="mostrarRegistroJugador = true">
                📝 No, registrarme ahora
              </button>
              <button class="btn-opcion invitado" @click="registrarInvitado">
                👤 Jugar como invitado
              </button>
            </div>
          </div>

          <!-- Modales (mismos que individual) -->
          <transition name="modal-fade">
            <div v-if="mostrarLoginJugador" class="modal-overlay" @click.self="cerrarModales">
              <div class="modal-login">
                <button class="btn-cerrar-modal" @click="cerrarModales">✕</button>
                <h3>Iniciar Sesión - Miembro {{ miembroActual + 1 }}</h3>
                <input v-model="loginEmail" type="email" placeholder="Email" class="input-modal" @keypress.enter="loginJugador" />
                <input v-model="loginPassword" type="password" placeholder="Contraseña" class="input-modal" @keypress.enter="loginJugador" />
                <div v-if="errorLogin" class="error-mensaje">{{ errorLogin }}</div>
                <button class="btn-modal-confirmar" @click="loginJugador" :disabled="cargando">
                  {{ cargando ? '⏳ Entrando...' : 'Entrar' }}
                </button>
              </div>
            </div>
          </transition>

          <transition name="modal-fade">
            <div v-if="mostrarRegistroJugador" class="modal-overlay" @click.self="cerrarModales">
              <div class="modal-login">
                <button class="btn-cerrar-modal" @click="cerrarModales">✕</button>
                <h3>Registrarse - Miembro {{ miembroActual + 1 }}</h3>
                <input v-model="registroNombre" type="text" placeholder="Nombre" class="input-modal" />
                <input v-model="registroEmail" type="email" placeholder="Email" class="input-modal" />
                <input v-model="registroPassword" type="password" placeholder="Contraseña (mín. 6 caracteres)" class="input-modal" @keypress.enter="registrarJugador" />
                <div v-if="errorRegistro" class="error-mensaje">{{ errorRegistro }}</div>
                <button class="btn-modal-confirmar" @click="registrarJugador" :disabled="cargando">
                  {{ cargando ? '⏳ Registrando...' : 'Crear Cuenta' }}
                </button>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Paso 5: Resumen -->
      <div v-else-if="paso === 'resumen'" class="paso-resumen">
        <h2>✅ Jugadores Listos</h2>

        <div class="resumen-lista">
          <div
            v-for="(jugador, idx) in jugadoresLista"
            :key="idx"
            class="resumen-item"
          >
            <div class="resumen-icono">
              {{ tipoJuego === 'parejas' ? '👥' : '👤' }}
            </div>
            <div class="resumen-info">
              <h4>{{ obtenerNombreJugador(jugador) }}</h4>
              <p v-if="tipoJuego === 'parejas'" class="miembros-pareja">
                {{ jugador.miembro1.nombre }} & {{ jugador.miembro2.nombre }}
              </p>
              <span :class="['badge-tipo', { invitado: esInvitado(jugador) }]">
                {{ esInvitado(jugador) ? '👤 Invitado' : '✅ Registrado' }}
              </span>
            </div>
          </div>
        </div>

        <div class="resumen-botones">
          <button class="btn-volver" @click="volverPaso">
            ← Cambiar jugadores
          </button>
          <button class="btn-comenzar" @click="iniciarPartida" :disabled="iniciandoPartida">
            {{ iniciandoPartida ? '⏳ Iniciando...' : '🎮 ¡Comenzar Juego!' }}
          </button>
        </div>

        <div v-if="errorIniciar" class="error-mensaje">
          {{ errorIniciar }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PlayerSetup',
  props: {
    playlist: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      paso: 'tipo',
      tipoJuego: null,
      cantidadJugadores: 0,
      jugadorActual: 0,
      parejaActual: 0,
      miembroActual: 0,
      nombreParejaActual: '',
      nombreParejaTemp: '',

      // Almacenamiento temporal
      jugadoresIndividuales: [],
      parejas: [],

      // Modales
      mostrarLoginJugador: false,
      mostrarRegistroJugador: false,

      // Formularios
      loginEmail: '',
      loginPassword: '',
      registroNombre: '',
      registroEmail: '',
      registroPassword: '',

      // Estados
      cargando: false,
      iniciandoPartida: false,
      errorLogin: '',
      errorRegistro: '',
      errorIniciar: ''
    }
  },
  computed: {
    maxCantidad() {
      return this.tipoJuego === 'individual' ? 4 : 3
    },
    jugadoresLista() {
      return this.tipoJuego === 'individual' ? this.jugadoresIndividuales : this.parejas
    }
  },
  methods: {
    // ========== Navegación ==========
    seleccionarTipo(tipo) {
      this.tipoJuego = tipo
      this.paso = 'cantidad'
    },

    seleccionarCantidad(cantidad) {
      this.cantidadJugadores = cantidad
      this.paso = this.tipoJuego === 'individual' ? 'registro-individual' : 'registro-parejas'
    },

    volverPaso() {
      if (this.paso === 'cantidad') {
        this.paso = 'tipo'
        this.tipoJuego = null
      } else if (this.paso === 'registro-individual') {
        if (this.jugadorActual > 0) {
          this.jugadorActual--
          this.jugadoresIndividuales.pop()
        } else {
          this.paso = 'cantidad'
        }
      } else if (this.paso === 'registro-parejas') {
        if (this.miembroActual > 0) {
          // Volver al primer miembro
          this.miembroActual = 0
          const parejaActual = this.parejas[this.parejaActual]
          if (parejaActual) {
            delete parejaActual.miembro2
          }
        } else if (this.parejaActual > 0 || this.nombreParejaActual) {
          // Volver a nombre de pareja o pareja anterior
          if (this.nombreParejaActual) {
            this.nombreParejaActual = ''
          } else {
            this.parejaActual--
            this.miembroActual = 1
            this.parejas.pop()
          }
        } else {
          this.paso = 'cantidad'
        }
      } else if (this.paso === 'resumen') {
        this.paso = this.tipoJuego === 'individual' ? 'registro-individual' : 'registro-parejas'
        if (this.tipoJuego === 'individual') {
          this.jugadorActual = Math.max(0, this.jugadoresIndividuales.length - 1)
        } else {
          this.parejaActual = Math.max(0, this.parejas.length - 1)
          this.miembroActual = this.parejas[this.parejaActual]?.miembro2 ? 1 : 0
        }
      }
    },

    // ========== Login ==========
    async loginJugador() {
      this.errorLogin = ''

      if (!this.loginEmail.trim() || !this.loginPassword.trim()) {
        this.errorLogin = 'Email y contraseña son requeridos'
        return
      }

      this.cargando = true

      try {
        const response = await fetch('http://localhost:5000/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: this.loginEmail,
            password: this.loginPassword
          })
        })

        const data = await response.json()

        if (response.ok && data.success) {
          this.agregarJugador({
            tipo: 'registrado',
            nombre: data.usuario.nombre,
            email: data.usuario.email,
            puntos: data.usuario.puntos,
            token: data.token,
            usuario_id: data.usuario.id
          })

          this.cerrarModales()
          this.limpiarFormularios()
          this.avanzarJugador()
        } else {
          this.errorLogin = data.error || 'Error al iniciar sesión'
        }
      } catch (err) {
        this.errorLogin = 'Error de conexión con el servidor'
      } finally {
        this.cargando = false
      }
    },

    // ========== Registro ==========
    async registrarJugador() {
      this.errorRegistro = ''

      if (!this.registroNombre.trim() || !this.registroEmail.trim() || !this.registroPassword.trim()) {
        this.errorRegistro = 'Todos los campos son requeridos'
        return
      }

      if (this.registroPassword.length < 6) {
        this.errorRegistro = 'La contraseña debe tener al menos 6 caracteres'
        return
      }

      this.cargando = true

      try {
        const response = await fetch('http://localhost:5000/api/auth/registro', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nombre: this.registroNombre,
            email: this.registroEmail,
            password: this.registroPassword
          })
        })

        const data = await response.json()

        if (response.ok && data.success) {
          this.agregarJugador({
            tipo: 'registrado',
            nombre: data.usuario.nombre,
            email: data.usuario.email,
            puntos: data.usuario.puntos,
            token: data.token,
            usuario_id: data.usuario.id
          })

          this.cerrarModales()
          this.limpiarFormularios()
          this.avanzarJugador()
        } else {
          this.errorRegistro = data.error || 'Error al registrar'
        }
      } catch (err) {
        this.errorRegistro = 'Error de conexión con el servidor'
      } finally {
        this.cargando = false
      }
    },

    // ========== Invitado ==========
    registrarInvitado() {
      const nombre = prompt('¿Cuál es tu nombre?')

      if (nombre && nombre.trim()) {
        this.agregarJugador({
          tipo: 'invitado',
          nombre: nombre.trim(),
          puntos: 0
        })

        this.avanzarJugador()
      }
    },

    // ========== Lógica de Jugadores ==========
    agregarJugador(datosJugador) {
      if (this.tipoJuego === 'individual') {
        this.jugadoresIndividuales.push(datosJugador)
      } else {
        // Modo parejas
        if (this.miembroActual === 0) {
          // Primer miembro - crear pareja
          this.parejas.push({
            nombre_pareja: this.nombreParejaActual,
            miembro1: datosJugador,
            miembro2: null
          })
        } else {
          // Segundo miembro - completar pareja
          this.parejas[this.parejaActual].miembro2 = datosJugador
        }
      }
    },

    avanzarJugador() {
      if (this.tipoJuego === 'individual') {
        this.jugadorActual++

        if (this.jugadorActual >= this.cantidadJugadores) {
          this.paso = 'resumen'
        }
      } else {
        // Modo parejas
        this.miembroActual++

        if (this.miembroActual >= 2) {
          // Pareja completada
          this.miembroActual = 0
          this.parejaActual++
          this.nombreParejaActual = ''

          if (this.parejaActual >= this.cantidadJugadores) {
            this.paso = 'resumen'
          }
        }
      }
    },

    guardarNombrePareja() {
      if (this.nombreParejaTemp.trim()) {
        this.nombreParejaActual = this.nombreParejaTemp.trim()
        this.nombreParejaTemp = ''
      }
    },

    // ========== Iniciar Partida ==========
    async iniciarPartida() {
      this.errorIniciar = ''
      this.iniciandoPartida = true

      try {
        const configuracion = {
          tipo_juego: this.tipoJuego
        }

        if (this.tipoJuego === 'individual') {
          configuracion.jugadores_individuales = this.jugadoresIndividuales
        } else {
          configuracion.parejas = this.parejas
        }

        const response = await fetch('http://localhost:5000/api/tablero/iniciar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            playlist_key: this.playlist,
            configuracion
          })
        })

        const data = await response.json()

        if (response.ok && data.success) {
          this.$emit('partida-iniciada', {
            partida_id: data.partida_id,
            configuracion
          })
        } else {
          this.errorIniciar = data.detail || 'Error al iniciar la partida'
        }
      } catch (err) {
        this.errorIniciar = 'Error de conexión con el servidor'
      } finally {
        this.iniciandoPartida = false
      }
    },

    // ========== Utilidades ==========
    cerrarModales() {
      this.mostrarLoginJugador = false
      this.mostrarRegistroJugador = false
    },

    limpiarFormularios() {
      this.loginEmail = ''
      this.loginPassword = ''
      this.registroNombre = ''
      this.registroEmail = ''
      this.registroPassword = ''
      this.errorLogin = ''
      this.errorRegistro = ''
    },

    obtenerNombreJugador(jugador) {
      if (this.tipoJuego === 'individual') {
        return jugador.nombre
      } else {
        return jugador.nombre_pareja
      }
    },

    esInvitado(jugador) {
      if (this.tipoJuego === 'individual') {
        return jugador.tipo === 'invitado'
      } else {
        return jugador.miembro1.tipo === 'invitado' && jugador.miembro2.tipo === 'invitado'
      }
    }
  }
}
</script>

<style scoped>
.player-setup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
  padding: 1rem;
}

.setup-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  width: 100%;
  max-width: 600px;
  animation: fadeIn 0.5s ease;
}

/* Headers */
.paso-tipo h2,
.paso-cantidad h2,
.paso-registro h2,
.paso-resumen h2 {
  text-align: center;
  color: white;
  margin-bottom: 1rem;
  font-size: 1.75rem;
}

.paso-tipo p,
.paso-cantidad p {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2rem;
}

/* Botones de tipo */
.tipo-botones {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.btn-tipo {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 2rem 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  color: white;
}

.btn-tipo:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: #9c27b0;
  transform: translateY(-4px);
}

.tipo-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.btn-tipo h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.btn-tipo p {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* Advertencia */
.advertencia {
  background: rgba(243, 156, 18, 0.2);
  border: 1px solid rgba(243, 156, 18, 0.5);
  padding: 0.75rem;
  border-radius: 10px;
  text-align: center !important;
  color: #f39c12 !important;
  font-weight: 600;
  margin-bottom: 1rem;
}

/* Selector de cantidad */
.cantidad-selector {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-cantidad {
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  border: none;
  border-radius: 16px;
  padding: 2rem 1rem;
  font-size: 2rem;
  font-weight: 700;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(156, 39, 176, 0.3);
}

.btn-cantidad:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(156, 39, 176, 0.4);
}

/* Botón volver pequeño */
.btn-volver-pequeno {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
}

.btn-volver-pequeno:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Registro */
.registro-opciones {
  margin-top: 2rem;
}

.registro-opciones > p {
  text-align: center;
  color: white;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

.opciones-botones {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-opcion {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1.25rem;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-opcion:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: #9c27b0;
  transform: translateX(5px);
}

.btn-opcion.invitado {
  border-color: rgba(243, 156, 18, 0.5);
}

.btn-opcion.invitado:hover {
  border-color: #f39c12;
}

/* Nombre de pareja */
.nombre-pareja-input {
  background: rgba(255, 255, 255, 0.05);
  padding: 1.5rem;
  border-radius: 12px;
  margin-top: 1rem;
}

.nombre-pareja-input p {
  color: white;
  margin-bottom: 1rem;
}

.input-nombre-pareja {
  width: 100%;
  padding: 0.875rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  margin-bottom: 1rem;
}

.input-nombre-pareja::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-nombre-pareja:focus {
  outline: none;
  border-color: #9c27b0;
}

.btn-confirmar-nombre {
  width: 100%;
  padding: 0.875rem;
  background: linear-gradient(135deg, #00c851, #007e33);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-confirmar-nombre:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 200, 81, 0.4);
}

.btn-confirmar-nombre:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.registro-miembro h3 {
  text-align: center;
  color: white;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
}

/* ========== MODALES ========== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-login {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 20px;
  padding: 2rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  animation: modalAppear 0.3s ease;
}

@keyframes modalAppear {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.btn-cerrar-modal {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 1.5rem;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.btn-cerrar-modal:hover {
  background: rgba(255, 68, 68, 0.3);
  transform: rotate(90deg);
}

.modal-login h3 {
  color: white;
  text-align: center;
  margin-bottom: 1.5rem;
  margin-top: 0;
  font-size: 1.5rem;
}

.input-modal {
  width: 100%;
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  margin-bottom: 1rem;
  box-sizing: border-box;
  transition: all 0.3s ease;
}

.input-modal::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-modal:focus {
  outline: none;
  border-color: #9c27b0;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(156, 39, 176, 0.2);
}

.error-mensaje {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #fca5a5;
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  text-align: center;
  font-size: 0.95rem;
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.btn-modal-confirmar {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(156, 39, 176, 0.3);
}

.btn-modal-confirmar:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(156, 39, 176, 0.4);
}

.btn-modal-confirmar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ========== RESUMEN ========== */
.resumen-lista {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 2rem 0;
}

.resumen-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  border-radius: 12px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.resumen-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #9c27b0;
}

.resumen-icono {
  font-size: 2rem;
  flex-shrink: 0;
}

.resumen-info {
  flex: 1;
}

.resumen-info h4 {
  color: white;
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
}

.resumen-info p {
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.miembros-pareja {
  font-size: 0.85rem !important;
  color: rgba(255, 255, 255, 0.6) !important;
  font-style: italic;
}

.badge-tipo {
  display: inline-block;
  padding: 0.3rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  background: rgba(0, 200, 81, 0.2);
  color: #00c851;
  border: 1px solid rgba(0, 200, 81, 0.4);
}

.badge-tipo.invitado {
  background: rgba(243, 156, 18, 0.2);
  color: #f39c12;
  border-color: rgba(243, 156, 18, 0.4);
}

.resumen-botones {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-volver,
.btn-comenzar {
  flex: 1;
  padding: 1rem;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-volver {
  background: linear-gradient(135deg, #2196f3, #0d47a1);
  color: white;
  box-shadow: 0 8px 32px rgba(33, 150, 243, 0.3);
}

.btn-volver:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(33, 150, 243, 0.4);
}

.btn-comenzar {
  background: linear-gradient(135deg, #00c851, #007e33);
  color: white;
  box-shadow: 0 8px 32px rgba(0, 200, 81, 0.3);
}

.btn-comenzar:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 200, 81, 0.4);
}

.btn-comenzar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ========== RESPONSIVE ========== */
@media (max-width: 768px) {
  .setup-card {
    padding: 1.5rem;
  }

  .tipo-botones {
    grid-template-columns: 1fr;
  }

  .btn-tipo {
    padding: 1.5rem 1rem;
  }

  .tipo-icon {
    font-size: 2.5rem;
  }

  .resumen-botones {
    flex-direction: column;
  }

  .modal-login {
    padding: 1.5rem;
    max-width: 90%;
  }
}

@media (max-width: 480px) {
  .setup-card {
    padding: 1rem;
  }

  .modal-login {
    padding: 1.25rem;
  }

  .btn-cerrar-modal {
    width: 36px;
    height: 36px;
    font-size: 1.25rem;
  }
}
</style>
