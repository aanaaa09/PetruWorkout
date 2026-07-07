<template>
  <div class="mejorar-page">
    <SimpleNavbar />
    <div class="content-wrapper">
      
      <div class="diagnosis-content">
        <h2 class="card-title">Fase de aprendizaje 📚</h2>
        
        <div class="card-body">
          <p>
            Estás en una etapa inicial en calistenia. Mi recomendación es que te centres en aprender bien la técnica y entrenar duro antes de preocuparte por bajar grasa o ganar músculo 💪. Ahora mismo tu cuerpo todavía está en desarrollo, y lo más importante es construir una base sólida 🦴.
          </p>
          
          <p>
            Te dejo aquí un curso completo con todos los ejercicios de calistenia para que sigas avanzando y no te estanques 👇
          </p>
        </div>

        <div class="video-wrapper">
          <iframe 
            width="100%" 
            height="100%" 
            src="https://www.youtube.com/embed/Z2qF0E205gA?rel=0&modestbranding=1" 
            title="Curso de Calistenia" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
          </iframe>
        </div>

        <div class="card-footer">
          <p><strong>Si haces esto bien durante unas semanas, vas a notar un cambio real en tu fuerza y control.</strong></p>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import SimpleNavbar from '@/components/navigation/SimpleNavbar.vue'

export default {
  name: 'MejorarView',
  components: {
    SimpleNavbar
  }
}
</script>

<style scoped>
.mejorar-page {
  min-height: 100vh;
  background: var(--bg-primary, #0d0d0d);
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  flex: 1;
  max-width: 1100px;
  margin: 0 auto;
  padding: 6rem 1rem 4rem; /* Matching the /fuerza page padding */
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.diagnosis-content {
  width: 100%;
}

.card-title {
  font-size: clamp(2rem, 5vw, 2.5rem);
  font-weight: 900;
  color: var(--color-accent, #06d6a0);
  margin-bottom: 1.5rem;
  text-align: center;
}

.card-body {
  font-size: 1.15rem;
  color: var(--color-text-secondary, #e0e0e0);
  line-height: 1.6;
  text-align: center;
  margin-bottom: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.video-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  background: #000;
  margin-bottom: 2.5rem;
}

.video-wrapper iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.card-footer {
  text-align: center;
  font-size: 1.15rem;
  color: white;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.card-footer strong {
  font-weight: 700;
  color: white;
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 5.5rem 1rem 3rem;
  }
  
  .card-title {
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
  }
  
  .card-body {
    font-size: 1.05rem;
    gap: 1.25rem;
    margin-bottom: 2rem;
  }
  
  .card-footer {
    font-size: 1.05rem;
  }
}
</style>
