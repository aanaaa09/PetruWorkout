<template>
  <section id="como-funciona" class="how-section">
    <div class="how-container">
      <div class="section-header">
        <span class="section-tag">CÓMO FUNCIONA</span>
        <h2 class="section-title">Tres pasos, sin compromiso</h2>
      </div>

      <ol class="steps">
        <li v-for="(step, i) in steps" :key="i" class="step">
          <span class="step-number">{{ i + 1 }}</span>
          <h3>{{ step.title }}</h3>
          <p>{{ step.text }}</p>
        </li>
      </ol>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HowItWorks',
  data() {
    return {
      steps: [
        { title: 'Respondes 5 preguntas', text: 'Objetivo, edad, nivel y qué te está frenando. Te lleva 30 segundos.' },
        { title: 'Reviso tu caso', text: 'Miro tus respuestas y te escribo yo mismo por WhatsApp con lo que veo que te está fallando.' },
        { title: 'Tú decides', text: 'Aplicas los consejos por tu cuenta o, si quieres, vemos cómo acompañarte. Sin presión.' },
      ],
    }
  },
}
</script>

<style scoped>
.how-section {
  padding: 5rem 2rem;
  background: var(--bg-primary);
}

.how-container {
  max-width: 1000px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-tag {
  font-size: 0.85rem;
  color: var(--color-accent);
  font-weight: 700;
  letter-spacing: 0.15em;
  display: block;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 2.25rem;
  font-weight: 800;
  color: white;
  margin: 0;
}

.steps {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.step {
  background: var(--bg-card);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 1.75rem 1.5rem;
  text-align: center;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: var(--gradient-primary);
  color: white;
  font-weight: 900;
  margin-bottom: 1rem;
}

.step h3 {
  margin: 0 0 0.5rem;
  font-size: 1.2rem;
  color: white;
}

.step p {
  margin: 0;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

@media (max-width: 768px) {
  .how-section { padding: 2.5rem 1.25rem; }
  .section-header { margin-bottom: 1.5rem; }
  .section-title { font-size: 1.5rem; }
  .steps { grid-template-columns: 1fr; gap: 0.75rem; }
  /* en móvil cada paso ocupa una fila compacta: número a la izquierda */
  .step {
    display: grid;
    grid-template-columns: auto 1fr;
    column-gap: 0.9rem;
    align-items: center;
    padding: 0.9rem 1rem;
    text-align: left;
  }
  .step-number { grid-row: 1 / 3; margin-bottom: 0; width: 2.2rem; height: 2.2rem; }
  .step h3 { font-size: 1.05rem; margin-bottom: 0.15rem; }
  .step p { font-size: 0.9rem; line-height: 1.4; }
}
</style>
