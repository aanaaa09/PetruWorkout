<template>
  <div class="test-fuerza-page">
    <div class="page-container">

      <!-- HEADER -->
      <div class="page-header">
        <span class="section-tag">TEST GRATUITO</span>
        <h1>¿Cuál es tu nivel real de fuerza?</h1>
        <p class="header-sub">Introduce tus máximos y descubre en qué punto estás en 30 segundos</p>
      </div>

      <!-- PASO 1: FORMULARIO -->
      <div v-if="step === 1" class="form-card">
        <div class="form-section">
          <label class="form-label">Sexo</label>
          <div class="sex-toggle">
            <button :class="['toggle-btn', sexo === 'm' ? 'active' : '']" @click="sexo = 'm'">Hombre</button>
            <button :class="['toggle-btn', sexo === 'f' ? 'active' : '']" @click="sexo = 'f'">Mujer</button>
          </div>
        </div>

        <div class="exercises-grid">
          <div v-for="ex in exercises" :key="ex.key" class="exercise-input">
            <span class="ex-icon">{{ ex.icon }}</span>
            <label>{{ ex.label }}</label>
            <input
              v-model.number="reps[ex.key]"
              type="number"
              min="0"
              :placeholder="ex.placeholder"
            />
            <span class="ex-hint">{{ ex.hint }}</span>
          </div>
        </div>

        <button class="btn-calculate" @click="openModal">
          Calcular mi nivel →
        </button>
      </div>

      <!-- RESULTADOS -->
      <div v-if="step === 3 && result" class="results-section">
        <!-- Score global -->
        <div class="score-card">
          <div class="score-circle" :style="{ borderColor: scoreColor }">
            <span class="score-number">{{ result.score }}</span>
            <span class="score-max">/100</span>
          </div>
          <div class="score-info">
            <div class="level-badge" :class="'level-' + result.level">
              {{ levelLabels[result.level] }}
            </div>
            <p class="brain-text">{{ brainText }}</p>
          </div>
        </div>

        <!-- Barras por ejercicio -->
        <div class="bars-card">
          <h3>Desglose por ejercicio</h3>
          <div v-for="ex in exercises" :key="ex.key" class="bar-row">
            <span class="bar-label">{{ ex.icon }} {{ ex.label }}</span>
            <div class="bar-bg">
              <div
                class="bar-fill"
                :style="{ width: result.scores[ex.key] + '%', background: barColor(result.scores[ex.key]) }"
              ></div>
            </div>
            <span class="bar-val">{{ reps[ex.key] || 0 }}</span>
          </div>
        </div>

        <!-- Punto débil -->
        <div class="weak-card">
          <span class="weak-icon">⚠️</span>
          <p>Tu mayor problema: <strong>fuerza de {{ result.weak_label }}</strong></p>
        </div>

        <!-- CTA WhatsApp -->
        <div :class="['cta-card', 'level-' + result.level]">
          <p v-html="ctaText"></p>
          <a class="wa-btn" href="https://wa.me/34642662849?text=FUERZA" target="_blank">
            Escríbeme "FUERZA" por WhatsApp
          </a>
        </div>

        <!-- Repetir test -->
        <button class="btn-reset" @click="reset">Repetir el test</button>
      </div>

    </div>

    <!-- MODAL nombre + email -->
    <transition name="modal-fade">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <button class="modal-close" @click="showModal = false">✕</button>
          <h2>Descubre tu resultado</h2>
          <p>Introduce tus datos para ver tu nivel de fuerza</p>

          <div class="modal-form">
            <input v-model="nombre" type="text" placeholder="Tu nombre" class="modal-input" />
            <input v-model="email" type="email" placeholder="tu@email.com" class="modal-input" />

            <div class="checkbox-group">
              <input v-model="privacyAccepted" type="checkbox" id="privacy" />
              <label for="privacy">Acepto la <router-link to="/info?legal=privacy" @click="showModal=false">política de privacidad</router-link></label>
            </div>

            <div v-if="modalError" class="error-msg">{{ modalError }}</div>

            <button class="btn-submit" :disabled="loading" @click="submitAndCalculate">
              {{ loading ? '⏳ Calculando...' : 'Ver mi resultado →' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
const API = 'https://petruworkout-production.up.railway.app'

export default {
  name: 'TestFuerza',
  data() {
    return {
      step: 1,
      sexo: 'm',
      reps: { pull: null, dips: null, push: null, squat: null },
      showModal: false,
      nombre: '',
      email: '',
      privacyAccepted: false,
      loading: false,
      modalError: '',
      result: null,
      exercises: [
        { key: 'pull',  icon: '⬆️', label: 'Dominadas',   placeholder: '0', hint: 'Máximo seguido' },
        { key: 'dips',  icon: '💪', label: 'Fondos',       placeholder: '0', hint: 'Máximo seguido' },
        { key: 'push',  icon: '🔄', label: 'Flexiones',    placeholder: '0', hint: 'Máximo seguido' },
        { key: 'squat', icon: '🦵', label: 'Sentadillas',  placeholder: '0', hint: 'Máximo seguido' },
      ],
      levelLabels: {
        principiante: 'Principiante', novato: 'Novato',
        intermedio: 'Intermedio', avanzado: 'Avanzado', elite: 'Élite',
      },
    }
  },
  computed: {
    scoreColor() {
      if (!this.result) return '#fff'
      const s = this.result.score
      if (s < 40) return '#E24B4A'
      if (s < 65) return '#EF9F27'
      if (s < 85) return '#378ADD'
      return '#1D9E75'
    },
    brainText() {
      const lv = this.result?.level
      const map = {
        principiante: 'Estás en un nivel bajo: tu cuerpo aún no tiene la base mínima para progresar de forma eficiente.',
        novato: 'Estás en un punto crítico: si no estructuras tu entrenamiento ahora, te vas a estancar muy pronto.',
        intermedio: 'Ya no estás empezando, pero si no aumentas la intensidad y la estrategia, te quedarás en este nivel durante años.',
        avanzado: 'Muy por encima de la media, pero aún tienes margen de mejora para alcanzar un nivel de fuerza completo.',
        elite: 'Estás muy por encima de la media, pero aún tienes un punto débil que te impide alcanzar un nivel de fuerza completo.',
      }
      return map[lv] || ''
    },
    ctaText() {
      const s = this.result?.score || 0
      const lv = this.result?.level
      const wa = 'https://wa.me/34642662849?text=FUERZA'
      const targets = { principiante: Math.min(s+38,64), novato: Math.min(s+38,80), intermedio: Math.min(s+27,95), avanzado: Math.min(s+15,98) }
      if (lv === 'principiante' || lv === 'novato' || lv === 'intermedio' || lv === 'avanzado') {
        return `Ahora mismo estás en <strong>${s}/100</strong>. Si quieres subir a <strong>${targets[lv]}</strong> en menos de 90 días, escríbeme <strong>"FUERZA"</strong> al WhatsApp y te explico cómo.`
      }
      return `La mayoría en este nivel se estanca porque entrena fuerte… pero no inteligente. Si quieres pasar a un nivel <strong>realmente completo (100/100)</strong>, escríbeme <strong>"FUERZA"</strong>.`
    },
  },
  methods: {
    barColor(pct) {
      if (pct < 40) return '#E24B4A'
      if (pct < 65) return '#EF9F27'
      if (pct < 85) return '#378ADD'
      return '#1D9E75'
    },
    openModal() {
      this.modalError = ''
      this.showModal = true
    },
    async submitAndCalculate() {
      this.modalError = ''
      if (!this.nombre.trim()) { this.modalError = 'Introduce tu nombre'; return }
      if (!this.email || !this.email.includes('@')) { this.modalError = 'Email inválido'; return }
      if (!this.privacyAccepted) { this.modalError = 'Acepta la política de privacidad'; return }

      this.loading = true
      try {
        const res = await fetch(`${API}/api/fuerza/register-and-calculate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nombre: this.nombre,
            email: this.email,
            sexo: this.sexo,
            pull:  this.reps.pull  || 0,
            dips:  this.reps.dips  || 0,
            push:  this.reps.push  || 0,
            squat: this.reps.squat || 0,
          }),
        })
        const data = await res.json()
        if (!res.ok) { this.modalError = data.detail || 'Error al registrar'; return }
        this.result = data
        this.showModal = false
        this.step = 3
      } catch {
        this.modalError = 'Error de conexión. Intenta de nuevo.'
      } finally {
        this.loading = false
      }
    },
    reset() {
      this.step = 1
      this.result = null
      this.reps = { pull: null, dips: null, push: null, squat: null }
    },
  },
}
</script>
