<template>
  <div class="calculator-view">
    <SimpleNavbar />
    <CalorieCalculator />
    <SimpleFooter @show-legal="showLegalPage" />

    <!-- Páginas legales -->
    <component
      v-if="currentLegalPage"
      :is="currentLegalComponent"
      @close="currentLegalPage = null"
    />
  </div>
</template>

<script>
import SimpleNavbar from '@/components/navigation/SimpleNavbar.vue'
import CalorieCalculator from '@/components/calculator/CalorieCalculator.vue'
import SimpleFooter from '@/components/navigation/SimpleFooter.vue'
import PrivacyPolicy from '@/components/legal/PrivacyPolicy.vue'
import TermsConditions from '@/components/legal/TermsConditions.vue'
import LegalNotice from '@/components/legal/LegalNotice.vue'

export default {
  name: 'CalculatorView',
  components: {
    SimpleNavbar,
    CalorieCalculator: CalorieCalculator,
    SimpleFooter,
    PrivacyPolicy,
    TermsConditions,
    LegalNotice
  },
  data() {
    return {
      currentLegalPage: null
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
    showLegalPage(pageType) {
      this.currentLegalPage = pageType
      window.scrollTo(0, 0)
    }
  },
  mounted() {
     const urlParams = new URLSearchParams(window.location.search)
  const token = urlParams.get('token')
  const savedToken = sessionStorage.getItem('petru_calculator_token')

  if (token) {
    sessionStorage.setItem('petru_calculator_token', token)
    window.history.replaceState({}, '', '/calculator')
  } else if (!savedToken) {
    this.$router.push('/')
    return
  }
    // SEO
    const canonical = document.querySelector('link[rel="canonical"]')
    if (canonical) canonical.href = 'https://petrucalistenia.com/calculator'
    document.title = 'Calculadora de Calorías - PetruWorkout'
  }
}
</script>

<style scoped>
.calculator-view {
  width: 100%;
  min-height: 100vh;
  background: var(--bg-primary);
}
</style>
