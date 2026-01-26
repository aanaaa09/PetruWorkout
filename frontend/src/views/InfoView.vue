<template>
  <div class="info-view">
    <FullNavbar @scroll-to="scrollToSection" />

    <main>
      <AboutSection id="sobre-mi" />
      <ServicesSection id="servicios" />
      <GuaranteeSection />

      <!-- ✅ Botón del grupo justo después del texto principal -->
      <section id="join-group" class="join-group-section">
        <p class="join-text">Estás a un paso de unirte al grupo y recibir tu regalo exclusivo</p>
        <button
          @click="goToGroup"
          class="btn-join-group"
        >
          🎁 Accede al grupo de WhatsApp
        </button>
      </section>

      <ContactForm id="contacto" />
    </main>

    <!-- Footer solo si no hay legal -->
    <FullFooter v-if="!currentLegalPage" @show-legal="showLegalPage" />

    <!-- Páginas legales -->
    <component
      v-if="currentLegalPage"
      :is="currentLegalComponent"
      @close="closeLegalPage"
    />
  </div>
</template>

<script>
import FullNavbar from '@/components/navigation/FullNavbar.vue'
import AboutSection from '@/components/landing/AboutSection.vue'
import ServicesSection from '@/components/landing/ServicesSection.vue'
import GuaranteeSection from '@/components/landing/GuaranteeSection.vue'
import ContactForm from '@/components/landing/ContactForm.vue'
import FullFooter from '@/components/navigation/FullFooter.vue'
import PrivacyPolicy from '@/components/legal/PrivacyPolicy.vue'
import TermsConditions from '@/components/legal/TermsConditions.vue'
import LegalNotice from '@/components/legal/LegalNotice.vue'

export default {
  name: 'InfoView',
  components: {
    FullNavbar,
    AboutSection,
    ServicesSection,
    GuaranteeSection,
    ContactForm,
    FullFooter,
    PrivacyPolicy,
    TermsConditions,
    LegalNotice
  },
  data() {
    return {
      currentLegalPage: null
    }
  },
  mounted() {
    const canonical = document.querySelector('link[rel="canonical"]')
    if (canonical) canonical.href = 'https://petrucalistenia.com/info'
    document.title = 'Servicios - PetruWorkout | Entrenador Personal'

    this.checkLegalParam()
  },
  watch: {
    '$route.query'() {
      this.checkLegalParam()
    }
  },
  computed: {
    currentLegalComponent() {
      const components = {
        'privacy': PrivacyPolicy,
        'terms': TermsConditions,
        'legal-notice': LegalNotice
      }
      return components[this.currentLegalPage]
    }
  },
  methods: {
    scrollToSection(sectionId) {
      const el = document.getElementById(sectionId)
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    },
    showLegalPage(pageType) {
      this.currentLegalPage = pageType
      window.scrollTo(0, 0)
    },
    closeLegalPage() {
      this.currentLegalPage = null
      this.$router.replace({ query: {} })
      window.scrollTo(0, 0)
    },
    checkLegalParam() {
      const legalParam = this.$route.query.legal
      if (legalParam && ['privacy', 'terms', 'legal-notice'].includes(legalParam)) {
        this.currentLegalPage = legalParam
        window.scrollTo(0, 0)
      }
    },
    goToGroup() {
      window.location.href = 'https://petrucalistenia.com/team'
    }
  }
}
</script>

<style scoped>
.info-view {
  width: 100%;
  min-height: 100vh;
  background: var(--bg-primary);
}

/* ===== SECCIÓN JOIN GROUP ===== */
.join-group-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 3rem 1rem;
  gap: 1.5rem;
}

.join-text {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.btn-join-group {
  background: var(--gradient-primary);
  color: white;
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);
}

.btn-join-group:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(6, 214, 160, 0.6);
}
</style>
