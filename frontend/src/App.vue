<template>
  <div id="app">
    <router-view />
    <CookieBanner />
  </div>
</template>

<script>
import { initTracking, getOrCreateSessionId, getTrafficSourceFromSession } from './utils/tracking'
import CookieBanner from "@/components/CookieBanner.vue";

export default {
  name: 'App',
  components: {CookieBanner},
  mounted() {
    // Inicializar tracking cuando la app se carga
    initTracking()

    // ✅ NUEVO: Escuchar eventos de Calendly
    this.setupCalendlyListener()

    // Añadir preconnect para Google Fonts si no existe
    if (!document.querySelector('link[href="https://fonts.googleapis.com"]')) {
      const preconnect1 = document.createElement('link');
      preconnect1.rel = 'preconnect';
      preconnect1.href = 'https://fonts.googleapis.com';
      document.head.appendChild(preconnect1);

      const preconnect2 = document.createElement('link');
      preconnect2.rel = 'preconnect';
      preconnect2.href = 'https://fonts.gstatic.com';
      preconnect2.crossOrigin = 'anonymous';
      document.head.appendChild(preconnect2);
    }
  },
  methods: {
    setupCalendlyListener() {
      window.addEventListener('message', this.handleCalendlyEvent)
    },

    async handleCalendlyEvent(e) {
      // Solo procesar eventos de Calendly
      if (e.origin !== 'https://calendly.com' && e.origin !== 'https://calendly.com') {
        return
      }

      // Detectar cuando completan la reserva
      if (e.data && e.data.event === 'calendly.event_scheduled') {
        console.log('🎉 ¡Reserva completada en Calendly!', e.data)

        const sessionId = getOrCreateSessionId()
        const trafficSource = getTrafficSourceFromSession()

        const bookingData = {
          session_id: sessionId,
          traffic_source: trafficSource,
          invitee_email: e.data.payload?.invitee?.email || 'unknown',
          invitee_name: e.data.payload?.invitee?.name || 'unknown',
          event_uri: e.data.payload?.event?.uri || null,
          event_start_time: e.data.payload?.event?.start_time || null
        }

        try {
          const response = await fetch('https://petruworkout-production.up.railway.app/api/tracking/booking-completed', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(bookingData)
          })

          if (response.ok) {
            console.log('✅ Reserva guardada en la base de datos')
          } else {
            console.error('❌ Error al guardar reserva:', await response.text())
          }
        } catch (error) {
          console.error('❌ Error de conexión al guardar reserva:', error)
        }
      }
    }
  },
  beforeUnmount() {
    // Limpiar listener cuando se destruya la app
    window.removeEventListener('message', this.handleCalendlyEvent)
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

#app {
  min-height: 100vh;
  background: var(--bg-primary);
}
</style>
