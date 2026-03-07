<template>
  <div class="admin-dashboard">

    <!-- CABECERA -->
    <div class="dashboard-header">
      <div class="header-left">
        <h2>📊 Dashboard Analytics</h2>
        <p>Métricas de rendimiento · Datos hasta ayer</p>
      </div>
      <div class="header-right">
        <span class="data-badge"><span class="dot"></span>Actualizado a d-1</span>
      </div>
    </div>

    <!-- FILTROS -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>Fuente de tráfico</label>
        <select v-model="filters.source" @change="fetchAll" class="filter-select">
          <option value="all">Todas las fuentes</option>
          <option value="instagram">📸 Instagram</option>
          <option value="organic_search">🔍 Organic Search</option>
          <option value="youtube">▶️ YouTube</option>
          <option value="facebook">👥 Facebook</option>
          <option value="linkedin">💼 LinkedIn</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Período</label>
        <div class="period-pills">
          <button v-for="p in periods" :key="p.value"
            @click="setPeriod(p.value)" class="period-pill"
            :class="{ active: filters.period === p.value }">{{ p.label }}</button>
        </div>
      </div>
      <div v-if="filters.period === 'custom'" class="filter-group">
        <label>Desde</label>
        <input type="date" v-model="filters.dateFrom" @change="fetchAll" class="filter-input" />
      </div>
      <div v-if="filters.period === 'custom'" class="filter-group">
        <label>Hasta</label>
        <input type="date" v-model="filters.dateTo" @change="fetchAll" class="filter-input" />
      </div>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div><p>Cargando métricas...</p>
    </div>

    <!-- ERROR -->
    <div v-else-if="error" class="error-state">
      <span>⚠️</span><p>{{ error }}</p>
      <button @click="fetchAll" class="btn-retry">Reintentar</button>
    </div>

    <template v-else>

      <!-- FILA 1 · KPIs -->
      <div class="row kpi-row">
        <div class="kpi-card">
          <span class="kpi-icon">👁️</span>
          <div class="kpi-body">
            <span class="kpi-label">Visitas totales</span>
            <span class="kpi-value">{{ fmt(totals.visits) }}</span>
            <span class="kpi-sub">en el período</span>
          </div>
        </div>
        <div class="kpi-card accent">
          <span class="kpi-icon">📅</span>
          <div class="kpi-body">
            <span class="kpi-label">Citas agendadas</span>
            <span class="kpi-value">{{ fmt(totals.bookings) }}</span>
            <span class="kpi-sub">confirmadas</span>
          </div>
        </div>
        <div class="kpi-card">
          <span class="kpi-icon">🎯</span>
          <div class="kpi-body">
            <span class="kpi-label">Tasa de conversión</span>
            <span class="kpi-value">{{ pct(conversionRate) }}</span>
            <span class="kpi-sub">visita → cita</span>
          </div>
        </div>
        <div class="kpi-card">
          <span class="kpi-icon">🖱️</span>
          <div class="kpi-body">
            <span class="kpi-label">Clicks Calendly</span>
            <span class="kpi-value">{{ fmt(totals.clicks) }}</span>
            <span class="kpi-sub">interacciones</span>
          </div>
        </div>
      </div>

      <!-- FILA 2 · EMBUDO + FUENTES -->
      <div class="row two-col">
        <div class="card">
          <div class="card-head">
            <h3>⬇️ Embudo de conversión</h3>
            <span class="tag">{{ sourceLabel }}</span>
          </div>
          <div class="funnel">
            <div v-for="(step, i) in funnelSteps" :key="i" class="funnel-step">
              <div class="funnel-top">
                <span class="funnel-name">{{ step.name }}</span>
                <span class="funnel-n">{{ fmt(step.count) }}</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: step.pct + '%', background: step.color }"></div>
              </div>
              <div class="funnel-bottom">
                <span class="funnel-pct">{{ step.pct.toFixed(1) }}% del total</span>
                <span v-if="i > 0" class="funnel-drop">↓ {{ (100 - step.pct).toFixed(1) }}% no continúan</span>
              </div>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-head">
            <h3>📡 Distribución por fuente</h3>
            <span class="tag">{{ periodLabel }}</span>
          </div>
          <div class="sources">
            <div v-for="src in trafficSources" :key="src.key" class="source-row">
              <div class="source-info"><span>{{ src.emoji }}</span><span class="source-name">{{ src.label }}</span></div>
              <div class="bar-track"><div class="bar-fill" :style="{ width: src.pct + '%', background: src.color }"></div></div>
              <div class="source-stats">
                <span class="source-pct">{{ src.pct.toFixed(1) }}%</span>
                <span class="source-n">{{ fmt(src.visits) }}</span>
              </div>
            </div>
            <div v-if="trafficSources.length === 0" class="empty-sources">Sin datos de fuentes</div>
          </div>
        </div>
      </div>

      <!-- FILA 2b · DISTRIBUCIÓN POR BOTÓN -->
      <div class="row">
        <div class="card">
          <div class="card-head">
            <h3>🖱️ Distribución de clicks por botón</h3>
            <span class="tag">{{ periodLabel }} · {{ sourceLabel }}</span>
          </div>
          <div class="btn-dist-grid">
            <div v-for="btn in buttonDistribution" :key="btn.key" class="btn-dist-row">
              <div class="source-info">
                <span>{{ btn.emoji }}</span>
                <span class="source-name">{{ btn.label }}</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: btn.pct + '%', background: btn.color }"></div>
              </div>
              <div class="source-stats">
                <span class="source-pct">{{ btn.pct.toFixed(1) }}%</span>
                <span class="source-n">{{ fmt(btn.clicks) }} clicks</span>
              </div>
            </div>
            <div v-if="buttonDistribution.length === 0" class="empty-sources">Sin datos de botones en este período</div>
          </div>
        </div>
      </div>

      <!-- FILA 3 · SIX SIGMA -->
      <div class="row sigma-row">
        <div class="card gauge-card">
          <div class="card-head">
            <h3>🏆 Nivel Sigma</h3>
            <span class="tag" :style="{ color: sigmaColor }">{{ sigmaLabel }}</span>
          </div>
          <div class="gauge-wrap">
            <svg viewBox="0 0 200 120" class="gauge-svg">
              <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="14" stroke-linecap="round"/>
              <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" :stroke="sigmaColor" stroke-width="14" stroke-linecap="round" :stroke-dasharray="sigmaArc + ' 251.2'" class="gauge-arc"/>
              <text x="100" y="88" text-anchor="middle" :fill="sigmaColor" font-size="30" font-weight="800">{{ sixSigma.sigma.toFixed(2) }}σ</text>
              <text x="100" y="108" text-anchor="middle" fill="rgba(255,255,255,0.4)" font-size="9">NIVEL SIGMA</text>
            </svg>
          </div>
          <div class="gauge-scale">
            <span v-for="n in [1,2,3,4,5,6]" :key="n">{{ n }}σ</span>
          </div>
        </div>
        <div class="card sigma-card">
          <div class="sigma-icon">💥</div>
          <div class="sigma-body">
            <span class="sigma-label">DPMO</span>
            <span class="sigma-value">{{ fmt(sixSigma.dpmo) }}</span>
            <span class="sigma-desc">Defectos por millón de oportunidades</span>
          </div>
          <span class="sigma-badge" :style="{ color: sigmaColor, background: sigmaColor + '18', borderColor: sigmaColor + '44' }">{{ dpmoLabel }}</span>
        </div>
        <div class="card sigma-card conversion-card">
          <div class="sigma-icon">🔄</div>
          <div class="sigma-body">
            <span class="sigma-label">RTY · Rendimiento acumulado</span>
            <span class="sigma-value">{{ pct(sixSigma.rty) }}</span>
            <span class="sigma-desc">% de visitas que llegan a cita</span>
          </div>
          <div class="rty-row">
            <div class="rty-step-box">
              <span class="rty-step-label">Click rate</span>
              <span class="rty-step-val">{{ (sixSigma.rty_y1 * 100).toFixed(1) }}%</span>
            </div>
            <span class="rty-op">×</span>
            <div class="rty-step-box">
              <span class="rty-step-label">Book rate</span>
              <span class="rty-step-val">{{ (sixSigma.rty_y2 * 100).toFixed(1) }}%</span>
            </div>
            <span class="rty-op">=</span>
            <span class="rty-result">{{ pct(sixSigma.rty) }}</span>
          </div>
          <div class="conv-divider"></div>
          <div class="ci-section">
            <span class="ci-title">📏 IC 95% Conversión</span>
            <span class="ci-range-label">[ {{ pct(sixSigma.ci_low) }} — {{ pct(sixSigma.ci_high) }} ]</span>
            <div class="ci-bar">
              <div class="ci-track">
                <div class="ci-range" :style="ciRangeStyle"></div>
                <div class="ci-dot"   :style="ciDotStyle"></div>
              </div>
              <div class="ci-labels">
                <span>{{ pct(sixSigma.ci_low) }}</span>
                <span>{{ pct(sixSigma.ci_high) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- FILA 3b · PROBABILIDADES POR FUENTE -->
      <div class="row">
        <div class="card prob-card">
          <div class="card-head">
            <h3>📊 Probabilidad de agendar por fuente</h3>
            <span class="tag">Conversión real con IC 95% · {{ periodLabel }}</span>
          </div>
          <div class="prob-grid">
            <div v-for="src in sourceProbabilities" :key="src.key" class="prob-item">
              <div class="prob-head">
                <span>{{ src.emoji }}</span>
                <span class="prob-name">{{ src.label }}</span>
                <span class="prob-ci">IC: [{{ pct(src.ci_low) }}, {{ pct(src.ci_high) }}]</span>
              </div>
              <div class="prob-bar-row">
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: Math.min(src.pct, 100) + '%', background: src.color }"></div>
                </div>
                <span class="prob-val" :style="{ color: src.color }">{{ src.pct.toFixed(2) }}%</span>
              </div>
              <span class="prob-meta">n={{ fmt(src.visits) }} visitas · {{ fmt(src.bookings) }} citas · σ={{ src.sigma.toFixed(2) }}</span>
            </div>
            <div v-if="sourceProbabilities.length === 0" class="empty-sources">Sin datos</div>
          </div>
        </div>
      </div>

      <!-- FILA 4 · TENDENCIA TEMPORAL -->
      <div class="row">
        <div class="card trend-card">
          <div class="card-head">
            <h3>📈 Tendencia temporal</h3>
            <span class="tag">{{ periodLabel }} · {{ sourceLabel }}</span>
          </div>
          <div v-if="trendLoading" class="trend-loading">
            <div class="spinner-sm"></div>
            <span>Generando gráfico...</span>
          </div>
          <div v-else-if="!trendData.length" class="trend-empty">
            <span>Sin datos para este período</span>
          </div>
          <div v-else ref="trendChart" class="chart-wrap"></div>
        </div>
      </div>

    </template>
  </div>
</template>

<script>
const SOURCE_CFG = {
  instagram:      { label: 'Instagram',      emoji: '📸', color: '#E1306C' },
  organic_search: { label: 'Organic Search', emoji: '🔍', color: '#4285F4' },
  youtube:        { label: 'YouTube',        emoji: '▶️', color: '#FF0000' },
  linkedin:       { label: 'LinkedIn',       emoji: '💼', color: '#0A66C2' },
  facebook:       { label: 'Facebook',       emoji: '👥', color: '#1877F2' },
}

const BUTTON_CFG = {
  'calculator-section': { label: 'Calculadora',     emoji: '🔢', color: '#9b5de5' },
  'results-section':    { label: 'Resultados',       emoji: '🏆', color: '#f15bb5' },
  'services-section':   { label: 'Servicios',        emoji: '💼', color: '#fee440' },
  'video-section':      { label: 'Vídeo',            emoji: '▶️', color: '#00bbf9' },
  'full-footer':        { label: 'Footer principal', emoji: '📋', color: '#00f5d4' },
  'full-navbar':        { label: 'Navbar',           emoji: '🔝', color: '#e63946' },
  'simple-footer':      { label: 'Footer simple',    emoji: '📄', color: '#4ecdc4' },
}

const SIGMA_COLORS = [
  { min: 5, color: '#06d6a0', label: 'Clase mundial' },
  { min: 4, color: '#4ecdc4', label: 'Excelente'     },
  { min: 3, color: '#ffd166', label: 'Competitivo'   },
  { min: 2, color: '#ff9a3c', label: 'Mejorable'     },
  { min: 0, color: '#e63946', label: 'Crítico'       },
]
const DPMO_LABELS = [
  { max: 233,      label: '★ Clase mundial' },
  { max: 6210,     label: '★ Excelente'     },
  { max: 66807,    label: '✓ Aceptable'     },
  { max: 308538,   label: '⚠ Mejorable'    },
  { max: Infinity, label: '✗ Crítico'      },
]
const BASE_URL = 'https://petruworkout-production.up.railway.app'

export default {
  name: 'AdminDashboard',

  data() {
    return {
      loading:      false,
      trendLoading: false,
      error:        null,

      filters: { source: 'all', period: '30', dateFrom: '', dateTo: '' },
      periods: [
        { value: '7',      label: '7d'     },
        { value: '30',     label: '30d'    },
        { value: '90',     label: '90d'    },
        { value: 'custom', label: 'Custom' },
      ],

      totals:     { visits: 0, clicks: 0, bookings: 0 },
      sixSigma:   { dpmo: 0, sigma: 1, rty: 0, rty_y1: 0, rty_y2: 0, ci_low: 0, ci_high: 0 },
      sourcesRaw: [],
      buttonsRaw: [],
      trendData:  [],
    }
  },

  computed: {
    conversionRate() {
      return this.totals.visits > 0 ? this.totals.bookings / this.totals.visits : 0
    },
    sourceLabel() {
      if (this.filters.source === 'all') return 'Todas las fuentes'
      return SOURCE_CFG[this.filters.source]?.label || this.filters.source
    },
    periodLabel() {
      if (this.filters.period === 'custom') return 'Período personalizado'
      const p = this.periods.find(x => x.value === this.filters.period)
      return p ? `Últimos ${p.label}` : ''
    },
    funnelSteps() {
      const { visits, clicks, bookings } = this.totals
      const base = visits || 1
      return [
        { name: '👁️ Visitas',         count: visits,   pct: 100,                color: '#06d6a0' },
        { name: '🖱️ Clicks Calendly', count: clicks,   pct: (clicks/base)*100,  color: '#e63946' },
        { name: '📅 Citas agendadas', count: bookings, pct: (bookings/base)*100, color: '#ffd166' },
      ]
    },
    trafficSources() {
      const total = this.sourcesRaw.reduce((s, x) => s + (x.visits||0), 0) || 1
      return this.sourcesRaw
        .filter(s => SOURCE_CFG[s.source])
        .map(s => ({
          key: s.source, label: SOURCE_CFG[s.source].label,
          emoji: SOURCE_CFG[s.source].emoji, color: SOURCE_CFG[s.source].color,
          visits: s.visits||0, pct: ((s.visits||0)/total)*100,
        }))
        .sort((a,b) => b.visits - a.visits)
    },
    buttonDistribution() {
      const total = this.buttonsRaw.reduce((s, x) => s + (x.clicks||0), 0) || 1
      return this.buttonsRaw
        .map(b => {
          const cfg = BUTTON_CFG[b.button] || { label: b.button, emoji: '🖱️', color: '#888' }
          return {
            key:    b.button,
            label:  cfg.label,
            emoji:  cfg.emoji,
            color:  cfg.color,
            clicks: b.clicks || 0,
            pct:    ((b.clicks || 0) / total) * 100,
          }
        })
        .sort((a, b) => b.clicks - a.clicks)
    },
    sourceProbabilities() {
      return this.sourcesRaw
        .filter(s => SOURCE_CFG[s.source])
        .map(s => ({
          key: s.source, label: SOURCE_CFG[s.source].label,
          emoji: SOURCE_CFG[s.source].emoji, color: SOURCE_CFG[s.source].color,
          visits: s.visits||0, clicks: s.clicks||0, bookings: s.bookings||0,
          pct: (s.conv_rate||0)*100,
          ci_low: s.ci_low||0, ci_high: s.ci_high||0, sigma: s.sigma||1,
        }))
        .sort((a,b) => b.pct - a.pct)
    },
    sigmaColor() {
      const s = this.sixSigma.sigma
      return SIGMA_COLORS.find(x => s >= x.min)?.color || '#e63946'
    },
    sigmaLabel() {
      const s = this.sixSigma.sigma
      return SIGMA_COLORS.find(x => s >= x.min)?.label || 'Crítico'
    },
    sigmaArc() {
      return Math.min(1, Math.max(0, (this.sixSigma.sigma-1)/5)) * 251.2
    },
    dpmoLabel() {
      const d = this.sixSigma.dpmo
      return DPMO_LABELS.find(x => d <= x.max)?.label || '✗ Crítico'
    },
    ciRangeStyle() {
      const max  = this.sixSigma.ci_high * 100 || 1
      const left = (this.sixSigma.ci_low * 100 / max) * 100
      return {
        position:'absolute', left:left.toFixed(1)+'%',
        width:(100-left).toFixed(1)+'%', top:0, height:'100%',
        background: this.sigmaColor+'30', borderRadius:'4px',
      }
    },
    ciDotStyle() {
      const max = this.sixSigma.ci_high * 100 || 1
      const pos = (this.conversionRate * 100 / max) * 100
      return {
        position:'absolute', left:Math.min(95,Math.max(5,pos)).toFixed(1)+'%',
        top:'50%', transform:'translate(-50%,-50%)',
        width:'12px', height:'12px',
        background: this.sigmaColor, borderRadius:'50%',
        border:'2px solid rgba(0,0,0,0.4)',
      }
    },
  },

  mounted() {
    this.loadPlotly().then(() => this.fetchAll())
  },

  methods: {
    fmt(n) {
      if (n == null || isNaN(n)) return '—'
      return new Intl.NumberFormat('es-ES').format(Math.round(n))
    },
    pct(v) {
      if (v == null || isNaN(v)) return '—'
      return (v > 1 ? v : v * 100).toFixed(2) + '%'
    },
    setPeriod(val) {
      this.filters.period = val
      if (val !== 'custom') this.fetchAll()
    },
    buildQS() {
      const p = new URLSearchParams()
      if (this.filters.source !== 'all') p.append('source', this.filters.source)
      if (this.filters.period !== 'custom') {
        p.append('days', this.filters.period)
      } else {
        if (this.filters.dateFrom) p.append('date_from', this.filters.dateFrom)
        if (this.filters.dateTo)   p.append('date_to',   this.filters.dateTo)
      }
      return p.toString()
    },

    loadPlotly() {
      if (window.Plotly) return Promise.resolve()
      return new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://cdn.plot.ly/plotly-2.32.0.min.js'
        script.onload  = resolve
        script.onerror = reject
        document.head.appendChild(script)
      })
    },

    async fetchAll() {
      this.loading      = true
      this.trendLoading = true
      this.error        = null
      try {
        const token   = localStorage.getItem('admin_token')
        const headers = { token }
        const qs      = this.buildQS()

        const res = await fetch(`${BASE_URL}/api/admin/analytics?${qs}`, { headers })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const a = await res.json()

        this.totals = {
          visits:   a.totals?.visits   ?? 0,
          clicks:   a.totals?.clicks   ?? 0,
          bookings: a.totals?.bookings ?? 0,
        }
        this.sixSigma = {
          dpmo:    a.six_sigma?.dpmo    ?? 0,
          sigma:   a.six_sigma?.sigma   ?? 1,
          rty:     a.six_sigma?.rty     ?? 0,
          rty_y1:  a.six_sigma?.rty_y1  ?? 0,
          rty_y2:  a.six_sigma?.rty_y2  ?? 0,
          ci_low:  a.six_sigma?.ci_low  ?? 0,
          ci_high: a.six_sigma?.ci_high ?? 0,
        }
        this.sourcesRaw = a.sources ?? []
        this.buttonsRaw = a.buttons ?? []
        this.trendData  = a.trend   ?? []

        this.$nextTick(() => {
          this.trendLoading = false
          this.$nextTick(() => this.renderChart())
        })

      } catch (err) {
        console.error('Dashboard error:', err)
        this.error        = 'Error al cargar los datos. Comprueba la conexión.'
        this.trendLoading = false
      } finally {
        this.loading = false
      }
    },

    renderChart() {
      const container = this.$refs.trendChart
      if (!container) return
      if (!window.Plotly) { console.warn('Plotly no está cargado'); return }
      if (!this.trendData.length) return

      const dates    = this.trendData.map(d => d.date)
      const visits   = this.trendData.map(d => d.visits)
      const clicks   = this.trendData.map(d => d.clicks)
      const bookings = this.trendData.map(d => d.bookings)

      const traces = [
        {
          x: dates, y: visits, name: 'Visitas',
          mode: 'lines+markers', type: 'scatter',
          line:   { color: '#06d6a0', width: 2 },
          marker: { color: '#06d6a0', size: 5 },
          fill: 'tozeroy', fillcolor: 'rgba(6,214,160,0.07)',
          hovertemplate: '<b>%{x}</b><br>Visitas: %{y}<extra></extra>',
        },
        {
          x: dates, y: clicks, name: 'Clicks Calendly',
          mode: 'lines+markers', type: 'scatter',
          line:   { color: '#e63946', width: 2 },
          marker: { color: '#e63946', size: 5 },
          fill: 'tozeroy', fillcolor: 'rgba(230,57,70,0.07)',
          hovertemplate: '<b>%{x}</b><br>Clicks: %{y}<extra></extra>',
        },
        {
          x: dates, y: bookings, name: 'Citas agendadas',
          mode: 'lines+markers', type: 'scatter',
          line:   { color: '#ffd166', width: 2 },
          marker: { color: '#ffd166', size: 5 },
          fill: 'tozeroy', fillcolor: 'rgba(255,209,102,0.07)',
          hovertemplate: '<b>%{x}</b><br>Citas: %{y}<extra></extra>',
        },
      ]

      const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor:  'rgba(0,0,0,0)',
        margin: { l: 40, r: 20, t: 10, b: 40 },
        height: 260,
        legend: {
          orientation: 'h', yanchor: 'bottom', y: 1.02,
          xanchor: 'right', x: 1,
          font: { color: 'rgba(255,255,255,0.55)', size: 12 },
          bgcolor: 'rgba(0,0,0,0)',
        },
        xaxis: {
          gridcolor: 'rgba(255,255,255,0.04)',
          tickfont:  { color: 'rgba(255,255,255,0.45)', size: 11 },
          linecolor: 'rgba(255,255,255,0.1)',
        },
        yaxis: {
          gridcolor: 'rgba(255,255,255,0.04)',
          tickfont:  { color: 'rgba(255,255,255,0.45)', size: 11 },
          rangemode: 'tozero',
        },
        hovermode: 'x unified',
        hoverlabel: {
          bgcolor:     'rgba(10,10,10,0.9)',
          font:        { color: 'white', size: 12 },
          bordercolor: 'rgba(255,255,255,0.1)',
        },
      }

      window.Plotly.newPlot(container, traces, layout, {
        displayModeBar: false,
        responsive:     true,
      })
    },
  },
}
</script>

<style scoped>
.admin-dashboard { max-width: 1400px; margin: 0 auto; }

.dashboard-header {
  display: flex; justify-content: space-between; align-items: flex-end;
  margin-bottom: 1.5rem;
}
.dashboard-header h2 { font-size: 1.75rem; color: white; margin: 0 0 .25rem; }
.dashboard-header p  { color: var(--color-text-muted); font-size: .9rem; margin: 0; }
.data-badge {
  display: flex; align-items: center; gap: .5rem;
  background: rgba(6,214,160,.1); border: 1px solid rgba(6,214,160,.3);
  color: var(--color-accent); padding: .35rem .875rem;
  border-radius: 20px; font-size: .78rem; font-weight: 600;
}
.dot {
  width: 7px; height: 7px; background: var(--color-accent);
  border-radius: 50%; animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* Filtros */
.filters-bar {
  display: flex; flex-wrap: wrap; gap: 1.5rem; align-items: flex-end;
  background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.09);
  border-radius: 14px; padding: 1rem 1.5rem; margin-bottom: 1.5rem;
}
.filter-group { display: flex; flex-direction: column; gap: .35rem; }
.filter-group label {
  font-size: .72rem; font-weight: 600; color: rgba(255,255,255,.45);
  text-transform: uppercase; letter-spacing: .07em;
}
.filter-select, .filter-input {
  background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14);
  border-radius: 8px; color: white; padding: .5rem .875rem;
  font-size: .875rem; cursor: pointer; transition: border-color .2s;
}
.filter-select:focus,.filter-input:focus { outline: none; border-color: var(--color-accent); }
.filter-select option { background: #1a1a1a; }
.period-pills { display: flex; gap: .35rem; }
.period-pill {
  background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.13);
  border-radius: 8px; color: rgba(255,255,255,.55);
  padding: .45rem .875rem; font-size: .82rem; font-weight: 600;
  cursor: pointer; transition: all .2s;
}
.period-pill:hover { background: rgba(255,255,255,.12); color: white; }
.period-pill.active { background: rgba(6,214,160,.18); border-color: var(--color-accent); color: var(--color-accent); }

/* Loading / Error */
.loading-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 1rem; padding: 5rem 2rem; color: rgba(255,255,255,.5);
}
.spinner {
  width: 40px; height: 40px; border: 3px solid rgba(255,255,255,.1);
  border-left-color: var(--color-accent); border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.error-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 1rem; padding: 4rem 2rem; text-align: center;
  color: rgba(255,255,255,.55); font-size: 1.5rem;
}
.error-state p { font-size: 1rem; }
.btn-retry {
  background: rgba(6,214,160,.13); border: 1px solid var(--color-accent);
  color: var(--color-accent); padding: .6rem 1.5rem; border-radius: 8px;
  cursor: pointer; font-weight: 600;
}

/* Grid */
.row { display: flex; gap: 1.25rem; width: 100%; margin-bottom: 1.25rem; }
.kpi-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 1.25rem; margin-bottom: 0; }
.kpi-card {
  background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.09);
  border-radius: 16px; padding: 1.25rem 1.5rem;
  display: flex; align-items: center; gap: 1rem;
  transition: border-color .2s, transform .2s;
}
.kpi-card:hover { border-color: rgba(255,255,255,.18); transform: translateY(-2px); }
.kpi-card.accent { background: linear-gradient(135deg,rgba(6,214,160,.12),rgba(6,214,160,.04)); border-color: rgba(6,214,160,.35); }
.kpi-icon { font-size: 2rem; flex-shrink: 0; }
.kpi-body { display: flex; flex-direction: column; gap: .18rem; }
.kpi-label { font-size: .75rem; color: rgba(255,255,255,.45); text-transform: uppercase; letter-spacing: .06em; }
.kpi-value { font-size: 1.75rem; font-weight: 800; color: white; line-height: 1; }
.kpi-sub   { font-size: .73rem; color: rgba(255,255,255,.3); }

.card {
  background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.09);
  border-radius: 16px; padding: 1.5rem; flex: 1;
}
.card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }
.card-head h3 { font-size: .975rem; color: white; margin: 0; font-weight: 700; }
.tag {
  font-size: .72rem; color: rgba(255,255,255,.4); background: rgba(255,255,255,.06);
  padding: .18rem .6rem; border-radius: 20px; white-space: nowrap;
}

.two-col > .card:first-child { flex: 1.1; }
.two-col > .card:last-child  { flex: 0.9; }

/* Funnel */
.funnel { display: flex; flex-direction: column; gap: 1.1rem; }
.funnel-step { display: flex; flex-direction: column; gap: .3rem; }
.funnel-top,.funnel-bottom { display: flex; justify-content: space-between; align-items: center; }
.funnel-name { font-size: .875rem; color: rgba(255,255,255,.78); font-weight: 500; }
.funnel-n    { font-size: .875rem; color: white; font-weight: 700; }
.funnel-pct  { font-size: .775rem; color: rgba(255,255,255,.45); }
.funnel-drop { font-size: .75rem; color: rgba(239,68,68,.65); }

.bar-track { height: 9px; background: rgba(255,255,255,.06); border-radius: 5px; overflow: hidden; flex: 1; }
.bar-fill  { height: 100%; border-radius: 5px; transition: width .8s ease; }

/* Sources */
.sources { display: flex; flex-direction: column; gap: .875rem; }
.source-row { display: grid; grid-template-columns: 140px 1fr auto; align-items: center; gap: .75rem; }
.source-info { display: flex; align-items: center; gap: .5rem; }
.source-name { font-size: .83rem; color: rgba(255,255,255,.72); white-space: nowrap; }
.source-stats { display: flex; flex-direction: column; align-items: flex-end; }
.source-pct { font-size: .83rem; color: white; font-weight: 700; }
.source-n   { font-size: .72rem; color: rgba(255,255,255,.38); }
.empty-sources { font-size: .85rem; color: rgba(255,255,255,.35); text-align: center; padding: 1rem 0; }

/* Distribución por botón — 2 columnas para aprovechar el ancho */
.btn-dist-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: .75rem 3rem;
}
.btn-dist-row {
  display: grid; grid-template-columns: 150px 1fr auto;
  align-items: center; gap: .75rem;
}

/* Sigma */
.sigma-row { display: grid; grid-template-columns: 210px 1fr 1.4fr; gap: 1.25rem; margin-bottom: 0; }
.gauge-card { display: flex; flex-direction: column; }
.gauge-wrap { display: flex; justify-content: center; }
.gauge-svg  { width: 160px; height: 96px; }
.gauge-arc  { transition: stroke-dasharray 1s ease; }
.gauge-scale { display: flex; justify-content: space-between; padding: 0 .5rem; font-size: .68rem; color: rgba(255,255,255,.28); margin-top: .25rem; }
.sigma-card { display: flex; flex-direction: column; gap: .75rem; justify-content: space-between; }
.sigma-icon  { font-size: 1.5rem; }
.sigma-body  { display: flex; flex-direction: column; gap: .2rem; flex: 1; }
.sigma-label { font-size: .72rem; color: rgba(255,255,255,.42); text-transform: uppercase; letter-spacing: .06em; }
.sigma-value { font-size: 1.75rem; font-weight: 800; color: white; line-height: 1.1; }
.sigma-desc  { font-size: .75rem; color: rgba(255,255,255,.38); }
.sigma-badge { display: inline-flex; align-self: flex-start; padding: .22rem .7rem; border-radius: 20px; border: 1px solid; font-size: .75rem; font-weight: 600; }

/* RTY + IC */
.conversion-card { gap: .6rem; }
.rty-row { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; }
.rty-step-box { display: flex; flex-direction: column; align-items: center; gap: .08rem; }
.rty-step-label { font-size: .64rem; color: rgba(255,255,255,.35); }
.rty-step-val   { font-size: .875rem; color: rgba(255,255,255,.65); font-weight: 600; }
.rty-op     { font-size: .75rem; color: rgba(255,255,255,.25); }
.rty-result { font-size: 1rem; font-weight: 700; color: var(--color-accent); }
.conv-divider { height: 1px; background: rgba(255,255,255,.07); margin: .25rem 0; }
.ci-section { display: flex; flex-direction: column; gap: .35rem; }
.ci-title       { font-size: .72rem; color: rgba(255,255,255,.42); text-transform: uppercase; letter-spacing: .06em; }
.ci-range-label { font-size: .78rem; color: rgba(255,255,255,.55); font-weight: 600; }
.ci-bar { margin-top: .2rem; }
.ci-track { position: relative; height: 9px; background: rgba(255,255,255,.06); border-radius: 5px; overflow: visible; margin-bottom: .4rem; }
.ci-labels { display: flex; justify-content: space-between; font-size: .68rem; color: rgba(255,255,255,.35); }

/* Probabilidades */
.prob-card { flex: 1; }
.prob-grid { display: grid; grid-template-columns: repeat(2,1fr); gap: 1.1rem; }
.prob-item { background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.07); border-radius: 12px; padding: 1rem; display: flex; flex-direction: column; gap: .55rem; }
.prob-head { display: flex; align-items: center; gap: .45rem; }
.prob-name { font-size: .875rem; font-weight: 600; color: white; flex: 1; }
.prob-ci   { font-size: .68rem; color: rgba(255,255,255,.32); }
.prob-bar-row { display: flex; align-items: center; gap: .75rem; }
.prob-val { font-size: .95rem; font-weight: 700; min-width: 50px; text-align: right; }
.prob-meta { font-size: .7rem; color: rgba(255,255,255,.3); }

/* Tendencia */
.trend-card { flex: 1; }
.trend-loading {
  display: flex; align-items: center; gap: .75rem;
  padding: 2rem; color: rgba(255,255,255,.4); font-size: .875rem;
}
.trend-empty {
  display: flex; align-items: center; justify-content: center;
  padding: 3rem; color: rgba(255,255,255,.3); font-size: .875rem;
}
.spinner-sm {
  width: 20px; height: 20px; border: 2px solid rgba(255,255,255,.1);
  border-left-color: var(--color-accent); border-radius: 50%;
  animation: spin .8s linear infinite; flex-shrink: 0;
}
.chart-wrap { width: 100%; min-height: 280px; }

/* Responsive */
@media (max-width: 1200px) {
  .sigma-row { grid-template-columns: repeat(2,1fr); }
  .btn-dist-grid { grid-template-columns: 1fr; }
}
@media (max-width: 968px) {
  .kpi-row  { grid-template-columns: repeat(2,1fr); }
  .two-col  { flex-direction: column; }
  .sigma-row { grid-template-columns: 1fr; }
  .prob-grid { grid-template-columns: 1fr; }
  .btn-dist-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .kpi-row { grid-template-columns: 1fr; }
  .filters-bar { gap: 1rem; padding: 1rem; }
  .dashboard-header { flex-direction: column; align-items: flex-start; gap: .5rem; }
  .source-row { grid-template-columns: 100px 1fr auto; }
  .btn-dist-row { grid-template-columns: 110px 1fr auto; }
}
</style>
