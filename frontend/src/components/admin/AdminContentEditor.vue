<template>
  <div class="content-editor">
    <div class="editor-header">
      <h2>✏️ Editor de Landing</h2>
      <p>Los cambios se publican automáticamente vía GitHub → Railway</p>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>

    <!-- Loading inicial -->
    <div v-if="loading" class="state-loading">
      <div class="spinner"></div>
      <p>Cargando contenido...</p>
    </div>

    <div v-else-if="loadError" class="state-error">
      <p>❌ {{ loadError }}</p>
      <button @click="fetchContent" class="btn-secondary">Reintentar</button>
    </div>

    <template v-else>

      <!-- ── TAB HERO ── -->
      <section v-if="activeTab === 'hero'" class="editor-section">
        <h3>🦸 Sección Hero</h3>

        <div class="field">
          <label>Título principal</label>
          <textarea v-model="form.hero.title" rows="3"></textarea>
        </div>
        <div class="field">
          <label>Palabra/frase resaltada (highlight)</label>
          <input v-model="form.hero.highlight" type="text" />
          <span class="hint">Parte del título que aparece en color acento</span>
        </div>
        <div class="field">
          <label>Texto del botón CTA</label>
          <input v-model="form.hero.button_text" type="text" />
        </div>

        <div class="field">
          <label>Beneficios (uno por línea)</label>
          <textarea
            :value="form.hero.benefits.join('\n')"
            @input="form.hero.benefits = $event.target.value.split('\n')"
            rows="6"
          ></textarea>
        </div>

        <div class="actions">
          <button @click="saveSection('hero')" class="btn-save" :disabled="saving">
            {{ saving === 'hero' ? '⏳ Guardando...' : '💾 Guardar Hero' }}
          </button>
        </div>
        <div v-if="saved === 'hero'" class="msg-ok">✅ Guardado. Railway redesplegará en ~1 min.</div>
      </section>

      <!-- ── TAB VIDEO ── -->
      <section v-if="activeTab === 'video'" class="editor-section">
        <h3>▶️ Sección Vídeo</h3>

        <div class="field">
          <label>Etiqueta superior</label>
          <input v-model="form.video.section_tag" type="text" />
        </div>
        <div class="field">
          <label>Título de la sección</label>
          <textarea v-model="form.video.title" rows="2"></textarea>
        </div>
        <div class="field">
          <label>Título del CTA</label>
          <input v-model="form.video.cta_title" type="text" />
        </div>
        <div class="field">
          <label>Descripción del CTA</label>
          <textarea v-model="form.video.cta_description" rows="3"></textarea>
        </div>

        <div class="divider"></div>

        <div class="field">
          <label>🎬 ID de YouTube</label>
          <div class="youtube-row">
            <input v-model="youtubeId" type="text" placeholder="ej: qDc5uScLz2c" />
            <button @click="saveYoutube" class="btn-save" :disabled="saving === 'youtube'">
              {{ saving === 'youtube' ? '⏳...' : 'Actualizar' }}
            </button>
          </div>
          <span class="hint">Solo el ID, no la URL completa. Actual: <code>{{ form.video.youtube_id }}</code></span>
        </div>
        <div v-if="saved === 'youtube'" class="msg-ok">✅ YouTube actualizado.</div>

        <div class="actions">
          <button @click="saveSection('video')" class="btn-save" :disabled="saving">
            {{ saving === 'video' ? '⏳ Guardando...' : '💾 Guardar Textos Vídeo' }}
          </button>
        </div>
        <div v-if="saved === 'video'" class="msg-ok">✅ Guardado.</div>
      </section>

      <!-- ── TAB RESULTS TEXTOS ── -->
      <section v-if="activeTab === 'results'" class="editor-section">
        <h3>🏆 Sección Resultados — Textos</h3>

        <div class="field">
          <label>Etiqueta superior</label>
          <input v-model="form.results.section_tag" type="text" />
        </div>
        <div class="field">
          <label>Título</label>
          <input v-model="form.results.title" type="text" />
        </div>
        <div class="field">
          <label>Título bloque de vídeos</label>
          <input v-model="form.results.videos_title" type="text" />
        </div>
        <div class="field">
          <label>Subtítulo bloque de vídeos</label>
          <input v-model="form.results.videos_subtitle" type="text" />
        </div>

        <div class="actions">
          <button @click="saveSection('results')" class="btn-save" :disabled="saving">
            {{ saving === 'results' ? '⏳ Guardando...' : '💾 Guardar Textos Resultados' }}
          </button>
        </div>
        <div v-if="saved === 'results'" class="msg-ok">✅ Guardado.</div>

        <!-- Sub-sección: imágenes -->
        <div class="divider"></div>
        <h4>🖼️ Subir imágenes (.webp)</h4>
        <p class="hint">
          La imagen debe tener aprox. <strong>661×674 px</strong> (tolerancia ±50 px).<br>
          Se generarán 3 tamaños automáticamente.
        </p>

        <div class="image-upload-grid">
          <div v-for="slot in imageSlots" :key="slot" class="upload-card">
            <span class="upload-label">{{ slot }}</span>
            <img
              v-if="imagePreviews[slot]"
              :src="imagePreviews[slot]"
              class="preview-thumb"
              alt="preview"
            />
            <label class="btn-file">
              📁 Seleccionar
              <input
                type="file"
                accept=".webp"
                style="display:none"
                @change="handleImageSelect($event, slot)"
              />
            </label>
            <button
              v-if="imageFiles[slot]"
              @click="uploadImage(slot)"
              class="btn-save"
              :disabled="uploadingImage === slot"
            >
              {{ uploadingImage === slot ? '⏳ Subiendo...' : '⬆️ Subir' }}
            </button>
            <div v-if="imageErrors[slot]" class="msg-error">{{ imageErrors[slot] }}</div>
            <div v-if="imageSuccess[slot]" class="msg-ok">✅ Subida correctamente</div>
          </div>
        </div>

        <!-- Sub-sección: vídeos de testimonios -->
        <div class="divider"></div>
        <h4>🎥 Vídeos de testimonios (.mp4)</h4>

        <div class="video-upload-grid">
          <div v-for="slot in videoSlots" :key="slot" class="upload-card">
            <span class="upload-label">{{ slot }}</span>
            <label class="btn-file">
              📁 Seleccionar .mp4
              <input
                type="file"
                accept=".mp4"
                style="display:none"
                @change="handleVideoSelect($event, slot)"
              />
            </label>
            <span v-if="videoFiles[slot]" class="file-name">{{ videoFiles[slot].name }}</span>
            <button
              v-if="videoFiles[slot]"
              @click="uploadVideo(slot)"
              class="btn-save"
              :disabled="uploadingVideo === slot"
            >
              {{ uploadingVideo === slot ? '⏳ Subiendo...' : '⬆️ Subir' }}
            </button>
            <div v-if="videoErrors[slot]" class="msg-error">{{ videoErrors[slot] }}</div>
            <div v-if="videoSuccess[slot]" class="msg-ok">✅ Subido correctamente</div>
          </div>
        </div>
      </section>

      <!-- ── TAB TESTIMONIALS ── -->
      <section v-if="activeTab === 'testimonials'" class="editor-section">
        <h3>⭐ Sección Testimonios</h3>

        <div class="field">
          <label>Etiqueta superior</label>
          <input v-model="form.testimonials.section_tag" type="text" />
        </div>
        <div class="field">
          <label>Título</label>
          <input v-model="form.testimonials.title" type="text" />
        </div>
        <div class="field">
          <label>Subtítulo</label>
          <input v-model="form.testimonials.subtitle" type="text" />
        </div>

        <div class="actions">
          <button @click="saveSection('testimonials')" class="btn-save" :disabled="saving">
            {{ saving === 'testimonials' ? '⏳ Guardando...' : '💾 Guardar Testimonios' }}
          </button>
        </div>
        <div v-if="saved === 'testimonials'" class="msg-ok">✅ Guardado.</div>
      </section>

    </template>
  </div>
</template>

<script>
const API = 'https://petruworkout-production.up.railway.app'

const defaultContent = {
  hero: { title: '', highlight: '', benefits: [], button_text: '' },
  video: { youtube_id: '', section_tag: '', title: '', cta_title: '', cta_description: '' },
  results: { section_tag: '', title: '', videos_title: '', videos_subtitle: '' },
  testimonials: { section_tag: '', title: '', subtitle: '' },
}

export default {
  name: 'AdminContentEditor',
  data() {
    return {
      loading: true,
      loadError: null,
      saving: null,
      saved: null,
      activeTab: 'hero',
      form: JSON.parse(JSON.stringify(defaultContent)),
      youtubeId: '',
      // Images
      imageSlots: ['esteban', 'franck', 'oscar', 'pedro'],
      imageFiles: {},
      imagePreviews: {},
      imageErrors: {},
      imageSuccess: {},
      uploadingImage: null,
      // Videos
      videoSlots: ['video1', 'video2', 'video3'],
      videoFiles: {},
      videoErrors: {},
      videoSuccess: {},
      uploadingVideo: null,
      tabs: [
        { id: 'hero',         label: 'Hero',        icon: '🦸' },
        { id: 'video',        label: 'Vídeo',       icon: '▶️' },
        { id: 'results',      label: 'Resultados',  icon: '🏆' },
        { id: 'testimonials', label: 'Testimonios', icon: '⭐' },
      ],
    }
  },
  mounted() {
    this.fetchContent()
  },
  methods: {
    token() { return localStorage.getItem('admin_token') },

    async fetchContent() {
      this.loading = true
      this.loadError = null
      try {
        const r = await fetch(`${API}/api/admin/content`, {
          headers: { token: this.token() },
        })
        const data = await r.json()
        if (!r.ok) throw new Error(data.detail || 'Error')
        // Merge con defaults para evitar campos nulos
        const c = data.content || {}
        for (const section of Object.keys(defaultContent)) {
          this.form[section] = { ...defaultContent[section], ...(c[section] || {}) }
        }
        this.youtubeId = this.form.video.youtube_id || ''
      } catch (e) {
        this.loadError = e.message
      } finally {
        this.loading = false
      }
    },

    async saveSection(section) {
      this.saving = section
      this.saved = null
      try {
        const r = await fetch(`${API}/api/admin/content`, {
          method: 'PUT',
          headers: { token: this.token(), 'Content-Type': 'application/json' },
          body: JSON.stringify({ [section]: this.form[section] }),
        })
        const data = await r.json()
        if (!r.ok) throw new Error(data.detail || 'Error')
        this.saved = section
        setTimeout(() => { if (this.saved === section) this.saved = null }, 4000)
      } catch (e) {
        alert('❌ Error al guardar: ' + e.message)
      } finally {
        this.saving = null
      }
    },

    async saveYoutube() {
      if (!this.youtubeId.trim()) return
      this.saving = 'youtube'
      this.saved = null
      try {
        const fd = new FormData()
        fd.append('youtube_id', this.youtubeId.trim())
        const r = await fetch(`${API}/api/admin/content/youtube`, {
          method: 'PUT',
          headers: { token: this.token() },
          body: fd,
        })
        const data = await r.json()
        if (!r.ok) throw new Error(data.detail || 'Error')
        this.form.video.youtube_id = this.youtubeId.trim()
        this.saved = 'youtube'
        setTimeout(() => { if (this.saved === 'youtube') this.saved = null }, 4000)
      } catch (e) {
        alert('❌ Error: ' + e.message)
      } finally {
        this.saving = null
      }
    },

    handleImageSelect(event, slot) {
      const file = event.target.files[0]
      if (!file) return
      this.imageFiles = { ...this.imageFiles, [slot]: file }
      this.imageErrors = { ...this.imageErrors, [slot]: null }
      this.imageSuccess = { ...this.imageSuccess, [slot]: false }
      // Preview
      const reader = new FileReader()
      reader.onload = e => { this.imagePreviews = { ...this.imagePreviews, [slot]: e.target.result } }
      reader.readAsDataURL(file)
    },

    async uploadImage(slot) {
      const file = this.imageFiles[slot]
      if (!file) return
      this.uploadingImage = slot
      this.imageErrors = { ...this.imageErrors, [slot]: null }
      try {
        const fd = new FormData()
        fd.append('name', slot)
        fd.append('file', file)
        const r = await fetch(`${API}/api/admin/content/image`, {
          method: 'POST',
          headers: { token: this.token() },
          body: fd,
        })
        const data = await r.json()
        if (!r.ok) throw new Error(data.detail || 'Error al subir imagen')
        this.imageSuccess = { ...this.imageSuccess, [slot]: true }
        this.imageFiles = { ...this.imageFiles, [slot]: null }
      } catch (e) {
        this.imageErrors = { ...this.imageErrors, [slot]: e.message }
      } finally {
        this.uploadingImage = null
      }
    },

    handleVideoSelect(event, slot) {
      const file = event.target.files[0]
      if (!file) return
      this.videoFiles = { ...this.videoFiles, [slot]: file }
      this.videoErrors = { ...this.videoErrors, [slot]: null }
      this.videoSuccess = { ...this.videoSuccess, [slot]: false }
    },

    async uploadVideo(slot) {
      const file = this.videoFiles[slot]
      if (!file) return
      this.uploadingVideo = slot
      this.videoErrors = { ...this.videoErrors, [slot]: null }
      try {
        const fd = new FormData()
        fd.append('slot', slot)
        fd.append('file', file)
        const r = await fetch(`${API}/api/admin/content/video`, {
          method: 'POST',
          headers: { token: this.token() },
          body: fd,
        })
        const data = await r.json()
        if (!r.ok) throw new Error(data.detail || 'Error al subir vídeo')
        this.videoSuccess = { ...this.videoSuccess, [slot]: true }
        this.videoFiles = { ...this.videoFiles, [slot]: null }
      } catch (e) {
        this.videoErrors = { ...this.videoErrors, [slot]: e.message }
      } finally {
        this.uploadingVideo = null
      }
    },
  },
}
</script>

<style scoped>
.content-editor { max-width: 900px; margin: 0 auto; }
.editor-header { margin-bottom: 1.5rem; }
.editor-header h2 { font-size: 1.75rem; color: white; margin: 0 0 .3rem; }
.editor-header p  { color: rgba(255,255,255,.45); font-size: .875rem; margin: 0; }

.tabs { display: flex; gap: .5rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.tab {
  padding: .6rem 1.25rem; border-radius: 10px; border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.04); color: rgba(255,255,255,.55);
  font-size: .875rem; font-weight: 600; cursor: pointer; transition: all .2s;
}
.tab:hover { background: rgba(255,255,255,.08); color: white; }
.tab.active { background: rgba(6,214,160,.18); border-color: var(--color-accent); color: var(--color-accent); }

.editor-section {
  background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.09);
  border-radius: 16px; padding: 2rem; display: flex; flex-direction: column; gap: 1.25rem;
}
.editor-section h3 { font-size: 1.1rem; color: white; margin: 0; }
.editor-section h4 { font-size: .95rem; color: white; margin: 0; }

.field { display: flex; flex-direction: column; gap: .4rem; }
.field label { font-size: .8rem; font-weight: 600; color: rgba(255,255,255,.5); text-transform: uppercase; letter-spacing: .05em; }
.field input, .field textarea {
  background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.13);
  border-radius: 8px; color: white; padding: .75rem 1rem; font-size: .9rem;
  font-family: inherit; resize: vertical; transition: border-color .2s;
}
.field input:focus, .field textarea:focus { outline: none; border-color: var(--color-accent); }
.hint { font-size: .75rem; color: rgba(255,255,255,.35); }
.hint code { background: rgba(255,255,255,.1); padding: .15rem .4rem; border-radius: 4px; font-size: .8rem; }

.youtube-row { display: flex; gap: .75rem; }
.youtube-row input { flex: 1; }

.actions { margin-top: .5rem; }
.btn-save {
  padding: .75rem 1.75rem; background: var(--gradient-primary); color: white;
  border: none; border-radius: 10px; font-weight: 700; font-size: .9rem;
  cursor: pointer; transition: all .2s;
}
.btn-save:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(6,214,160,.35); }
.btn-save:disabled { opacity: .55; cursor: not-allowed; }
.btn-secondary {
  padding: .6rem 1.5rem; background: rgba(255,255,255,.07); color: white;
  border: 1px solid rgba(255,255,255,.18); border-radius: 8px; cursor: pointer;
}

.divider { height: 1px; background: rgba(255,255,255,.08); margin: .5rem 0; }

.msg-ok    { font-size: .85rem; color: var(--color-accent); font-weight: 600; padding: .5rem 0; }
.msg-error { font-size: .82rem; color: #ff6b6b; font-weight: 600; padding: .4rem 0; }

/* Image upload */
.image-upload-grid, .video-upload-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;
}
.upload-card {
  background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.1);
  border-radius: 12px; padding: 1.25rem; display: flex; flex-direction: column; gap: .6rem;
}
.upload-label { font-size: .8rem; font-weight: 700; color: rgba(255,255,255,.6); text-transform: uppercase; }
.preview-thumb { width: 100%; height: 90px; object-fit: cover; border-radius: 6px; }
.btn-file {
  display: inline-flex; align-items: center; gap: .4rem; cursor: pointer;
  padding: .6rem 1rem; background: rgba(255,255,255,.07); border: 1px dashed rgba(255,255,255,.2);
  border-radius: 8px; color: rgba(255,255,255,.7); font-size: .82rem; font-weight: 600;
  transition: all .2s;
}
.btn-file:hover { background: rgba(255,255,255,.12); border-color: var(--color-accent); color: white; }
.file-name { font-size: .75rem; color: rgba(255,255,255,.45); word-break: break-all; }

.state-loading { display: flex; flex-direction: column; align-items: center; gap: 1rem; padding: 4rem 2rem; color: rgba(255,255,255,.4); }
.state-error   { display: flex; flex-direction: column; align-items: center; gap: 1rem; padding: 3rem; color: #ff6b6b; }
.spinner {
  width: 36px; height: 36px; border: 3px solid rgba(255,255,255,.1);
  border-left-color: var(--color-accent); border-radius: 50%; animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .image-upload-grid, .video-upload-grid { grid-template-columns: 1fr; }
  .editor-section { padding: 1.25rem; }
}
</style>
