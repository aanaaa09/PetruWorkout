<template>
  <section class="social-proof">
    <div class="social-proof-container">
      <p class="proof-title">PERSONAS QUE HAN CONFIADO EN MÍ</p>

      <div class="proof-avatars">
        <div class="avatar-stack">
          <div class="avatar" v-for="n in 5" :key="n" :style="{ '--i': n }">
            <span>{{ getInitial(n) }}</span>
          </div>
          <div class="avatar-more">+997</div>
        </div>
        <div class="proof-text">
          <span class="count">+1000</span>
          <span class="label">transformaciones exitosas</span>
        </div>
      </div>

      <div class="trust-badges">
        <div class="badge">
          <span class="badge-icon">✓</span>
          <span>Certificado</span>
        </div>
        <div class="badge">
          <span class="badge-icon">🎯</span>
          <span>Resultados Garantizados</span>
        </div>
        <div class="badge">
          <span class="badge-icon">💪</span>
          <span>100% Online</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'SocialProof',
  methods: {
    getInitial(n) {
      const initials = ['M', 'J', 'A', 'C', 'L']
      return initials[n - 1] || '?'
    }
  }
}
</script>

<style scoped>
.social-proof {
  padding: 3rem 2rem;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.social-proof-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.proof-title {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin: 0;
}

.proof-avatars {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.avatar-stack {
  display: flex;
  align-items: center;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-accent), #ff6b7a);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: white;
  border: 3px solid var(--bg-primary);
  margin-left: calc(var(--i, 1) > 1 ? -15px : 0);
  position: relative;
  z-index: calc(10 - var(--i, 1));
}

.avatar-more {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.75rem;
  color: white;
  border: 3px solid var(--bg-primary);
  margin-left: -15px;
}

.proof-text {
  display: flex;
  flex-direction: column;
}

.proof-text .count {
  font-size: 1.75rem;
  font-weight: 900;
  color: white;
}

.proof-text .label {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.trust-badges {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  justify-content: center;
}

.badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50px;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.badge-icon {
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .proof-avatars {
    flex-direction: column;
    gap: 1rem;
  }

  .proof-text {
    align-items: center;
    text-align: center;
  }

  .trust-badges {
    gap: 1rem;
  }

  .badge {
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
  }
}
</style>
