<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <div class="header-box">
          <h2 class="modal-title">DIAGNÓSTICO: <span class="text-green">FUERZA REAL</span></h2>
          <p v-if="step < 6" class="modal-desc">
            Analizo tu nivel y te digo qué deberías hacer para conseguir tu objetivo.
          </p>
        </div>
      </div>

      <div class="modal-body">
        <!-- Step 1: Objetivo -->
        <div v-if="step === 1" class="step-content animation-slide">
          <h3 class="question-title">¿Cuál es tu objetivo? ¿Qué te gustaría conseguir? 🎯</h3>
          <div class="options-grid">
            <button v-for="opt in goalOptions" :key="opt" 
                    :class="['option-btn', { selected: answers.goal === opt }]"
                    @click="selectOption('goal', opt)">
              {{ opt }}
            </button>
          </div>
        </div>

        <!-- Step 2: Edad -->
        <div v-if="step === 2" class="step-content animation-slide">
          <h3 class="question-title">¿Qué edad tienes actualmente?</h3>
          <div class="options-grid">
            <button v-for="opt in ageOptions" :key="opt" 
                    :class="['option-btn', { selected: answers.age === opt }]"
                    @click="selectOption('age', opt)">
              {{ opt }}
            </button>
          </div>
        </div>

        <!-- Step 3: Nivel -->
        <div v-if="step === 3" class="step-content animation-slide">
          <h3 class="question-title">¿Cuál es tu nivel ahora mismo? 📈</h3>
          <div class="options-grid">
            <button v-for="opt in levelOptions" :key="opt" 
                    :class="['option-btn', { selected: answers.level === opt }]"
                    @click="selectOption('level', opt)">
              {{ opt }}
            </button>
          </div>
        </div>

        <!-- Step 4: Bloqueo -->
        <div v-if="step === 4" class="step-content animation-slide">
          <h3 class="question-title">¿Qué es lo que más te está frenando ahora? 🛑</h3>
          <div class="options-grid">
            <button v-for="opt in blockOptions" :key="opt" 
                    :class="['option-btn', { selected: answers.block === opt }]"
                    @click="selectOption('block', opt)">
              {{ opt }}
            </button>
          </div>
        </div>

        <!-- Step 5: Solución -->
        <div v-if="step === 5" class="step-content animation-slide">
          <h3 class="question-title">Si identifico tu bloqueo, ¿qué tipo de solución buscas? ⚡</h3>
          <div class="options-grid">
            <button v-for="opt in solutionOptions" :key="opt" 
                    :class="['option-btn', { selected: answers.solution === opt }]"
                    @click="selectOption('solution', opt)">
              {{ opt }}
            </button>
          </div>
        </div>

        <!-- Step 6: Contacto -->
        <div v-if="step === 6" class="step-content animation-slide contact-step">
          <div class="header-box">
            <h3 class="modal-title text-green">¡Último paso!</h3>
            <p class="contact-text">
              Voy a revisar tus respuestas y te escribo yo mismo por WhatsApp. Analizamos tu caso a fondo y vemos qué puede estar fallando.
            </p>
          </div>
          <div class="form-group">
            <label>Nombre completo</label>
            <input type="text" v-model="answers.name" placeholder="Tu nombre" class="form-input" />
          </div>
          <div class="form-group">
            <label>Teléfono (WhatsApp)</label>
            <div class="phone-input-wrapper">
              
              <!-- Custom Country Select -->
              <div class="custom-country-select" ref="countrySelect">
                <div class="selected-country" @click="toggleCountryDropdown">
                  <span class="flag">{{ selectedCountry.flag }}</span>
                  <span class="prefix">{{ selectedCountry.dialCode }}</span>
                  <span class="arrow">▾</span>
                </div>
                
                <!-- Dropdown list -->
                <div v-if="showCountryDropdown" class="dropdown-overlay" @click="showCountryDropdown = false"></div>
                <div v-if="showCountryDropdown" class="country-dropdown-container">
                  <div class="country-search-box">
                    <input 
                      type="text" 
                      v-model="countrySearchQuery" 
                      placeholder="Buscar país..." 
                      class="country-search-input"
                      ref="searchInput"
                    />
                  </div>
                  <ul class="country-dropdown-list">
                    <li v-for="c in filteredCountries" :key="c.code" @click="selectCountry(c)" class="country-item">
                      <span class="flag">{{ c.flag }}</span>
                      <span class="name">{{ c.name }}</span>
                      <span class="code">{{ c.dialCode }}</span>
                    </li>
                    <li v-if="filteredCountries.length === 0" class="country-item no-results">
                      No se encontraron países
                    </li>
                  </ul>
                </div>
              </div>

              <input type="tel" v-model="answers.phone" placeholder="612 34 56 78" class="form-input phone-input" />
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button v-if="step > 1" class="btn-back" @click="prevStep">Atrás</button>
        <button v-if="step < 6" class="btn-next" :disabled="!canGoNext" @click="nextStep">Siguiente</button>
        <button v-if="step === 6" class="btn-submit" :disabled="!isFormValid" @click="submitForm">Enviar y analizar mi nivel <span class="send-icon">🚀</span></button>
      </div>

      <!-- Barra de progreso -->
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: (step / 6) * 100 + '%' }"></div>
      </div>

    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { countries } from '@/utils/countries'

export default {
  name: 'AdmissionFormModal',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      step: 1,
      answers: {
        age: '',
        goal: '',
        level: '',
        block: '',
        solution: '',
        name: '',
        prefix: '+34',
        phone: ''
      },
      showCountryDropdown: false,
      countrySearchQuery: '',
      countries: countries,
      ageOptions: ['Menos de 18', '18-24', '25-35', '+35'],
      goalOptions: [
        'Ganar músculo',
        'Perder grasa y definir',
        'Aprender habilidades (Muscle-up, pino, front lever…)',
        'Llegar a mi nivel máximo en Fuerza y Físico'
      ],
      levelOptions: [
        'Empiezo desde cero',
        'Entreno, pero no progreso',
        'Tengo Fuerza básica (dominadas, fondos, flexiones)',
        'Nivel avanzado (Dominadas con peso, habilidades)'
      ],
      blockOptions: [
        'No sé cómo entrenar bien',
        'Falta de disciplina y constancia',
        'Me estanco',
        'Entreno mucho, pero no progreso'
      ],
      solutionOptions: [
        'Solo busco el resultado y aplicar los consejos por mi cuenta.',
        'Quiero ver mi diagnóstico y conocer los precios de tu asesoría.',
        'Busco un entrenador que me lleve al 100% para acelerar mi proceso'
      ]
    }
  },
  computed: {
    canGoNext() {
      if (this.step === 1) return !!this.answers.goal
      if (this.step === 2) return !!this.answers.age
      if (this.step === 3) return !!this.answers.level
      if (this.step === 4) return !!this.answers.block
      if (this.step === 5) return !!this.answers.solution
      return true
    },
    isFormValid() {
      const cleanPhone = this.answers.phone.replace(/\D/g, '')
      return this.answers.name.trim() !== '' && cleanPhone.length >= 8
    },
    selectedCountry() {
      return this.countries.find(c => c.dialCode === this.answers.prefix) || this.countries.find(c => c.code === 'ES')
    },
    filteredCountries() {
      if (!this.countrySearchQuery) return this.countries
      const q = this.countrySearchQuery.toLowerCase()
      return this.countries.filter(c => 
        c.name.toLowerCase().includes(q) || 
        c.dialCode.includes(q)
      )
    }
  },
  methods: {
    toggleCountryDropdown() {
      this.showCountryDropdown = !this.showCountryDropdown
      if (this.showCountryDropdown) {
        this.countrySearchQuery = ''
        this.$nextTick(() => {
          if (this.showCountryDropdown && this.$refs.searchInput) {
            this.$refs.searchInput.focus()
          }
        })
      }
    },
    selectCountry(country) {
      this.answers.prefix = country.dialCode
      this.showCountryDropdown = false
    },
    selectOption(field, value) {
      this.answers[field] = value
      // Auto avance rápido al siguiente paso (opcional, mejora UX)
      setTimeout(() => {
        if (this.step < 6) this.nextStep()
      }, 300)
    },
    nextStep() {
      if (this.step < 6) this.step++
    },
    prevStep() {
      if (this.step > 1) this.step--
    },
    submitForm() {
      // Mock envio de datos (luego se integrará con Telegram)
      console.log('Datos del formulario enviados:', this.answers)

      // Lógica de redirección
      if (this.answers.age === 'Menos de 18') {
        this.router.push('/mejorar')
      } else {
        this.router.push('/fuerza')
      }
      
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(5px);
  padding: 1rem;
}

.modal-content {
  background: var(--bg-secondary, #1a1a1a);
  border-radius: 20px;
  width: 100%;
  max-width: 600px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  border: 1px solid rgba(255,255,255,0.1);
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

.modal-header {
  padding: 2rem 2rem 1rem;
}

.header-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.contact-step .header-box {
  padding: 1.25rem 1rem;
  margin-bottom: 1.75rem;
}

.contact-text {
  color: var(--color-text-secondary, #e0e0e0);
  font-size: 0.95rem;
  margin-top: 0.5rem;
  margin-bottom: 0;
  line-height: 1.4;
}

.modal-title {
  color: white;
  font-size: 1.6rem;
  font-weight: 900;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.text-green {
  color: var(--color-accent, #06d6a0);
}

@media (max-width: 768px) {
  .modal-title .text-green {
    display: block;
  }
}

.modal-desc {
  color: var(--color-text-secondary, #e0e0e0);
  font-size: 1.05rem;
  margin-top: 0.75rem;
  font-weight: 500;
  line-height: 1.4;
}

.modal-body {
  padding: 1rem 2rem 2rem;
  min-height: 380px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.question-title {
  color: white;
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  text-align: center;
  line-height: 1.3;
}

.options-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option-btn {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.15);
  color: #e0e0e0;
  padding: 1.2rem 1.5rem;
  border-radius: 12px;
  font-size: 1.05rem;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.option-btn:hover {
  background: rgba(255,255,255,0.1);
  border-color: rgba(255,255,255,0.2);
}

.option-btn.selected {
  background: rgba(6, 214, 160, 0.1);
  border-color: var(--color-accent, #06d6a0);
  color: var(--color-accent, #06d6a0);
  font-weight: 700;
}

.contact-text {
  color: white;
  font-size: 1.1rem;
  text-align: center;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: var(--color-text-secondary, #a0a0a0);
  font-size: 0.9rem;
}

.form-input {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.2);
  padding: 1rem;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  width: 100%;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-accent, #06d6a0);
  background: rgba(255,255,255,0.08);
}

.phone-input-wrapper {
  display: flex;
  align-items: stretch;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  overflow: visible; /* To allow dropdown to overflow */
  transition: all 0.3s ease;
  position: relative;
}

.phone-input-wrapper:focus-within {
  border-color: var(--color-accent, #06d6a0);
}

.custom-country-select {
  position: relative;
  background: rgba(0,0,0,0.2);
  border-right: 1px solid rgba(255,255,255,0.1);
  display: flex;
  align-items: center;
}

.selected-country {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0.75rem;
  cursor: pointer;
  color: white;
  user-select: none;
}

.selected-country .arrow {
  font-size: 0.8rem;
  color: #a0a0a0;
  margin-left: 0.2rem;
}

.dropdown-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 10;
}

.country-dropdown-container {
  position: absolute;
  bottom: 100%; /* Despliega hacia arriba */
  left: 0;
  width: 320px;
  background: #2a2a2a;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  box-shadow: 0 -10px 30px rgba(0,0,0,0.5); /* Sombra hacia arriba */
  margin-bottom: 5px;
  z-index: 20;
  display: flex;
  flex-direction: column;
}

.country-search-box {
  padding: 0.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.country-search-input {
  width: 100%;
  padding: 0.5rem;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 4px;
  color: white;
  font-size: 0.9rem;
}
.country-search-input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.country-dropdown-list {
  max-height: 250px;
  overflow-y: auto;
  padding: 0;
  margin: 0;
  list-style: none;
}

.country-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background 0.2s;
  color: white;
}

.country-item:hover {
  background: rgba(255,255,255,0.1);
}

.country-item.no-results {
  color: #a0a0a0;
  cursor: default;
  justify-content: center;
  padding: 1rem;
}
.country-item.no-results:hover {
  background: transparent;
}

.country-item .name {
  flex: 1;
  font-size: 0.95rem;
}

.country-item .code {
  color: #a0a0a0;
  font-size: 0.9rem;
}

/* Custom Scrollbar for dropdown */
.country-dropdown-list::-webkit-scrollbar {
  width: 6px;
}
.country-dropdown-list::-webkit-scrollbar-track {
  background: transparent;
}
.country-dropdown-list::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.2);
  border-radius: 3px;
}

.phone-input {
  border: none;
  background: transparent;
  flex: 1;
  border-radius: 0;
}
.phone-input:focus {
  border-color: transparent;
  background: transparent;
}

.modal-footer {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(255,255,255,0.05);
  background: rgba(0,0,0,0.2);
}

.btn-back {
  background: transparent;
  color: var(--color-text-secondary, #a0a0a0);
  border: none;
  font-size: 1rem;
  cursor: pointer;
}

.btn-back:hover {
  color: white;
}

.btn-next, .btn-submit {
  background: var(--gradient-primary, linear-gradient(135deg, #06d6a0, #04ad80));
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  margin-left: auto;
  transition: opacity 0.2s;
}

.btn-next:disabled, .btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.progress-bar-container {
  height: 4px;
  background: rgba(255,255,255,0.1);
  width: 100%;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--color-accent, #06d6a0);
  transition: width 0.3s ease;
}

.animation-slide {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
