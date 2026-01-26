<template>
  <div class="legal-page">
    <div class="legal-container">
      <div class="legal-header">
        <button @click="goBack" class="btn-back">
          ← Volver al inicio
        </button>
        <h1>⚖️ Aviso Legal</h1>
        <p class="last-update">Última actualización: {{ new Date().toLocaleDateString('es-ES') }}</p>
      </div>

      <div class="legal-content">
        <section>
          <h2>Riesgos del Uso del Producto</h2>
          <div class="warning-box">
            <p><strong>⚠️ IMPORTANTE: LEA DETENIDAMENTE</strong></p>
          </div>
          <p>El contenido de este sitio web no reemplaza a la atención médica ni al diagnóstico directo, personal y profesional. Ninguno de los planes de comidas o programas de ejercicios debe realizarse o usarse de otra manera sin la autorización previa de su médico o proveedor de atención médica. La información contenida en este documento no tiene la intención de proporcionar consejos específicos de salud física o mental, o cualquier otro consejo, para ninguna persona o empresa y no se debe confiar en ese aspecto. No somos profesionales médicos y nada en este sitio web debe malinterpretarse en el sentido contrario.</p>

          <p>Puede haber riesgos asociados con la participación en actividades mencionadas en nuestro sitio para personas con problemas de salud o con afecciones físicas o mentales preexistentes. Debido a que existen estos riesgos, no participará en ningún plan de comidas disponible de nosotros si tiene mala salud o tiene una condición mental o física preexistente. Si elige participar en estos riesgos, lo hace por su propia voluntad y acuerdo, asumiendo a sabiendas y voluntariamente todos los riesgos asociados con tales actividades dietéticas. Estos riesgos también pueden existir para aquellos que actualmente gozan de buena salud en este momento.</p>

          <p>Como con cualquier programa de ejercicios, usted asume ciertos riesgos para su salud y seguridad. Cualquier forma de programa de ejercicios puede causar lesiones, y nuestros programas no son una excepción. Es posible que se lastime haciendo los ejercicios en su programa, especialmente si los ejecuta con una mala forma o técnica. Aunque se incluye una instrucción completa en el formulario para cada ejercicio. Tenga en cuenta que nuestros programas (como cualquier otro programa de ejercicios) implican un riesgo de lesión. Si elige participar en estos riesgos, lo hace por su propia voluntad y acuerdo, asumiendo a sabiendas y voluntariamente todos los riesgos asociados con tales actividades de ejercicio. Estos riesgos también pueden existir para aquellos que actualmente gozan de buena salud en este momento.</p>

          <p><strong>No somos médicos.</strong> Nuestros consejos, ya sea en nuestro sitio web, en nuestro plan de comidas, en nuestro programa de ejercicios o por correo electrónico, no pretenden sustituir el asesoramiento médico. Debe consultar a su médico antes de comenzar CUALQUIER plan de comidas o programa de ejercicios, sin excepciones. Está utilizando nuestros planes, programas de entrenamientos y tutorías bajo su propio riesgo y no somos responsables de ninguna lesión o problema de salud que pueda experimentar o incluso la muerte como resultado del uso de nuestros programas.</p>
        </section>

        <section>
          <h2>Resultados Generalmente Esperados</h2>
          <p>Aunque nuestros productos y servicios están destinados a ser implementados en su totalidad, a veces no lo son, lo que podría resultar en una falta de progreso / resultados para el usuario. Si implementa correctamente nuestros productos y servicios, debería ver resultados satisfactorios, sin embargo, debe aclararse que incluso cuando los consumidores implementen todos nuestros productos o servicios, aun así, es posible que no obtengan los resultados que podrían haber esperado y también es posible que no pierdan grasa ni ganen músculo ni tengan ningún resultado positivo de ningún tipo.</p>
        </section>

        <section>
          <h2>Renuncia de Responsabilidad Testimonial</h2>
          <p>Todas las transformaciones y testimonios son reales. Sin embargo, se aclara que estos testimonios no representan resultados típicos con nuestros planes de comidas y programas de entrenamiento. Están diseñados como una vitrina de lo que las personas más motivadas y dedicadas pueden lograr siguiendo nuestros planes de entrenamiento y plan de comidas personalizados. Tus resultados pueden variar y es posible que no obtengas los mismos resultados en comparación con otra persona cuando utiliza nuestros servicios debido a diferencias en su historial de ejercicio individual, genética y motivación / dedicación personal. Los resultados finales que obtenga dependen del individuo y de cuanto esfuerzo ponga.</p>
        </section>

        <section>
          <h2>Política de Envíos</h2>
          <p>Al tratarse de un servicio, no habrá envíos presenciales, sin embargo la entrega de algunos de mis servicios online se realizarán en un plazo de entre 24-36 horas desde que el cliente realiza la compra.</p>
        </section>

        <section>
          <h2>Cancelación de Pedidos y Devolución y Reembolso</h2>
          <p>Con nuestros productos en línea, tenemos una <strong>garantía de devolución del dinero de 14 días</strong>: si dentro de los primeros 14 días de su compra inicial no está feliz o satisfecho con alguna de sus compras (servicios de suscripción y sin suscripción) por cualquier razón, simplemente solicite un reembolso completo poniéndose en contacto con el equipo de Atención al cliente <a href="mailto:info.petrusw@gmail.com">info.petrusw@gmail.com</a>. Se le reembolsará y se cancelará su suscripción. Sin embargo, si ha comprado un programa durante un periodo promocional y ha canjeado esa promoción (por ejemplo, suplementos, ropa, auriculares), no será elegible para un reembolso.</p>
        </section>

        <section>
          <h2>Seguridad y Protección a Compradores</h2>
          <p>Visa/Mastercard: el usuario deberá proporcionar el nombre del titular de la tarjeta, el número, la fecha de caducidad y el CVV.</p>
          <p>Toda la información será tramitada a través de una pasarela de pagos externa a PETRU WORKOUT denominada <strong>Stripe</strong>, pudiendo obtener más información visitando su página web <a href="https://stripe.com/es/privacy" target="_blank" rel="noopener noreferrer">https://stripe.com/es/privacy</a></p>
          <p>La cuota de suscripción se cobrará en la fecha de facturación indicada tras la adquisición de la formación y se realizará de forma mensual, trimestral o anual, según la modalidad adquirida.</p>
        </section>

        <section>
          <h2>Información de Facturación de la Suscripción Recurrente</h2>
          <div class="info-box">
            <p><strong>IMPORTANTE</strong></p>
          </div>
          <p>Si compra nuestro programa, se le cobrará automáticamente cada periodo y continuará recibiendo nuevos planes de comidas y programas de entrenamiento actualizados durante el tiempo que elija seguir siendo cliente. Para cancelar su suscripción, simplemente envíe un correo electrónico a <a href="mailto:info.petrusw@gmail.com">info.petrusw@gmail.com</a> al menos 3 días (72 horas) antes de su próximo día de facturación.</p>
          <p>Con nuestros productos en línea, tenemos una <strong>garantía de devolución del dinero de 5 días</strong>: si dentro de los primeros 5 días de su compra inicial (primera) no está feliz o satisfecho con alguna de sus compras (servicios de suscripción) por cualquier razón, simplemente solicite un reembolso completo poniéndose en contacto con el equipo de Atención al cliente. Se le reembolsará y se cancelará su suscripción.</p>
        </section>

        <section>
          <h2>Contacto</h2>
          <p>¿Tiene preguntas acerca de esto? ¡Envíanos un email! Puedes ponerte en contacto con nuestro equipo de atención al cliente en <a href="mailto:info.petrusw@gmail.com">info.petrusw@gmail.com</a> y estaremos encantados de responder a cualquiera de sus preguntas.</p>
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
  name: 'LegalNotice',
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

.legal-content p {
  margin-bottom: 1rem;
  text-align: justify;
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
  margin: 0;
  text-align: center;
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
