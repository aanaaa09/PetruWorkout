<template>
  <section id="dudas" class="faq-section">
    <div class="faq-container">
      <div class="section-header">
        <span class="section-tag">DUDAS FRECUENTES</span>
        <h2 class="section-title">Antes de empezar</h2>
      </div>

      <details v-for="(item, i) in items" :key="i" class="faq-item">
        <summary>{{ item.q }}</summary>
        <p>{{ item.a }}</p>
      </details>
    </div>
  </section>
</template>

<script>
export default {
  name: 'FaqSection',
  data() {
    return {
      items: [
        {
          q: '¿Tiene algún coste el diagnóstico?',
          a: 'No. Respondes, te escribo con lo que veo en tu caso y tú decides si quieres algo más. Si te interesa mi asesoría, ahí te cuento cómo funciona y cuánto cuesta.'
        },
        {
          q: '¿Necesito gimnasio o material?',
          a: 'No. Se entrena en casa o en el parque, con tu propio peso corporal.'
        },
        {
          q: '¿Y si empiezo desde cero o tengo más de 40 años?',
          a: 'Puedes empezar desde cero. Entre mis clientes hay personas desde los 27 hasta los 63 años, y el plan se adapta a tu nivel.'
        },
        {
          q: '¿Por qué me pides el teléfono?',
          a: 'Para escribirte yo mismo por WhatsApp con tu diagnóstico. Sin comerciales ni llamadas que no pidas.'
        },
      ],
    }
  },
}
</script>

<style scoped>
.faq-section {
  padding: 5rem 2rem;
  background: var(--bg-secondary);
}

.faq-container {
  max-width: 760px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 2.5rem;
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

.faq-item {
  background: var(--bg-card);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  margin-bottom: 0.75rem;
  overflow: hidden;
}

.faq-item[open] {
  border-color: rgba(6, 214, 160, 0.3);
}

.faq-item summary {
  list-style: none;
  cursor: pointer;
  padding: 1.1rem 1.25rem;
  color: white;
  font-weight: 700;
  font-size: 1.05rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.faq-item summary::-webkit-details-marker { display: none; }
.faq-item summary::after {
  content: '+';
  color: var(--color-accent);
  font-size: 1.5rem;
  line-height: 1;
  flex-shrink: 0;
}
.faq-item[open] summary::after { content: '–'; }

.faq-item p {
  margin: 0;
  padding: 0 1.25rem 1.25rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .faq-section { padding: 3.5rem 1.25rem; }
  .section-title { font-size: 1.75rem; }
  .faq-item summary { font-size: 1rem; }
}
</style>
