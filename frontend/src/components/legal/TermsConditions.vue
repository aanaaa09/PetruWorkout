<template>
  <div class="legal-page">
    <div class="legal-container">
      <div class="legal-header">
        <button @click="goBack" class="btn-back">
          ← Volver al inicio
        </button>
        <h1>📄 Términos y Condiciones</h1>
        <p class="last-update">Última actualización: {{ new Date().toLocaleDateString('es-ES') }}</p>
      </div>

      <div class="legal-content">
        <section>
          <h2>1. Aceptación de los Términos</h2>
          <p>Al acceder y utilizar los servicios de PetruWorkout, usted acepta estar sujeto a estos Términos y Condiciones. Si no está de acuerdo con alguna parte de estos términos, no debe utilizar nuestros servicios.</p>
        </section>

        <section>
          <h2>2. Descripción del Servicio</h2>
          <p>PetruWorkout ofrece servicios de entrenamiento personal online especializado en calistenia, incluyendo:</p>
          <ul>
            <li>Programas de entrenamiento personalizados</li>
            <li>Planes de nutrición adaptados</li>
            <li>Seguimiento y asesoramiento continuo</li>
            <li>Acceso a contenido exclusivo y recursos</li>
          </ul>
        </section>

        <section>
          <h2>3. Registro y Cuenta de Usuario</h2>
          <p>Para acceder a ciertos servicios, deberá crear una cuenta proporcionando información precisa y actualizada. Usted es responsable de mantener la confidencialidad de su contraseña y de todas las actividades que ocurran bajo su cuenta.</p>
          <div class="info-box">
            <p><strong>Importante:</strong> Notifique inmediatamente cualquier uso no autorizado de su cuenta.</p>
          </div>
        </section>

        <section>
          <h2>4. Uso Aceptable</h2>
          <p>Al utilizar nuestros servicios, usted se compromete a:</p>
          <ul>
            <li>No compartir su cuenta con terceros</li>
            <li>No reproducir, distribuir o comercializar el contenido sin autorización</li>
            <li>No utilizar el servicio para fines ilegales o no autorizados</li>
            <li>Seguir las instrucciones y recomendaciones de seguridad proporcionadas</li>
          </ul>
        </section>

        <section>
          <h2>5. Propiedad Intelectual</h2>
          <p>Todo el contenido disponible en PetruWorkout, incluyendo pero no limitado a textos, gráficos, logotipos, imágenes, videos, programas de entrenamiento y planes de nutrición, es propiedad de Adrián Petru Oltean y está protegido por las leyes de propiedad intelectual.</p>
          <p>Se prohíbe expresamente la reproducción, distribución, modificación o uso comercial del contenido sin autorización previa por escrito.</p>
        </section>

        <section>
          <h2>6. Servicios de Pago y Suscripciones</h2>
          <h3>6.1 Facturación</h3>
          <p>Los servicios de pago se facturan de forma mensual, trimestral o anual según el plan seleccionado. El primer cargo se realiza al momento de la compra y los subsecuentes en la misma fecha de cada período.</p>

          <h3>6.2 Cancelación</h3>
          <p>Puede cancelar su suscripción en cualquier momento enviando un correo a <a href="mailto:info.petrusw@gmail.com">info.petrusw@gmail.com</a> con al menos 72 horas de antelación a la próxima fecha de facturación.</p>

          <h3>6.3 Reembolsos</h3>
          <p>Ofrecemos garantía de devolución según lo especificado en nuestro Aviso Legal. Los reembolsos se procesan en un plazo de 5-10 días hábiles.</p>
        </section>

        <section>
          <h2>7. Limitación de Responsabilidad</h2>
          <div class="warning-box">
            <p><strong>⚠️ IMPORTANTE</strong></p>
          </div>
          <p>PetruWorkout no se hace responsable de:</p>
          <ul>
            <li>Lesiones físicas derivadas de la práctica incorrecta de los ejercicios</li>
            <li>Resultados individuales, que pueden variar según múltiples factores</li>
            <li>Problemas de salud preexistentes o no diagnosticados</li>
            <li>Uso del servicio sin supervisión médica adecuada</li>
          </ul>
          <p><strong>Consulte siempre con un médico antes de comenzar cualquier programa de entrenamiento o nutrición.</strong></p>
        </section>

        <section>
          <h2>8. Modificaciones del Servicio</h2>
          <p>Nos reservamos el derecho de modificar, suspender o descontinuar cualquier aspecto del servicio en cualquier momento sin previo aviso. No seremos responsables ante usted ni ante terceros por cualquier modificación, suspensión o descontinuación del servicio.</p>
        </section>

        <section>
          <h2>9. Privacidad y Protección de Datos</h2>
          <p>El tratamiento de sus datos personales se rige por nuestra Política de Privacidad. Al utilizar nuestros servicios, acepta dicho tratamiento conforme a lo establecido en dicha política.</p>
        </section>

        <section>
          <h2>10. Ley Aplicable y Jurisdicción</h2>
          <p>Estos Términos y Condiciones se rigen por las leyes españolas. Para cualquier controversia derivada de estos términos, las partes se someten a los juzgados y tribunales del domicilio del usuario.</p>
        </section>

        <section>
          <h2>11. Contacto</h2>
          <p>Para cualquier consulta relacionada con estos Términos y Condiciones, puede contactarnos en:</p>
          <div class="info-box">
            <p><strong>Email:</strong> <a href="mailto:info.petrusw@gmail.com">info.petrusw@gmail.com</a></p>
            <p><strong>Titular:</strong> Adrián Petru Oltean</p>
          </div>
        </section>

        <section>
          <h2>12. Aceptación de Modificaciones</h2>
          <p>Nos reservamos el derecho de actualizar estos Términos y Condiciones en cualquier momento. Las modificaciones entrarán en vigor inmediatamente después de su publicación en el sitio web. El uso continuado del servicio después de dichas modificaciones constituye su aceptación de los nuevos términos.</p>
        </section>
      </div>

      <div class="legal-footer">
        <button @click="goBack" class="btn-back-footer">
          ← Volver al inicio
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TermsConditions',
  methods: {
    goBack() {
       this.$router.push('/')
      this.$nextTick(() => {
        window.scrollTo(0, 0)
      })
    }
  }
}
</script>

<style scoped>
.legal-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 2rem;
}

.legal-container {
  max-width: 900px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  padding: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.legal-header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

.btn-back {
  position: absolute;
  left: 0;
  top: 0;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(-5px);
}

.legal-header h1 {
  font-size: 2.5rem;
  color: white;
  margin: 0 0 0.5rem 0;
}

.last-update {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.legal-content {
  color: var(--color-text-secondary);
  line-height: 1.8;
}

.legal-content section {
  margin-bottom: 2.5rem;
}

.legal-content h2 {
  color: var(--color-accent);
  font-size: 1.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(230, 57, 70, 0.3);
}

.legal-content h3 {
  color: white;
  font-size: 1.2rem;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.legal-content p {
  margin-bottom: 1rem;
  text-align: justify;
}

.legal-content ul {
  margin: 1rem 0;
  padding-left: 2rem;
}

.legal-content li {
  margin-bottom: 0.5rem;
}

.legal-content a {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
}

.legal-content a:hover {
  text-decoration: underline;
}

.warning-box {
  background: rgba(255, 193, 7, 0.15);
  border: 2px solid rgba(255, 193, 7, 0.5);
  border-radius: 10px;
  padding: 1.5rem;
  margin: 1rem 0;
}

.warning-box p {
  margin: 0;
  color: #ffc107;
  font-size: 1.1rem;
  text-align: center;
}

.info-box {
  background: rgba(230, 57, 70, 0.1);
  border: 1px solid rgba(230, 57, 70, 0.3);
  border-radius: 10px;
  padding: 1.5rem;
  margin: 1rem 0;
}

.info-box p {
  margin-bottom: 0.5rem;
  text-align: left;
}

.info-box p:last-child {
  margin-bottom: 0;
}

.legal-footer {
  text-align: center;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-back-footer {
  background: var(--gradient-primary);
  border: none;
  color: white;
  padding: 1rem 2rem;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(230, 57, 70, 0.3);
}

.btn-back-footer:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(230, 57, 70, 0.4);
}

@media (max-width: 768px) {
  .legal-container {
    padding: 2rem 1.5rem;
  }

  .legal-header h1 {
    font-size: 2rem;
    margin-top: 3rem;
  }

  .btn-back {
    position: static;
    margin-bottom: 1.5rem;
    width: 100%;
  }

  .legal-content {
    text-align: left;
  }
}
</style>
