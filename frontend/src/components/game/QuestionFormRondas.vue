<template>
  <div class="question-form">
    <!-- ✅ SOLO TÍTULO -->
    <h3 v-if="tipoPregunta === 'solo_titulo'">
      ¿Cuál es el título?
    </h3>

    <!-- ✅ SOLO AÑO -->
    <h3 v-else-if="tipoPregunta === 'solo_anio'">
      ¿En qué año se lanzó?
    </h3>

    <!-- ✅ SOLO ARTISTA -->
    <h3 v-else-if="tipoPregunta === 'solo_artista'">
      ¿Quién es el artista?
    </h3>

    <div class="form-grid">
      <!-- Solo Título -->
      <div v-if="tipoPregunta === 'solo_titulo'" class="input-field input-centered">
        <label for="titulo-input">🎵 Título de la canción</label>
        <input
          id="titulo-input"
          type="text"
          v-model="tituloLocal"
          placeholder="Ej: Bohemian Rhapsody"
          @keypress="handleKeypress"
          @input="updateTitulo"
          class="modern-input"
          :disabled="disabled"
        />
      </div>

      <!-- Solo Año -->
      <div v-else-if="tipoPregunta === 'solo_anio'" class="input-field input-centered">
        <label for="anio-input">📅 Año de lanzamiento</label>
        <input
          id="anio-input"
          type="number"
          v-model="anioLocal"
          placeholder="Ej: 1975"
          @keypress="handleKeypress"
          @input="updateAnio"
          class="modern-input"
          :disabled="disabled"
          min="1900"
          max="2025"
        />
      </div>

      <!-- Solo Artista -->
      <div v-else-if="tipoPregunta === 'solo_artista'" class="input-field input-centered">
        <label for="artista-only-input">🎤 Artista</label>
        <input
          id="artista-only-input"
          type="text"
          v-model="artistaLocal"
          placeholder="Ej: Queen"
          @keypress="handleKeypress"
          @input="updateArtista"
          class="modern-input"
          :disabled="disabled"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    titulo: String,
    artista: String,
    anio: String,
    tipoPregunta: String,
    disabled: Boolean
  },
  data() {
    return {
      tituloLocal: this.titulo,
      artistaLocal: this.artista,
      anioLocal: this.anio
    }
  },
  watch: {
    titulo(val) {
      this.tituloLocal = val
    },
    artista(val) {
      this.artistaLocal = val
    },
    anio(val) {
      this.anioLocal = val
    }
  },
  methods: {
    handleKeypress(e) {
      if (e.key === 'Enter' && !this.disabled) {
        this.$emit('submit')
      }
    },
    updateTitulo() {
      this.$emit('update:titulo', this.tituloLocal)
    },
    updateArtista() {
      this.$emit('update:artista', this.artistaLocal)
    },
    updateAnio() {
      this.$emit('update:anio', this.anioLocal)
    }
  }
}
</script>

<style scoped>
.question-form {
  background: linear-gradient(135deg, #ffd6a5, #ffb6b9);
  border-radius: 24px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.question-form h3 {
  font-weight: 700;
  font-size: 1.4rem;
  color: #6a1b9a;
  text-align: center;
  margin-bottom: 2rem;
  text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.5);
}

.form-grid {
  display: grid;
  gap: 1.5rem;
}

.input-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-centered {
  max-width: 400px;
  margin: 0 auto;
  width: 100%;
}

.input-field label {
  color: #4a235a;
  font-weight: 600;
  font-size: 0.95rem;
}

.modern-input {
  padding: 1rem;
  border-radius: 14px;
  font-size: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.6);
  color: #4a235a;
  font-weight: 500;
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.modern-input::placeholder {
  color: rgba(74, 35, 90, 0.5);
}

.modern-input:focus {
  outline: none;
  border-color: #ff6f61;
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 0 0 4px rgba(255, 111, 97, 0.2);
}

.modern-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .question-form {
    padding: 1.5rem;
    border-radius: 20px;
  }
}

@media (max-width: 480px) {
  .question-form {
    padding: 1rem;
    border-radius: 16px;
  }

  .modern-input {
    padding: 0.875rem;
    font-size: 0.95rem;
  }
}
</style>
