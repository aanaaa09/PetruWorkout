<template>
  <section class="guarantee-section">
    <div class="guarantee-container">
      <div class="guarantee-badge">
        <div class="badge-icon">🛡️</div>
        <div class="badge-text">100%</div>
        <div class="badge-subtext">GARANTÍA</div>
      </div>

      <div class="guarantee-content">
        <h2 class="guarantee-title">
          Garantía de Devolución <span class="accent">100%</span>
        </h2>

        <p class="guarantee-text">
          Si después de <strong>90 días</strong> siguiendo mi programa al 100%,
          no consigues los resultados prometidos (menos de 20% de grasa y +3kg de músculo),
          <strong>te devuelvo TODO tu dinero</strong>.
        </p>

        <p class="guarantee-text highlight">
          Sin preguntas. Sin complicaciones. Firmado por contrato.
        </p>

        <div class="guarantee-points">
          <div class="point">
            <span class="point-icon">📝</span>
            <div>
              <h4>Firmado por Contrato</h4>
              <p>Acuerdo legal que protege tu inversión</p>
            </div>
          </div>

          <div class="point">
            <span class="point-icon">💰</span>
            <div>
              <h4>Devolución Completa</h4>
              <p>El 100% de tu dinero de vuelta</p>
            </div>
          </div>

          <div class="point">
            <span class="point-icon">⏱️</span>
            <div>
              <h4>90 Días para Probarlo</h4>
              <p>Tiempo suficiente para ver resultados</p>
            </div>
          </div>
        </div>

        <p class="guarantee-note">
          * La garantía aplica solo si sigues el programa al 100% y cumples con
          los requisitos de seguimiento establecidos.
        </p>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'GuaranteeSection'
}
</script>

<style scoped>
.guarantee-section {
  padding: 6rem 2rem;
  background: linear-gradient(135deg, rgba(230, 57, 70, 0.15) 0%, rgba(230, 57, 70, 0.05) 100%);
  border-top: 1px solid rgba(230, 57, 70, 0.2);
  border-bottom: 1px solid rgba(230, 57, 70, 0.2);
}

.guarantee-container {
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 4rem;
  align-items: center;
}

.guarantee-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 180px;
  height: 180px;
  background: var(--gradient-primary);
  border-radius: 50%;
  box-shadow: 0 20px 50px rgba(230, 57, 70, 0.4);
  position: relative;
}

.guarantee-badge::before {
  content: '';
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  border: 3px dashed rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.badge-icon {
  font-size: 2.5rem;
}

.badge-text {
  font-size: 2.5rem;
  font-weight: 900;
  color: white;
  line-height: 1;
}

.badge-subtext {
  font-size: 0.85rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 0.1em;
}

.guarantee-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.guarantee-title {
  font-size: 2.25rem;
  font-weight: 800;
  color: white;
  margin: 0;
  line-height: 1.2;
}

.guarantee-title .accent {
  color: var(--color-accent);
}

.guarantee-text {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin: 0;
}

.guarantee-text strong {
  color: white;
}

.guarantee-text.highlight {
  color: white;
  font-weight: 600;
  font-size: 1.2rem;
}

.guarantee-points {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-top: 1rem;
}

.point {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.point-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.point h4 {
  font-size: 1rem;
  color: white;
  margin: 0 0 0.25rem 0;
}

.point p {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin: 0;
}

.guarantee-note {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  margin: 1rem 0 0 0;
  font-style: italic;
}

@media (max-width: 968px) {
  .guarantee-container {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 2.5rem;
  }

  .guarantee-badge {
    margin: 0 auto;
    width: 150px;
    height: 150px;
  }

  .badge-text {
    font-size: 2rem;
  }

  .guarantee-points {
    grid-template-columns: 1fr;
    text-align: left;
  }

  .point {
    background: rgba(255, 255, 255, 0.03);
    padding: 1rem;
    border-radius: 12px;
  }
}

@media (max-width: 640px) {
  .guarantee-section {
    padding: 4rem 1rem;
  }

  .guarantee-title {
    font-size: 1.75rem;
  }

  .guarantee-text {
    font-size: 1rem;
  }

  .guarantee-badge {
    width: 130px;
    height: 130px;
  }

  .badge-icon {
    font-size: 2rem;
  }

  .badge-text {
    font-size: 1.75rem;
  }
}
</style>
