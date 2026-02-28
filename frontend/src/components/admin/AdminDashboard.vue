<template>
  <div class="admin-dashboard">

    <!-- CABECERA -->
    <div class="dashboard-header">
      <div class="header-left">
        <h2>📊 Dashboard Analytics</h2>
        <p>Métricas de rendimiento · Datos hasta ayer</p>
      </div>
      <div class="header-right">
        <span class="data-badge">
          <span class="dot"></span>
          Actualizado a d-1
        </span>
      </div>
    </div>

    <!-- FILTROS GLOBALES -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>Fuente de tráfico</label>
        <select v-model="filters.source" @change="fetchAll" class="filter-select">
          <option value="all">Todas las fuentes</option>
          <option value="instagram">📸 Instagram</option>
          <option value="organic_search">🔍 Organic Search</option>
          <option value="whatsapp">💬 WhatsApp</option>
          <option value="facebook">👥 Facebook</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Período</label>
        <div class="period-pills">
          <button
            v-for="p in periods" :key="p.value"
            @click="setPeriod(p.value)"
            class="period-pill"
            :class="{ active: filters.period === p.value }"
          >{{ p.label }}</button>
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
      <div class="spinner"></div>
      <p>Cargando métricas...</p>
    </div>

    <!-- ERROR -->
    <div v-else-if="error" class="error-state">
      <span>⚠️</span>
      <p>{{ error }}</p>
      <button @click="fetchAll" class="btn-retry">Reintentar</button>
    </div>

    <!-- DASHBOARD -->
    <template v-else>

      <!-- ══════════════════════════════════════
           FILA 1 · KPI CARDS
      ══════════════════════════════════════ -->
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

      <!-- ══════════════════════════════════════
           FILA 2 · EMBUDO + FUENTES
      ══════════════════════════════════════ -->
      <div class="row two-col">

        <!-- Embudo -->
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
                <span v-if="i > 0" class="funnel-drop">
                  ↓ {{ (100 - step.pct).toFixed(1) }}% no continúan
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Fuentes -->
        <div class="card">
          <div class="card-head">
            <h3>📡 Distribución por fuente</h3>
            <span class="tag">{{ periodLabel }}</span>
          </div>
          <div class="sources">
            <div v-for="src in trafficSources" :key="src.key" class="source-row">
              <div class="source-info">
                <span>{{ src.emoji }}</span>
                <span class="source-name">{{ src.label }}</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: src.pct + '%', background: src.color }"></div>
              </div>
              <div class="source-stats">
                <span class="source-pct">{{ src.pct.toFixed(1) }}%</span>
                <span class="source-n">{{ fmt(src.visits) }}</span>
              </div>
            </div>
            <div v-if="trafficSources.length === 0" class="empty-sources">
              Sin datos de fuentes para el período seleccionado
            </div>
          </div>
        </div>

      </div>

      <!-- ══════════════════════════════════════
           FILA 3 · SIX SIGMA
      ══════════════════════════════════════ -->
      <div class="row sigma-row">

        <!-- Gauge Sigma -->
        <div class="card gauge-card">
          <div class="card-head">
            <h3>🏆 Nivel Sigma</h3>
            <span class="tag" :style="{ color: sigmaColor }">{{ sigmaLabel }}</span>
          </div>
          <div class="gauge-wrap">
            <svg viewBox="0 0 200 120" class="gauge-svg">
              <path d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="14" stroke-linecap="round"/>
              <path d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none" :stroke="sigmaColor" stroke-width="14" stroke-linecap="round"
                :stroke-dasharray="sigmaArc + ' 251.2'" class="gauge-arc"/>
              <text x="100" y="88" text-anchor="middle" :fill="sigmaColor"
                font-size="30" font-weight="800">{{ sixSigma.sigma.toFixed(2) }}σ</text>
              <text x="100" y="108" text-anchor="middle"
                fill="rgba(255,255,255,0.4)" font-size="9">NIVEL SIGMA</text>
            </svg>
          </div>
          <div class="gauge-scale">
            <span v-for="n in [1,2,3,4,5,6]" :key="n">{{ n }}σ</span>
          </div>
        </div>

        <!-- DPMO -->
        <div class="card sigma-card">
          <div class="sigma-icon">💥</div>
          <div class="sigma-body">
            <span class="sigma-label">DPMO</span>
            <span class="sigma-value">{{ fmt(sixSigma.dpmo) }}</span>
            <span class="sigma-desc">Defectos por millón de oportunidades</span>
          </div>
          <span class="sigma-badge"
            :style="{ color: sigmaColor, background: sigmaColor + '18', borderColor: sigmaColor + '44' }">
            {{ dpmoLabel }}
          </span>
        </div>

        <!-- RTY -->
        <div class="card sigma-card">
          <div class="sigma-icon">🔄</div>
          <div class="sigma-body">
            <span class="sigma-label">RTY · Rendimiento acumulado</span>
            <span class="sigma-value">{{ pct(sixSigma.rty) }}</span>
            <span class="sigma-desc">% de visitas que llegan a cita</span>
          </div>
          <div class="rty-row">
            <span class="rty-step">{{ (sixSigma.rty_y1 * 100).toFixed(1) }}%</span>
            <span class="rty-op">×</span>
            <span class="rty-step">{{ (sixSigma.rty_y2 * 100).toFixed(1) }}%</span>
            <span class="rty-op">=</span>
            <span class="rty-result">{{ pct(sixSigma.rty) }}</span>
          </div>
        </div>

        <!-- IC 95% -->
        <div class="card sigma-card">
          <div class="sigma-icon">📏</div>
          <div class="sigma-body">
            <span class="sigma-label">IC 95% Conversión</span>
            <span class="sigma-value">{{ pct(conversionRate) }}</span>
            <span class="sigma-desc">
              [ {{ pct(sixSigma.ci_low) }} — {{ pct(sixSigma.ci_high) }} ]
            </span>
          </div>
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

      <!-- ══════════════════════════════════════
           FILA 3b · PROBABILIDAD POR FUENTE
      ══════════════════════════════════════ -->
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
              <span class="prob-meta">
                n={{ fmt(src.visits) }} visitas · {{ fmt(src.bookings) }} citas
                · σ={{ src.sigma.toFixed(2) }}
              </span>
            </div>
            <div v-if="sourceProbabilities.length === 0" class="empty-sources">
              Sin datos para el período seleccionado
            </div>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════
           FILA 4 · TENDENCIA TEMPORAL
      ══════════════════════════════════════ -->
      <div class="row">
        <div class="card trend-card">
          <div class="card-head">
            <h3>📈 Tendencia temporal</h3>
            <span class="tag">Visitas · Clicks · Citas · Semana a semana</span>
          </div>
          <div class="chart-wrap">
            <canvas ref="trendCanvas"></canvas>
          </div>
          <div class="legend">
            <span class="leg-item"><span class="leg-dot" style="background:#06d6a0"></span>Visitas</span>
            <span class="leg-item"><span class="leg-dot" style="background:#e63946"></span>Clicks Calendly</span>
            <span class="leg-item"><span class="leg-dot" style="background:#ffd166"></span>Citas agendadas</span>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script>
const SOURCE_CFG = {
  instagram:      { label: 'Instagram',      emoji: '📸', color: '#E1306C' },
  organic_search: { label: 'Organic Search', emoji: '🔍', color: '#4285F4' },
  whatsapp:       { label: 'WhatsApp',       emoji: '💬', color: '#25D366' },
  facebook:       { label: 'Facebook',       emoji: '👥', color: '#1877F2' },
}

const SIGMA_COLORS = [
  { min: 5,   color: '#06d6a0', label: 'Clase mundial' },
  { min: 4,   color: '#4ecdc4', label: 'Excelente'     },
  { min: 3,   color: '#ffd166', label: 'Competitivo'   },
  { min: 2,   color: '#ff9a3c', label: 'Mejorable'     },
  { min: 0,   color: '#e63946', label: 'Crítico'       },
]

const DPMO_LABELS = [
  { max: 233,    label: '★ Clase mundial' },
  { max: 6210,   label: '★ Excelente'     },
  { max: 66807,  label: '✓ Aceptable'     },
  { max: 308538, label: '⚠ Mejorable'    },
  { max: Infinity, label: '✗ Crítico'    },
]

export default {
  name: 'AdminDashboard',

  data() {
    return {
      loading: false,
      error:   null,
      chart:   null,

      filters: {
        source:   'all',
        period:   '30',
        dateFrom: '',
        dateTo:   '',
      },

      periods: [
        { value: '7',      label: '7d'     },
        { value: '30',     label: '30d'    },
        { value: '90',     label: '90d'    },
        { value: 'custom', label: 'Custom' },
      ],

      // Datos crudos del backend
      totals:    { visits: 0, clicks: 0, bookings: 0 },
      sixSigma:  { dpmo: 0, sigma: 1, rty: 0, rty_y1: 0, rty_y2: 0, ci_low: 0, ci_high: 0 },
      sourcesRaw: [],
      trendRaw:   [],
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
        { name: '👁️ Visitas',         count: visits,   pct: 100,                          color: '#06d6a0' },
        { name: '🖱️ Clicks Calendly', count: clicks,   pct: (clicks / base) * 100,        color: '#e63946' },
        { name: '📅 Citas agendadas', count: bookings, pct: (bookings / base) * 100,       color: '#ffd166' },
      ]
    },

    trafficSources() {
      const total = this.sourcesRaw.reduce((s, x) => s + (x.visits || 0), 0) || 1
      return this.sourcesRaw
        .filter(s => SOURCE_CFG[s.source])
        .map(s => ({
          key:     s.source,
          label:   SOURCE_CFG[s.source].label,
          emoji:   SOURCE_CFG[s.source].emoji,
          color:   SOURCE_CFG[s.source].color,
          visits:  s.visits || 0,
          pct:     ((s.visits || 0) / total) * 100,
        }))
        .sort((a, b) => b.visits - a.visits)
    },

    sourceProbabilities() {
      return this.sourcesRaw
        .filter(s => SOURCE_CFG[s.source])
        .map(s => ({
          key:      s.source,
          label:    SOURCE_CFG[s.source].label,
          emoji:    SOURCE_CFG[s.source].emoji,
          color:    SOURCE_CFG[s.source].color,
          visits:   s.visits   || 0,
          clicks:   s.clicks   || 0,
          bookings: s.bookings || 0,
          pct:      (s.conv_rate || 0) * 100,
          ci_low:   s.ci_low   || 0,
          ci_high:  s.ci_high  || 0,
          sigma:    s.sigma    || 1,
        }))
        .sort((a, b) => b.pct - a.pct)
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
      const pct = Math.min(1, Math.max(0, (this.sixSigma.sigma - 1) / 5))
      return pct * 251.2
    },

    dpmoLabel() {
      const d = this.sixSigma.dpmo
      return DPMO_LABELS.find(x => d <= x.max)?.label || '✗ Crítico'
    },

    ciRangeStyle() {
      const max  = this.sixSigma.ci_high * 100 || 1
      const left  = (this.sixSigma.ci_low  * 100 / max) * 100
      const right = 100
      return {
        position: 'absolute',
        left: left.toFixed(1) + '%',
        width: (100 - left).toFixed(1) + '%',
        top: 0, height: '100%',
        background: this.sigmaColor + '30',
        borderRadius: '4px',
      }
    },

    ciDotStyle() {
      const max  = this.sixSigma.ci_high * 100 || 1
      const pos  = (this.conversionRate  * 100 / max) * 100
      return {
        position: 'absolute',
        left: Math.min(95, Math.max(5, pos)).toFixed(1) + '%',
        top: '50%',
        transform: 'translate(-50%, -50%)',
        width: '12px', height: '12px',
        background: this.sigmaColor,
        borderRadius: '50%',
        border: '2px solid rgba(0,0,0,0.4)',
      }
    },
  },

  mounted() {
    this.loadChartJS().then(() => this.fetchAll())
  },

  beforeUnmount() {
    if (this.chart) this.chart.destroy()
  },

  methods: {
    // ── Utilidades ──────────────────────────────────────────────────────────
    fmt(n) {
      if (n == null || isNaN(n)) return '—'
      return new Intl.NumberFormat('es-ES').format(Math.round(n))
    },

    pct(v) {
      if (v == null || isNaN(v)) return '—'
      const p = v > 1 ? v : v * 100
      return p.toFixed(2) + '%'
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

    loadChartJS() {
      return new Promise(resolve => {
        if (window.Chart) { resolve(); return }
        const s = document.createElement('script')
        s.src    = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js'
        s.onload = resolve
        s.onerror = resolve
        document.head.appendChild(s)
      })
    },

    // ── Fetch principal ────────────────────────────────────────────────────
    async fetchAll() {
      this.loading = true
      this.error   = null

      try {
        const token   = localStorage.getItem('admin_token')
        const headers = { token }
        const base    = 'https://petruworkout-production.up.railway.app'
        const qs      = this.buildQS()

        // Llamada principal: analytics (devuelve todo en uno)
        const analyticsRes = await fetch(`${base}/api/admin/analytics?${qs}`, { headers })

        if (analyticsRes.ok) {
          const a = await analyticsRes.json()

          // Totales
          this.totals = {
            visits:   a.totals?.visits   ?? 0,
            clicks:   a.totals?.clicks   ?? 0,
            bookings: a.totals?.bookings ?? 0,
          }

          // Six Sigma
          this.sixSigma = {
            dpmo:   a.six_sigma?.dpmo   ?? 0,
            sigma:  a.six_sigma?.sigma  ?? 1,
            rty:    a.six_sigma?.rty    ?? 0,
            rty_y1: a.six_sigma?.rty_y1 ?? 0,
            rty_y2: a.six_sigma?.rty_y2 ?? 0,
            ci_low:  a.six_sigma?.ci_low  ?? 0,
            ci_high: a.six_sigma?.ci_high ?? 0,
          }

          // Fuentes
          this.sourcesRaw = (a.sources ?? []).filter(
            s => s.source !== 'direct' && s.source !== 'internal'
          )

          // Tendencia
          this.trendRaw = a.trend ?? []

        } else {
          // Fallback: llamar a los endpoints legacy
          await this.fetchLegacy(base, headers, qs)
        }

        this.$nextTick(() => this.renderChart())

      } catch (err) {
        console.error('Dashboard error:', err)
        this.error = 'Error al cargar los datos. Comprueba la conexión.'
      } finally {
        this.loading = false
      }
    },

    // Fallback a endpoints legacy (mientras no exista /api/admin/analytics)
    async fetchLegacy(base, headers, qs) {
      const [dashRes, funnelRes, statsRes] = await Promise.allSettled([
        fetch(`${base}/api/admin/dashboard?${qs}`,  { headers }),
        fetch(`${base}/api/tracking/funnel?${qs}`,  { headers }),
        fetch(`${base}/api/tracking/stats?${qs}`,   { headers }),
      ])

      if (dashRes.status === 'fulfilled' && dashRes.value.ok) {
        const d = await dashRes.value.json()
        this.totals.visits   = d.total_visits   ?? d.visits   ?? 0
        this.totals.clicks   = d.total_clicks   ?? d.clicks   ?? 0
        this.totals.bookings = d.total_bookings ?? d.bookings ?? 0
      }

      if (funnelRes.status === 'fulfilled' && funnelRes.value.ok) {
        const f = await funnelRes.value.json()
        this.totals.visits   = f.visits   ?? this.totals.visits
        this.totals.clicks   = f.clicks   ?? this.totals.clicks
        this.totals.bookings = f.bookings ?? this.totals.bookings
      }

      if (statsRes.status === 'fulfilled' && statsRes.value.ok) {
        const s = await statsRes.value.json()
        const arr = Array.isArray(s) ? s : (s.sources ?? s.data ?? [])
        this.sourcesRaw = arr.filter(x =>
          x.source !== 'direct' && x.source !== 'internal'
        )
      }

      // Calcular Six Sigma localmente con los datos disponibles
      const v = this.totals.visits   || 1
      const c = this.totals.clicks   || 0
      const b = this.totals.bookings || 0
      const dpmo = Math.round((1 - b / v) * 1_000_000)
      const sigma = this.dpmoToSigma(dpmo)
      const y1   = c / v
      const y2   = b / Math.max(c, 1)
      const p    = b / v
      const z    = 1.96
      const m    = Math.sqrt((p * (1 - p)) / v) * z
      this.sixSigma = {
        dpmo,  sigma,
        rty: y1 * y2, rty_y1: y1, rty_y2: y2,
        ci_low:  Math.max(0, p - m),
        ci_high: Math.min(1, p + m),
      }
      this.trendRaw = []
    },

    dpmoToSigma(dpmo) {
      const table = [
        [691462, 1.0], [308538, 2.0], [66807, 3.0],
        [6210,   4.0], [233,    5.0], [3.4,   6.0],
      ]
      if (dpmo >= 691462) return 1.0
      if (dpmo <= 3.4)    return 6.0
      for (let i = 0; i < table.length - 1; i++) {
        const [hi, slo] = table[i]
        const [lo, shi] = table[i + 1]
        if (dpmo <= hi && dpmo >= lo) {
          const t = (dpmo - hi) / (lo - hi)
          return parseFloat((slo + t * (shi - slo)).toFixed(3))
        }
      }
      return 1.0
    },

    // ── Gráfico de tendencia ───────────────────────────────────────────────
    renderChart() {
      if (!window.Chart || !this.$refs.trendCanvas) return
      if (this.chart) { this.chart.destroy(); this.chart = null }

      let labels, visits, clicks, bookings

      if (this.trendRaw.length > 0) {
        // Agrupar por semana si hay muchos días
        const raw = this.trendRaw
        if (raw.length <= 14) {
          labels   = raw.map(d => d.date)
          visits   = raw.map(d => d.visits)
          clicks   = raw.map(d => d.clicks)
          bookings = raw.map(d => d.bookings)
        } else {
          // Agrupar en semanas
          const weeks = {}
          raw.forEach(d => {
            const dt  = new Date(d.date)
            const mon = new Date(dt.setDate(dt.getDate() - dt.getDay() + 1))
            const key = mon.toISOString().slice(0, 10)
            if (!weeks[key]) weeks[key] = { v: 0, c: 0, b: 0 }
            weeks[key].v += d.visits
            weeks[key].c += d.clicks
            weeks[key].b += d.bookings
          })
          labels   = Object.keys(weeks).map(k => 'Sem ' + k.slice(5))
          visits   = Object.values(weeks).map(w => w.v)
          clicks   = Object.values(weeks).map(w => w.c)
          bookings = Object.values(weeks).map(w => w.b)
        }
      } else {
        // Placeholder distribuido
        const n = Math.min(Math.ceil((parseInt(this.filters.period) || 30) / 7), 12)
        labels   = Array.from({ length: n }, (_, i) => `Sem ${i + 1}`)
        const rand = (base, noise) =>
          labels.map(() => Math.max(0, Math.round(base + (Math.random() - 0.5) * noise * 2)))
        visits   = rand(this.totals.visits   / n, this.totals.visits   * 0.3 / n)
        clicks   = rand(this.totals.clicks   / n, this.totals.clicks   * 0.3 / n)
        bookings = rand(this.totals.bookings / n, this.totals.bookings * 0.3 / n)
      }

      const ctx = this.$refs.trendCanvas.getContext('2d')
      this.chart = new window.Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [
            { label: 'Visitas',          data: visits,   borderColor: '#06d6a0',
              backgroundColor: 'rgba(6,214,160,0.07)',  tension: 0.4, fill: true,
              pointBackgroundColor: '#06d6a0', pointRadius: 4 },
            { label: 'Clicks Calendly',  data: clicks,   borderColor: '#e63946',
              backgroundColor: 'rgba(230,57,70,0.07)',  tension: 0.4, fill: true,
              pointBackgroundColor: '#e63946', pointRadius: 4 },
            { label: 'Citas agendadas',  data: bookings, borderColor: '#ffd166',
              backgroundColor: 'rgba(255,209,102,0.07)', tension: 0.4, fill: true,
              pointBackgroundColor: '#ffd166', pointRadius: 4 },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: 'rgba(10,10,10,0.9)',
              padding: 12,
              titleColor: '#fff',
              bodyColor: 'rgba(255,255,255,0.65)',
              borderColor: 'rgba(255,255,255,0.08)',
              borderWidth: 1,
            },
          },
          scales: {
            x: { grid: { color: 'rgba(255,255,255,0.04)' },
                 ticks: { color: 'rgba(255,255,255,0.45)', font: { size: 11 } } },
            y: { grid: { color: 'rgba(255,255,255,0.04)' },
                 ticks: { color: 'rgba(255,255,255,0.45)', font: { size: 11 } },
                 beginAtZero: true },
          },
        },
      })
    },
  },
}
</script>

<style scoped>
/* ── BASE ─────────────────────────────────────── */
.admin-dashboard { max-width: 1400px; margin: 0 auto; }

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1.5rem;
}
.dashboard-header h2 { font-size: 1.75rem; color: white; margin: 0 0 .25rem; }
.dashboard-header p  { color: var(--color-text-muted); font-size: .9rem; margin: 0; }

.data-badge {
  display: flex;
  align-items: center;
  gap: .5rem;
  background: rgba(6,214,160,.1);
  border: 1px solid rgba(6,214,160,.3);
  color: var(--color-accent);
  padding: .35rem .875rem;
  border-radius: 20px;
  font-size: .78rem;
  font-weight: 600;
}
.dot {
  width: 7px; height: 7px;
  background: var(--color-accent);
  border-radius: 50%;
  animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* ── FILTROS ──────────────────────────────────── */
.filters-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: flex-end;
  background: rgba(255,255,255,.025);
  border: 1px solid rgba(255,255,255,.09);
  border-radius: 14px;
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
}
.filter-group { display: flex; flex-direction: column; gap: .35rem; }
.filter-group label {
  font-size: .72rem; font-weight: 600;
  color: rgba(255,255,255,.45);
  text-transform: uppercase; letter-spacing: .07em;
}
.filter-select, .filter-input {
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(255,255,255,.14);
  border-radius: 8px;
  color: white;
  padding: .5rem .875rem;
  font-size: .875rem;
  cursor: pointer;
  transition: border-color .2s;
}
.filter-select:focus,.filter-input:focus { outline: none; border-color: var(--color-accent); }
.filter-select option { background: #1a1a1a; }

.period-pills { display: flex; gap: .35rem; }
.period-pill {
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(255,255,255,.13);
  border-radius: 8px;
  color: rgba(255,255,255,.55);
  padding: .45rem .875rem;
  font-size: .82rem; font-weight: 600;
  cursor: pointer;
  transition: all .2s;
}
.period-pill:hover { background: rgba(255,255,255,.12); color: white; }
.period-pill.active {
  background: rgba(6,214,160,.18);
  border-color: var(--color-accent);
  color: var(--color-accent);
}

/* ── LOADING / ERROR ──────────────────────────── */
.loading-state {
  display: flex; flex-direction: column;
  align-items: center; gap: 1rem;
  padding: 5rem 2rem;
  color: rgba(255,255,255,.5);
}
.spinner {
  width: 40px; height: 40px;
  border: 3px solid rgba(255,255,255,.1);
  border-left-color: var(--color-accent);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error-state {
  display: flex; flex-direction: column;
  align-items: center; gap: 1rem;
  padding: 4rem 2rem; text-align: center;
  color: rgba(255,255,255,.55);
  font-size: 1.5rem;
}
.error-state p { font-size: 1rem; }
.btn-retry {
  background: rgba(6,214,160,.13);
  border: 1px solid var(--color-accent);
  color: var(--color-accent);
  padding: .6rem 1.5rem; border-radius: 8px;
  cursor: pointer; font-weight: 600;
}
.btn-retry:hover { background: rgba(6,214,160,.22); }

/* ── GRID ─────────────────────────────────────── */
.row { display: flex; gap: 1.25rem; width: 100%; margin-bottom: 1.25rem; }

/* KPI row */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
  margin-bottom: 0;
}

.kpi-card {
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.09);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: border-color .2s, transform .2s;
}
.kpi-card:hover { border-color: rgba(255,255,255,.18); transform: translateY(-2px); }
.kpi-card.accent {
  background: linear-gradient(135deg, rgba(6,214,160,.12) 0%, rgba(6,214,160,.04) 100%);
  border-color: rgba(6,214,160,.35);
}

.kpi-icon { font-size: 2rem; flex-shrink: 0; }
.kpi-body { display: flex; flex-direction: column; gap: .18rem; }
.kpi-label { font-size: .75rem; color: rgba(255,255,255,.45); text-transform: uppercase; letter-spacing: .06em; }
.kpi-value { font-size: 1.75rem; font-weight: 800; color: white; line-height: 1; }
.kpi-sub   { font-size: .73rem; color: rgba(255,255,255,.3); }

/* Cards */
.card {
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.09);
  border-radius: 16px;
  padding: 1.5rem;
  flex: 1;
}

.card-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1.25rem;
}
.card-head h3 { font-size: .975rem; color: white; margin: 0; font-weight: 700; }
.tag {
  font-size: .72rem; color: rgba(255,255,255,.4);
  background: rgba(255,255,255,.06);
  padding: .18rem .6rem; border-radius: 20px;
  white-space: nowrap;
}

/* ── TWO-COL ──────────────────────────────────── */
.two-col { gap: 1.25rem; }
.two-col > .card:first-child { flex: 1.1; }
.two-col > .card:last-child  { flex: 0.9; }

/* ── FUNNEL ───────────────────────────────────── */
.funnel { display: flex; flex-direction: column; gap: 1.1rem; }
.funnel-step { display: flex; flex-direction: column; gap: .3rem; }
.funnel-top, .funnel-bottom {
  display: flex; justify-content: space-between; align-items: center;
}
.funnel-name { font-size: .875rem; color: rgba(255,255,255,.78); font-weight: 500; }
.funnel-n    { font-size: .875rem; color: white; font-weight: 700; }
.funnel-pct  { font-size: .775rem; color: rgba(255,255,255,.45); }
.funnel-drop { font-size: .75rem;  color: rgba(239,68,68,.65); }

/* ── BAR SHARED ───────────────────────────────── */
.bar-track { height: 9px; background: rgba(255,255,255,.06); border-radius: 5px; overflow: hidden; flex: 1; }
.bar-fill  { height: 100%; border-radius: 5px; transition: width .8s ease; }

/* ── SOURCES ──────────────────────────────────── */
.sources { display: flex; flex-direction: column; gap: .875rem; }
.source-row { display: grid; grid-template-columns: 140px 1fr auto; align-items: center; gap: .75rem; }
.source-info { display: flex; align-items: center; gap: .5rem; }
.source-name { font-size: .83rem; color: rgba(255,255,255,.72); white-space: nowrap; }
.source-stats { display: flex; flex-direction: column; align-items: flex-end; gap: .08rem; }
.source-pct { font-size: .83rem; color: white; font-weight: 700; }
.source-n   { font-size: .72rem; color: rgba(255,255,255,.38); }
.empty-sources { font-size: .85rem; color: rgba(255,255,255,.35); text-align: center; padding: 1rem 0; }

/* ── SIGMA ROW ────────────────────────────────── */
.sigma-row {
  display: grid;
  grid-template-columns: 210px repeat(3, 1fr);
  gap: 1.25rem;
  margin-bottom: 0;
}

.gauge-card { display: flex; flex-direction: column; }
.gauge-wrap { display: flex; justify-content: center; }
.gauge-svg  { width: 160px; height: 96px; }
.gauge-arc  { transition: stroke-dasharray 1s ease; }
.gauge-scale {
  display: flex; justify-content: space-between;
  padding: 0 .5rem;
  font-size: .68rem; color: rgba(255,255,255,.28);
  margin-top: .25rem;
}

.sigma-card {
  display: flex; flex-direction: column; gap: .75rem; justify-content: space-between;
}
.sigma-icon  { font-size: 1.5rem; }
.sigma-body  { display: flex; flex-direction: column; gap: .2rem; flex: 1; }
.sigma-label { font-size: .72rem; color: rgba(255,255,255,.42); text-transform: uppercase; letter-spacing: .06em; }
.sigma-value { font-size: 1.75rem; font-weight: 800; color: white; line-height: 1.1; }
.sigma-desc  { font-size: .75rem; color: rgba(255,255,255,.38); }
.sigma-badge {
  display: inline-flex; align-self: flex-start;
  padding: .22rem .7rem; border-radius: 20px; border: 1px solid;
  font-size: .75rem; font-weight: 600;
}

.rty-row  { display: flex; align-items: center; gap: .4rem; flex-wrap: wrap; }
.rty-step { font-size: .8rem; color: rgba(255,255,255,.5); }
.rty-op   { font-size: .75rem; color: rgba(255,255,255,.25); }
.rty-result { font-size: .85rem; font-weight: 700; color: var(--color-accent); }

.ci-bar  { margin-top: .5rem; }
.ci-track {
  position: relative; height: 9px;
  background: rgba(255,255,255,.06); border-radius: 5px;
  overflow: visible; margin-bottom: .4rem;
}
.ci-labels {
  display: flex; justify-content: space-between;
  font-size: .68rem; color: rgba(255,255,255,.35);
}

/* ── PROBABILIDADES ───────────────────────────── */
.prob-card { flex: 1; }
.prob-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.1rem;
}
.prob-item {
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.07);
  border-radius: 12px;
  padding: 1rem;
  display: flex; flex-direction: column; gap: .55rem;
}
.prob-head { display: flex; align-items: center; gap: .45rem; }
.prob-name { font-size: .875rem; font-weight: 600; color: white; flex: 1; }
.prob-ci   { font-size: .68rem; color: rgba(255,255,255,.32); }

.prob-bar-row { display: flex; align-items: center; gap: .75rem; }
.prob-val { font-size: .95rem; font-weight: 700; min-width: 50px; text-align: right; }
.prob-meta { font-size: .7rem; color: rgba(255,255,255,.3); }

/* ── TENDENCIA ────────────────────────────────── */
.trend-card { flex: 1; }
.chart-wrap { position: relative; height: 240px; width: 100%; }
.chart-wrap canvas { width: 100% !important; height: 100% !important; }
.legend { display: flex; gap: 1.5rem; justify-content: center; margin-top: 1rem; }
.leg-item { display: flex; align-items: center; gap: .4rem; font-size: .78rem; color: rgba(255,255,255,.5); }
.leg-dot  { width: 10px; height: 10px; border-radius: 50%; }

/* ── RESPONSIVE ──────────────────────────────── */
@media (max-width: 1200px) {
  .sigma-row { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 968px) {
  .kpi-row   { grid-template-columns: repeat(2, 1fr); }
  .two-col   { flex-direction: column; }
  .sigma-row { grid-template-columns: 1fr; }
  .prob-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .kpi-row { grid-template-columns: 1fr; }
  .filters-bar { gap: 1rem; padding: 1rem; }
  .dashboard-header { flex-direction: column; align-items: flex-start; gap: .5rem; }
  .source-row { grid-template-columns: 100px 1fr auto; }
}
</style>
