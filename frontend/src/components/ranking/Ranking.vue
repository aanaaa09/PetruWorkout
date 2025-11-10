<template>
  <div class="ranking-container">
    <div class="ranking-header">
      <h2>🏆 Ranking de Jugadores</h2>
      <button class="btn btn-volver" @click="$emit('cerrar')">
        ← Volver
      </button>
    </div>

    <div v-if="cargando" class="loading">
      <div class="spinner"></div>
      <p>Cargando ranking...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>❌ {{ error }}</p>
      <button class="btn btn-volver" @click="cargarRanking">
        Reintentar
      </button>
    </div>

    <div v-else class="ranking-list">
      <div
        v-for="(usuario, index) in ranking"
        :key="index"
        class="ranking-item"
        :class="{'top-three': index < 3}"
      >
        <div class="posicion">
          <span v-if="index === 0" class="medalla">🥇</span>
          <span v-else-if="index === 1" class="medalla">🥈</span>
          <span v-else-if="index === 2" class="medalla">🥉</span>
          <span v-else class="numero">{{ index + 1 }}</span>
        </div>

        <div class="usuario-info">
          <span class="nombre">{{ usuario.nombre }}</span>
        </div>

        <div class="puntos">
          <span class="numero-puntos">{{ usuario.puntos }}</span>
          <span class="label-puntos">puntos</span>
        </div>
      </div>

      <div v-if="ranking.length === 0" class="sin-datos">
        <p>📊 Aún no hay jugadores en el ranking</p>
        <p class="subtitulo">¡Sé el primero en jugar!</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Ranking',
  data() {
    return {
      ranking: [],
      cargando: true,
      error: null
    }
  },
  mounted() {
    this.cargarRanking()
  },
  methods: {
    async cargarRanking() {
      this.cargando = true
      this.error = null

      try {
        const response = await fetch('http://localhost:5000/api/auth/ranking?limit=50')

        if (!response.ok) {
          throw new Error('Error al obtener el ranking')
        }

        const data = await response.json()
        this.ranking = data.ranking || []

      } catch (err) {
        console.error('Error cargando ranking:', err)
        this.error = 'No se pudo cargar el ranking. Intenta de nuevo.'
      } finally {
        this.cargando = false
      }
    }
  }
}
</script>

<style scoped>
.ranking-container {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.4s ease;
}

.ranking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.ranking-header h2 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top: 4px solid #ffd700;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  text-align: center;
  padding: 2rem;
}

.error-message p {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  color: #ff6b6b;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.ranking-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(5px);
}

.ranking-item.top-three {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 237, 78, 0.05));
  border-color: rgba(255, 215, 0, 0.3);
}

.posicion {
  min-width: 60px;
  text-align: center;
}

.medalla {
  font-size: 2rem;
}

.posicion .numero {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.6);
}

.usuario-info {
  flex: 1;
}

.nombre {
  font-size: 1.2rem;
  font-weight: 600;
  color: white;
}

.puntos {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 100px;
}

.numero-puntos {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #00c851, #00ff6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.label-puntos {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sin-datos {
  text-align: center;
  padding: 3rem;
  color: rgba(255, 255, 255, 0.6);
}

.sin-datos p {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.subtitulo {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.4);
}

@media (max-width: 768px) {
  .ranking-container {
    padding: 1.5rem;
  }

  .ranking-header h2 {
    font-size: 1.5rem;
  }

  .ranking-item {
    padding: 1rem;
    gap: 1rem;
  }

  .posicion {
    min-width: 50px;
  }

  .medalla {
    font-size: 1.5rem;
  }

  .nombre {
    font-size: 1rem;
  }

  .numero-puntos {
    font-size: 1.4rem;
  }

  .puntos {
    min-width: 80px;
  }
}

@media (max-width: 480px) {
  .ranking-header {
    flex-direction: column;
    align-items: stretch;
  }

  .ranking-item {
    gap: 0.75rem;
  }

  .posicion .numero {
    font-size: 1.2rem;
  }
}
</style>
