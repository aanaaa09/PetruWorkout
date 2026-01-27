<template>
  <div class="calculator-page">
    <div class="calculator-container">
      <div class="calculator-header">
        <h1>🔥 Calculadora de Calorías</h1>
        <p class="subtitle">
          Descubre cuántas calorías necesitas consumir diariamente según tus objetivos
        </p>
      </div>

      <form @submit.prevent="calculateCalories" class="calculator-form">
        <!-- Género -->
        <div class="form-group">
          <label class="form-label">Sexo</label>
          <div class="radio-group">
            <label class="radio-option">
              <input type="radio" v-model="formData.gender" value="male" required />
              <span>👨 Hombre</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="formData.gender" value="female" required />
              <span>👩 Mujer</span>
            </label>
          </div>
        </div>

        <!-- Edad -->
        <div class="form-group">
          <label class="form-label">Edad (años)</label>
          <input
            type="number"
            v-model.number="formData.age"
            placeholder="Ej: 25"
            min="15"
            max="100"
            required
            class="form-input"
          />
        </div>

        <!-- Peso -->
        <div class="form-group">
          <label class="form-label">Peso (kg)</label>
          <input
            type="number"
            v-model.number="formData.weight"
            placeholder="Ej: 70"
            min="30"
            max="300"
            step="0.1"
            required
            class="form-input"
          />
        </div>

        <!-- Estatura -->
        <div class="form-group">
          <label class="form-label">Estatura (cm)</label>
          <input
            type="number"
            v-model.number="formData.height"
            placeholder="Ej: 175"
            min="100"
            max="250"
            required
            class="form-input"
          />
        </div>

        <!-- Nivel de actividad -->
        <div class="form-group">
          <label class="form-label">Nivel de Actividad Física</label>
          <select v-model="formData.activityLevel" required class="form-select">
            <option value="">Selecciona tu nivel</option>
            <option value="sedentary">Sedentario (poco o ningún ejercicio)</option>
            <option value="light">Ligero (ejercicio 1-3 días/semana)</option>
            <option value="moderate">Moderado (ejercicio 3-5 días/semana)</option>
            <option value="active">Activo (ejercicio 6-7 días/semana)</option>
            <option value="very_active">Muy activo (ejercicio intenso diario)</option>
          </select>
        </div>

        <!-- Objetivo -->
        <div class="form-group">
          <label class="form-label">Objetivo</label>
          <select v-model="formData.goal" required class="form-select">
            <option value="">Selecciona tu objetivo</option>
            <option value="lose">Perder peso (déficit calórico)</option>
            <option value="maintain">Mantener peso (mantenimiento)</option>
            <option value="gain">Ganar masa muscular (superávit calórico)</option>
          </select>
        </div>

        <button type="submit" class="btn-calculate" :disabled="calculating">
          {{ calculating ? '⏳ Calculando...' : '🔥 Calcular Calorías' }}
        </button>

        <!-- Mensaje de error -->
        <div v-if="errorMessage" class="error-message">
          ❌ {{ errorMessage }}
        </div>
      </form>

      <!-- Resultados -->
      <transition name="fade">
        <div v-if="results" class="results-section">
          <h2 class="results-title">📊 Tus Resultados</h2>

          <div class="results-grid">
            <!-- IMC -->
            <div class="result-card">
              <div class="result-icon">⚖️</div>
              <h3>Índice de Masa Corporal (IMC)</h3>
              <div class="result-value">{{ results.bmi }}</div>
              <div class="result-status" :class="getBMIClass()">
                {{ getBMIStatus() }}
              </div>
            </div>

            <!-- Calorías Base -->
            <div class="result-card highlight">
              <div class="result-icon">🔥</div>
              <h3>Gasto Energético Basal (GEB)</h3>
              <div class="result-value">{{ results.bmr }} kcal</div>
              <p class="result-description">
                Calorías que quemas en reposo
              </p>
            </div>

            <!-- Calorías Totales -->
            <div class="result-card highlight">
              <div class="result-icon">💪</div>
              <h3>Gasto Energético Total (GET)</h3>
              <div class="result-value">{{ results.tdee }} kcal</div>
              <p class="result-description">
                Calorías totales que quemas al día
              </p>
            </div>

            <!-- Calorías Recomendadas -->
            <div class="result-card main-result">
              <div class="result-icon">🎯</div>
              <h3>Calorías Diarias Recomendadas</h3>
              <div class="result-value large">{{ results.recommended }} kcal</div>
              <p class="result-description">
                {{ getGoalDescription() }}
              </p>
            </div>
          </div>

          <!-- Distribución de Macronutrientes -->
          <div class="macros-section">
            <h3 class="macros-title">🍽️ Distribución de Macronutrientes Sugerida</h3>
            <div class="macros-grid">
              <div class="macro-card">
                <div class="macro-icon">🥩</div>
                <h4>Proteínas</h4>
                <div class="macro-value">{{ results.macros.protein }}g</div>
                <div class="macro-percentage">{{ results.macros.proteinCal }} kcal (30%)</div>
              </div>

              <div class="macro-card">
                <div class="macro-icon">🍚</div>
                <h4>Carbohidratos</h4>
                <div class="macro-value">{{ results.macros.carbs }}g</div>
                <div class="macro-percentage">{{ results.macros.carbsCal }} kcal (40%)</div>
              </div>

              <div class="macro-card">
                <div class="macro-icon">🥑</div>
                <h4>Grasas</h4>
                <div class="macro-value">{{ results.macros.fats }}g</div>
                <div class="macro-percentage">{{ results.macros.fatsCal }} kcal (30%)</div>
              </div>
            </div>
          </div>

          <!-- Consejos -->
          <div class="tips-section">
            <h3>💡 Consejos Importantes</h3>
            <ul class="tips-list">
              <li>
                <strong>Estos valores son una guía.</strong> Cada cuerpo es diferente y puede requerir ajustes.
              </li>
              <li>
                <strong>Sé consistente.</strong> Mantén un seguimiento durante 2-3 semanas y ajusta según tus resultados.
              </li>
              <li>
                <strong>Hidrátate bien.</strong> Bebe al menos 2-3 litros de agua al día.
              </li>
              <li>
                <strong>Calidad sobre cantidad.</strong> Prioriza alimentos nutritivos y naturales.
              </li>
              <li>
                <strong>¿Necesitas ayuda?</strong> Un plan personalizado puede acelerar tus resultados.
              </li>
            </ul>
          </div>

          <!-- CTA -->
          <div class="cta-section">
            <h3>🚀 ¿Quieres llevar esto al siguiente nivel?</h3>
            <p>
              Con mi programa personalizado, no solo sabrás qué comer, sino que tendrás un plan completo
              adaptado a ti con seguimiento directo y ajustes semanales.
            </p>
            <div class="cta-buttons">
              <a
                href="https://calendly.com/petruworkout/reunion"
                target="_blank"
                rel="noopener noreferrer"
                class="btn-calendly"
              >
                📅 Agendar Llamada Gratuita
              </a>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CalorieCalculator',
  data() {
    return {
      formData: {
        gender: '',
        age: null,
        weight: null,
        height: null,
        activityLevel: '',
        goal: ''
      },
      results: null,
      calculating: false,
      errorMessage: ''
    }
  },
  methods: {
    async calculateCalories() {
      this.calculating = true
      this.errorMessage = ''

      try {
        // Llamar a la API del backend
        const response = await fetch('https://petruworkout-production.up.railway.app/api/calculator/calculate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            gender: this.formData.gender,
            age: this.formData.age,
            weight: this.formData.weight,
            height: this.formData.height,
            activity_level: this.formData.activityLevel,
            goal: this.formData.goal
          })
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Error al calcular calorías')
        }

        const data = await response.json()

        // Mapear la respuesta del backend al formato del frontend
        this.results = {
          bmi: data.bmi,
          bmr: data.bmr,
          tdee: data.tdee,
          recommended: data.recommended,
          macros: {
            protein: data.macros.protein,
            carbs: data.macros.carbs,
            fats: data.macros.fats,
            proteinCal: data.macros.protein_cal,
            carbsCal: data.macros.carbs_cal,
            fatsCal: data.macros.fats_cal
          }
        }

        // Scroll a resultados
        this.$nextTick(() => {
          const resultsEl = document.querySelector('.results-section')
          if (resultsEl) {
            resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }
        })
      } catch (error) {
        console.error('Error al calcular calorías:', error)
        this.errorMessage = error.message || 'Error al calcular calorías. Por favor, intenta de nuevo.'
      } finally {
        this.calculating = false
      }
    },

    getBMIStatus() {
      const bmi = parseFloat(this.results.bmi)
      if (bmi < 18.5) return 'Bajo peso'
      if (bmi < 25) return 'Peso normal'
      if (bmi < 30) return 'Sobrepeso'
      return 'Obesidad'
    },

    getBMIClass() {
      const bmi = parseFloat(this.results.bmi)
      if (bmi < 18.5) return 'status-low'
      if (bmi < 25) return 'status-normal'
      if (bmi < 30) return 'status-warning'
      return 'status-high'
    },

    getGoalDescription() {
      if (this.formData.goal === 'lose') {
        return 'Para perder peso de forma saludable (déficit de 500 kcal/día)'
      } else if (this.formData.goal === 'maintain') {
        return 'Para mantener tu peso actual'
      } else {
        return 'Para ganar masa muscular (superávit de 300 kcal/día)'
      }
    }
  }
}
</script>

<style scoped>
/* (Los estilos permanecen exactamente igual que antes) */
.calculator-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 8rem 2rem 4rem;
}

.calculator-container {
  max-width: 900px;
  margin: 0 auto;
}

.calculator-header {
  text-align: center;
  margin-bottom: 3rem;
}

.calculator-header h1 {
  font-size: 3rem;
  font-weight: 900;
  color: white;
  margin: 0 0 1rem 0;
  background: linear-gradient(135deg, var(--color-accent) 0%, #4dffb8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.2rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.calculator-form {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-label {
  font-size: 1rem;
  font-weight: 600;
  color: white;
}

.form-input,
.form-select {
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--color-accent);
  background: rgba(255, 255, 255, 0.08);
}

.form-select option {
  background: var(--bg-secondary);
  color: white;
}

.radio-group {
  display: flex;
  gap: 1rem;
}

.radio-option {
  flex: 1;
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.radio-option:hover {
  border-color: var(--color-accent);
  background: rgba(255, 255, 255, 0.08);
}

.radio-option input[type="radio"] {
  accent-color: var(--color-accent);
}

.radio-option span {
  font-size: 1.1rem;
  color: white;
  font-weight: 500;
}

.btn-calculate {
  padding: 1.25rem 2rem;
  background: var(--gradient-primary);
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
}

.btn-calculate:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.6);
}

.btn-calculate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: rgba(239, 35, 60, 0.15);
  border: 1px solid rgba(239, 35, 60, 0.3);
  color: #ff6b6b;
  padding: 1rem;
  border-radius: 10px;
  text-align: center;
  font-weight: 600;
}

.results-section {
  margin-top: 4rem;
  animation: fadeIn 0.5s ease;
}

.results-title {
  font-size: 2rem;
  color: white;
  text-align: center;
  margin: 0 0 2rem 0;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.result-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
}

.result-card.highlight {
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.1) 0%, rgba(6, 214, 160, 0.05) 100%);
  border-color: rgba(6, 214, 160, 0.3);
}

.result-card.main-result {
  grid-column: 1 / -1;
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.15) 0%, rgba(6, 214, 160, 0.1) 100%);
  border: 2px solid var(--color-accent);
}

.result-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.result-card h3 {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0 0 1rem 0;
}

.result-value {
  font-size: 2.5rem;
  font-weight: 900;
  color: var(--color-accent);
  margin: 0 0 0.5rem 0;
}

.result-value.large {
  font-size: 3rem;
}

.result-description {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin: 0;
}

.result-status {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  margin-top: 0.5rem;
}

.status-low {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.status-normal {
  background: rgba(6, 214, 160, 0.2);
  color: var(--color-accent);
}

.status-warning {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
}

.status-high {
  background: rgba(239, 35, 60, 0.2);
  color: #ef233c;
}

.macros-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 2.5rem;
  margin-bottom: 3rem;
}

.macros-title {
  font-size: 1.5rem;
  color: white;
  text-align: center;
  margin: 0 0 2rem 0;
}

.macros-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.macro-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.macro-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.macro-card h4 {
  font-size: 1rem;
  color: white;
  margin: 0 0 0.75rem 0;
}

.macro-value {
  font-size: 2rem;
  font-weight: 900;
  color: var(--color-accent);
  margin: 0 0 0.25rem 0;
}

.macro-percentage {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.tips-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 2.5rem;
  margin-bottom: 3rem;
}

.tips-section h3 {
  font-size: 1.5rem;
  color: white;
  margin: 0 0 1.5rem 0;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tips-list li {
  padding-left: 1.5rem;
  position: relative;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.tips-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--color-accent);
  font-weight: 700;
}

.cta-section {
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.15) 0%, rgba(6, 214, 160, 0.05) 100%);
  border: 2px solid var(--color-accent);
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
}

.cta-section h3 {
  font-size: 2rem;
  color: white;
  margin: 0 0 1rem 0;
}

.cta-section p {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0 0 2rem 0;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-whatsapp,
.btn-calendly {
  padding: 1.25rem 2rem;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-whatsapp {
  background: linear-gradient(135deg, #25D366, #128C7E);
  color: white;
  box-shadow: 0 8px 30px rgba(37, 211, 102, 0.4);
}

.btn-whatsapp:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(37, 211, 102, 0.6);
}

.btn-calendly {
  background: var(--gradient-primary);
  color: white;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
}

.btn-calendly:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.6);
}

.fade-enter-active {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .calculator-page {
    padding: 6rem 1rem 3rem;
  }

  .calculator-header h1 {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .calculator-form {
    padding: 1.5rem;
  }

  .radio-group {
    flex-direction: column;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }

  .macros-grid {
    grid-template-columns: 1fr;
  }

  .cta-buttons {
    flex-direction: column;
  }

  .btn-whatsapp,
  .btn-calendly {
    width: 100%;
    justify-content: center;
  }
}
</style>
