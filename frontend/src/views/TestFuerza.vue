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
        <div class="form-section">
  <label class="form-label">Peso corporal</label>
  <div class="peso-input-wrap">
    <input
      v-model.number="peso"
      type="number"
      min="0"
      placeholder="70"
      class="peso-input"
    />
    <span class="peso-unit">kg</span>
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
import { useHead } from '@unhead/vue'
export default {
  name: 'TestFuerza',
  setup() {
    useHead({
      title: 'Test de Fuerza Gratis | PetruWorkout',
      link: [
    { rel: 'canonical', href: 'https://petrucalistenia.com/test-fuerza' }
  ],
      meta: [
        { name: 'description', content: 'Descubre tu nivel real de fuerza en 30 segundos. Test gratuito de dominadas, fondos, flexiones y sentadillas.' },
        { property: 'og:title', content: 'Test de Fuerza Gratis | PetruWorkout' },
        { property: 'og:description', content: 'Descubre tu nivel real de fuerza en 30 segundos. Test gratuito de calistenia.' },
        { property: 'og:url', content: 'https://petrucalistenia.com/test-fuerza' },
        { name: 'robots', content: 'index, follow' },
      ]
    })
  },
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

        const alguno = Object.values(this.reps).some(v => v !== null && v > 0)
      if (!alguno) {
      this.modalError = 'Introduce al menos un ejercicio para continuar'
      return
    }

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
<style scoped>
.test-fuerza-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 6rem 2rem 4rem;
}

.page-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

/* HEADER */
.page-header {
  text-align: center;
}
.section-tag {
  font-size: 0.85rem;
  color: var(--color-accent);
  font-weight: 700;
  letter-spacing: 0.15em;
  display: block;
  margin-bottom: 1rem;
}
.page-header h1 {
  font-size: clamp(1.75rem, 4vw, 2.75rem);
  font-weight: 900;
  color: white;
  margin: 0 0 0.75rem 0;
}
.header-sub {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* FORM CARD */
.form-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}
.form-section {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.form-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(255,255,255,0.5);
  text-transform: uppercase;
  letter-spacing: 0.07em;
}
.sex-toggle {
  display: flex;
  gap: 0.75rem;
}

.toggle-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(255,255,255,0.13);
  border-radius: 10px;
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.55);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}
.toggle-btn:hover {
  background: rgba(255,255,255,0.09);
  color: white;
}
.toggle-btn.active {
  background: rgba(6,214,160,0.18);
  border-color: var(--color-accent);
  color: var(--color-accent);
}
.peso-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  max-width: 160px;
}
.peso-input {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.13);
  border-radius: 8px;
  color: white;
  padding: 0.6rem 0.875rem;
  font-size: 1rem;
  font-family: inherit;
  width: 100%;
  transition: border-color 0.2s;
}
.peso-input:focus {
  outline: none;
  border-color: var(--color-accent);
}
.peso-input::placeholder { color: rgba(255,255,255,0.25); }
.peso-unit {
  font-size: 0.9rem;
  color: rgba(255,255,255,0.45);
  font-weight: 600;
}

/* EXERCISES GRID */
.exercises-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.exercise-input {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 1rem 1.25rem;
}
.ex-icon {
  font-size: 1.4rem;
}
.exercise-input label {
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
}
.exercise-input input {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.13);
  border-radius: 8px;
  color: white;
  padding: 0.6rem 0.875rem;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
}
.exercise-input input:focus {
  outline: none;
  border-color: var(--color-accent);
}
.exercise-input input::placeholder {
  color: rgba(255,255,255,0.25);
}
.ex-hint {
  font-size: 0.72rem;
  color: rgba(255,255,255,0.3);
}

.btn-calculate {
  padding: 1rem 2rem;
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6,214,160,0.35);
  align-self: stretch;
}
.btn-calculate:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(6,214,160,0.55);
}

/* RESULTS */
.results-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Score card */
.score-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}
.score-circle {
  width: 110px;
  height: 110px;
  border-radius: 50%;
  border: 4px solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.score-number {
  font-size: 2.25rem;
  font-weight: 900;
  color: white;
  line-height: 1;
}
.score-max {
  font-size: 0.75rem;
  color: rgba(255,255,255,0.4);
}
.score-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.level-badge {
  display: inline-block;
  padding: 0.3rem 0.875rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  align-self: flex-start;
}
.level-principiante { background: rgba(226,75,74,0.2);  color: #E24B4A; border: 1px solid rgba(226,75,74,0.35); }
.level-novato        { background: rgba(239,159,39,0.2); color: #EF9F27; border: 1px solid rgba(239,159,39,0.35); }
.level-intermedio    { background: rgba(55,138,221,0.2); color: #378ADD; border: 1px solid rgba(55,138,221,0.35); }
.level-avanzado      { background: rgba(6,214,160,0.2);  color: var(--color-accent); border: 1px solid rgba(6,214,160,0.35); }
.level-elite         { background: rgba(6,214,160,0.25); color: #4dffb8; border: 1px solid rgba(6,214,160,0.5); }
.brain-text {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  line-height: 1.55;
  margin: 0;
}

/* Bars card */
.bars-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.bars-card h3 {
  font-size: 0.9rem;
  font-weight: 700;
  color: rgba(255,255,255,0.55);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin: 0;
}
.bar-row {
  display: grid;
  grid-template-columns: 120px 1fr 36px;
  align-items: center;
  gap: 0.75rem;
}
.bar-label {
  font-size: 0.85rem;
  color: rgba(255,255,255,0.7);
  white-space: nowrap;
}
.bar-bg {
  height: 9px;
  background: rgba(255,255,255,0.06);
  border-radius: 5px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.8s ease;
}
.bar-val {
  font-size: 0.85rem;
  font-weight: 700;
  color: white;
  text-align: right;
}

/* Weak card */
.weak-card {
  background: rgba(239,159,39,0.1);
  border: 1px solid rgba(239,159,39,0.3);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.weak-icon { font-size: 1.25rem; }
.weak-card p {
  font-size: 0.9rem;
  color: rgba(255,255,255,0.75);
  margin: 0;
}
.weak-card strong { color: #EF9F27; }

/* CTA card */
.cta-card {
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  align-items: center;
  border: 1px solid rgba(6,214,160,0.3);
  background: linear-gradient(135deg, rgba(6,214,160,0.1) 0%, rgba(6,214,160,0.04) 100%);
}
.cta-card p {
  font-size: 1rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}
.cta-card p strong { color: white; }
.wa-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #25D366, #128C7E);
  color: white;
  border-radius: 12px;
  font-weight: 800;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(37,211,102,0.35);
}
.wa-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(37,211,102,0.55);
}

.btn-reset {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.55);
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  align-self: center;
  transition: all 0.2s;
}
.btn-reset:hover {
  background: rgba(255,255,255,0.1);
  color: white;
}

/* MODAL */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}
.modal-content {
  background: rgba(26,26,26,0.98);
  border: 1px solid rgba(6,214,160,0.3);
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 460px;
  width: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255,255,255,0.1);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.modal-close:hover { background: rgba(255,255,255,0.2); }
.modal-content h2 {
  font-size: 1.5rem;
  color: white;
  font-weight: 800;
  margin: 0 0 0.25rem;
}
.modal-content > p {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin: 0 0 1rem;
}
.modal-form {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}
.modal-input {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.13);
  border-radius: 10px;
  color: white;
  padding: 0.875rem 1rem;
  font-size: 0.95rem;
  font-family: inherit;
  transition: border-color 0.2s;
}
.modal-input:focus {
  outline: none;
  border-color: var(--color-accent);
}
.modal-input::placeholder { color: rgba(255,255,255,0.25); }
.checkbox-group {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}
.checkbox-group input[type="checkbox"] { margin-top: 2px; accent-color: var(--color-accent); }
.checkbox-group a { color: var(--color-accent); text-decoration: underline; }
.error-msg {
  font-size: 0.82rem;
  color: #ff6b6b;
  font-weight: 600;
  padding: 0.4rem 0;
}
.btn-submit {
  padding: 1rem 1.5rem;
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 8px 25px rgba(6,214,160,0.35);
}
.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(6,214,160,0.5);
}
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

/* RESPONSIVE */
@media (max-width: 640px) {
  .test-fuerza-page { padding: 5rem 1rem 3rem; }
  .exercises-grid { grid-template-columns: 1fr; }
  .score-card { flex-direction: column; text-align: center; }
  .level-badge { align-self: center; }
  .bar-row { grid-template-columns: 90px 1fr 28px; }
  .modal-content { padding: 2rem 1.5rem; }
}
</style>
