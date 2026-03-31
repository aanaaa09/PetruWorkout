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
            :value="(form.hero.benefits || []).join('\n')"
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

      <!-- ── TAB RESULTS ── -->
      <section v-if="activeTab === 'results'" class="editor-section">
        <h3>🏆 Sección Resultados</h3>

        <!-- Textos generales -->
        <div class="subsection">
          <h4>📝 Textos generales</h4>
          <div class="field">
            <label>Etiqueta superior</label>
            <input v-model="form.results.section_tag" type="text" />
          </div>
          <div class="field">
            <label>Título principal</label>
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
            <button @click="saveResultsTexts" class="btn-save" :disabled="saving === 'results-texts'">
              {{ saving === 'results-texts' ? '⏳ Guardando...' : '💾 Guardar Textos' }}
            </button>
          </div>
          <div v-if="saved === 'results-texts'" class="msg-ok">✅ Guardado.</div>
        </div>

        <div class="divider"></div>

        <!-- Usuarios / tarjetas de resultados -->
        <div class="subsection">
          <h4>👤 Tarjetas de resultados</h4>
          <p class="hint">Edita los datos de cada usuario que aparece en la sección de resultados</p>

          <div class="users-accordion">
            <div
              v-for="(user, idx) in form.results.users"
              :key="user.id"
              class="user-block"
              :class="{ open: openUser === idx }"
            >
              <!-- Header del acordeón -->
              <button class="user-block-header" @click="openUser = openUser === idx ? null : idx">
                <span class="user-num">👤 {{ user.name || 'Usuario ' + user.id }}</span>
                <span class="user-chevron">{{ openUser === idx ? '▲' : '▼' }}</span>
              </button>

              <!-- Contenido expandido -->
              <div v-if="openUser === idx" class="user-block-body">
                <div class="fields-grid">
                  <div class="field">
                    <label>Nombre</label>
                    <input v-model="user.name" type="text" placeholder="Ej: Esteban" />
                  </div>
                  <div class="field">
                    <label>Edad</label>
                    <input v-model="user.age" type="text" placeholder="Ej: 37 años" />
                  </div>
                  <div class="field">
                    <label>Estadísticas</label>
                    <input v-model="user.stats" type="text" placeholder="Ej: Antes 25% grasa, ahora 12%" />
                  </div>
                  <div class="field">
                    <label>Duración</label>
                    <input v-model="user.duration" type="text" placeholder="Ej: 12 semanas" />
                  </div>
                  <div class="field">
                    <label>Hora del mensaje (WhatsApp)</label>
                    <input v-model="user.whatsapp_time" type="text" placeholder="Ej: 17:12" />
                  </div>
                </div>

                <div class="field" style="margin-top:.75rem">
                  <label>💬 Texto del mensaje (burbuja WhatsApp)</label>
                  <textarea v-model="user.whatsapp_text" rows="4" placeholder="Escribe aquí el testimonio del cliente..."></textarea>
                </div>

                <!-- Vista previa WhatsApp -->
                <div v-if="user.whatsapp_text" class="whatsapp-preview">
                  <span class="preview-label">Vista previa:</span>
                  <div class="wa-bubble">
                    <p class="wa-text">{{ user.whatsapp_text }}</p>
                    <span class="wa-time">{{ user.whatsapp_time || '00:00' }}</span>
                  </div>
                </div>

                <div class="divider"></div>

                <!-- Imagen del usuario -->
                <div class="image-upload-block">
                  <h5>🖼️ Imagen del usuario</h5>
                  <p class="hint">Formato .webp · dimensiones aprox. <strong>661×674 px</strong> (tolerancia ±50 px)</p>
                  <p class="hint">Slug de imagen: <code>{{ user.image_slug }}</code></p>

                  <div class="upload-row">
                    <img
                      v-if="imagePreviews[user.image_slug]"
                      :src="imagePreviews[user.image_slug]"
                      class="preview-thumb"
                      alt="preview"
                    />
                    <div class="upload-actions">
                      <label class="btn-file">
                        📁 Seleccionar .webp
                        <input
                          type="file"
                          accept=".webp"
                          style="display:none"
                          @change="handleImageSelect($event, user.image_slug)"
                        />
                      </label>
                      <button
                        v-if="imageFiles[user.image_slug]"
                        @click="uploadImage(user.image_slug)"
                        class="btn-save"
                        :disabled="uploadingImage === user.image_slug"
                      >
                        {{ uploadingImage === user.image_slug ? '⏳ Subiendo...' : '⬆️ Subir imagen' }}
                      </button>
                    </div>
                  </div>
                  <div v-if="imageErrors[user.image_slug]" class="msg-error">{{ imageErrors[user.image_slug] }}</div>
                  <div v-if="imageSuccess[user.image_slug]" class="msg-ok">✅ Imagen subida correctamente</div>
                </div>

                <!-- Guardar este usuario -->
                <div class="actions" style="margin-top:1rem">
                  <button @click="saveUser(idx)" class="btn-save" :disabled="saving === 'user-' + idx">
                    {{ saving === 'user-' + idx ? '⏳ Guardando...' : '💾 Guardar Usuario ' + user.id }}
                  </button>
                </div>
                <div v-if="saved === 'user-' + idx" class="msg-ok">✅ Guardado correctamente.</div>
              </div>
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <!-- Vídeos de testimonios -->
        <div class="subsection">
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

const defaultUsers = [1, 2, 3, 4].map(id => ({
  id,
  name: `Usuario ${id}`,
  age: '',
  stats: '',
  duration: '',
  whatsapp_text: '',
  whatsapp_time: '',
  image_slug: `user${id}`,
}))

const defaultContent = {
  hero: { title: '', highlight: '', benefits: [], button_text: '' },
  video: { youtube_id: '', section_tag: '', title: '', cta_title: '', cta_description: '' },
  results: {
    section_tag: '',
    title: '',
    videos_title: '',
    videos_subtitle: '',
    users: defaultUsers,
  },
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
      openUser: null,
      // Images
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
        if (!r.ok) throw new Error(data.detail || 'Error cargando contenido')

        const c = data.content || {}

        // Hero
        this.form.hero = { ...defaultContent.hero, ...(c.hero || {}) }

        // Video
        this.form.video = { ...defaultContent.video, ...(c.video || {}) }
        this.youtubeId = this.form.video.youtube_id || ''

        // Results — merge especial para users array
        const resultsBase = { ...defaultContent.results }
        if (c.results) {
          this.form.results = {
            ...resultsBase,
            ...c.results,
            // Si ya hay users guardados, usar esos; si no, usar los defaults
            users: (c.results.users && c.results.users.length > 0)
              ? c.results.users
              : defaultUsers,
          }
        } else {
          this.form.results = resultsBase
        }

        // Testimonials
        this.form.testimonials = { ...defaultContent.testimonials, ...(c.testimonials || {}) }

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
        if (!r.ok) throw new Error(data.detail || 'Error guardando')
        this.saved = section
        setTimeout(() => { if (this.saved === section) this.saved = null }, 4000)
      } catch (e) {
        alert('❌ Error al guardar: ' + e.message)
      } finally {
        this.saving = null
      }
    },

    async saveResultsTexts() {
      this.saving = 'results-texts'
      this.saved = null
      try {
        // Guardar solo los campos de texto, manteniendo users
        const payload = {
          results: {
            section_tag:     this.form.results.section_tag,
            title:           this.form.results.title,
            videos_title:    this.form.results.videos_title,
            videos_subtitle: this.form.results.videos_subtitle,
            users:           this.form.results.users,
          }
        }
        const r = await fetch(`${API}/api/admin/content`, {
          method: 'PUT',
          headers: { token: this.token(), 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
        const data = await r.json()
        if (!r.ok) throw new Error(data.detail || 'Error guardando')
        this.saved = 'results-texts'
        setTimeout(() => { if (this.saved === 'results-texts') this.saved = null }, 4000)
      } catch (e) {
        alert('❌ Error al guardar: ' + e.message)
      } finally {
        this.saving = null
      }
    },

    async saveUser(idx) {
      const key = `user-${idx}`
      this.saving = key
      this.saved = null
      try {
        // Guardamos todo results con el usuario modificado
        const payload = {
          results: { ...this.form.results }
        }
        const r = await fetch(`${API}/api/admin/content`, {
          method: 'PUT',
          headers: { token: this.token(), 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
        const data = await r.json()
        if (!r.ok) throw new Error(data.detail || 'Error guardando')
        this.saved = key
        setTimeout(() => { if (this.saved === key) this.saved = null }, 4000)
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

    handleImageSelect(event, slug) {
      const file = event.target.files[0]
      if (!file) return
      this.imageFiles = { ...this.imageFiles, [slug]: file }
      this.imageErrors = { ...this.imageErrors, [slug]: null }
      this.imageSuccess = { ...this.imageSuccess, [slug]: false }
      const reader = new FileReader()
      reader.onload = e => { this.imagePreviews = { ...this.imagePreviews, [slug]: e.target.result } }
      reader.readAsDataURL(file)
    },

    async uploadImage(slug) {
      const file = this.imageFiles[slug]
      if (!file) return
      this.uploadingImage = slug
      this.imageErrors = { ...this.imageErrors, [slug]: null }
      try {
        const fd = new FormData()
        fd.append('name', slug)
        fd.append('file', file)
        const r = await fetch(`${API}/api/admin/content/image`, {
          method: 'POST',
          headers: { token: this.token() },
          body: fd,
        })
        const data = await r.json()
        if (!r.ok) throw new Error(data.detail || 'Error al subir imagen')
        this.imageSuccess = { ...this.imageSuccess, [slug]: true }
        this.imageFiles = { ...this.imageFiles, [slug]: null }
      } catch (e) {
        this.imageErrors = { ...this.imageErrors, [slug]: e.message }
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
.editor-section h4 { font-size: .95rem; color: white; margin: 0 0 .75rem; }

.subsection { display: flex; flex-direction: column; gap: .9rem; }

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

.fields-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; }

/* Acordeón de usuarios */
.users-accordion { display: flex; flex-direction: column; gap: .6rem; }
.user-block { border: 1px solid rgba(255,255,255,.1); border-radius: 12px; overflow: hidden; }
.user-block.open { border-color: var(--color-accent); }
.user-block-header {
  width: 100%; display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 1.25rem; background: rgba(255,255,255,.04);
  border: none; color: white; cursor: pointer; font-size: .9rem; font-weight: 600;
  transition: background .2s;
}
.user-block-header:hover { background: rgba(255,255,255,.08); }
.user-block.open .user-block-header { background: rgba(6,214,160,.1); color: var(--color-accent); }
.user-num { display: flex; align-items: center; gap: .5rem; }
.user-chevron { font-size: .75rem; color: rgba(255,255,255,.4); }

.user-block-body { padding: 1.25rem; display: flex; flex-direction: column; gap: .9rem; }

/* WhatsApp preview */
.whatsapp-preview { display: flex; flex-direction: column; gap: .4rem; margin-top: .25rem; }
.preview-label { font-size: .72rem; color: rgba(255,255,255,.35); text-transform: uppercase; letter-spacing: .05em; }
.wa-bubble {
  background: linear-gradient(135deg, #128C7E, #075E54);
  border-radius: 8px; padding: .75rem 1rem;
  max-width: 480px; position: relative;
}
.wa-bubble::before {
  content: ''; position: absolute; top: 0; left: -8px;
  border-style: solid; border-width: 0 8px 8px 0;
  border-color: transparent #075E54 transparent transparent;
}
.wa-text { color: white; font-size: .875rem; line-height: 1.5; margin: 0 0 .4rem; word-break: break-word; }
.wa-time { display: block; text-align: right; font-size: .68rem; color: rgba(255,255,255,.55); }

/* Image upload */
.image-upload-block { display: flex; flex-direction: column; gap: .6rem; }
.image-upload-block h5 { font-size: .875rem; color: white; margin: 0; }
.upload-row { display: flex; align-items: flex-start; gap: 1rem; flex-wrap: wrap; }
.upload-actions { display: flex; flex-direction: column; gap: .5rem; }
.preview-thumb { width: 100px; height: 80px; object-fit: cover; border-radius: 6px; }
.btn-file {
  display: inline-flex; align-items: center; gap: .4rem; cursor: pointer;
  padding: .6rem 1rem; background: rgba(255,255,255,.07); border: 1px dashed rgba(255,255,255,.2);
  border-radius: 8px; color: rgba(255,255,255,.7); font-size: .82rem; font-weight: 600;
  transition: all .2s;
}
.btn-file:hover { background: rgba(255,255,255,.12); border-color: var(--color-accent); color: white; }
.file-name { font-size: .75rem; color: rgba(255,255,255,.45); word-break: break-all; }

/* Videos grid */
.video-upload-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.upload-card {
  background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.1);
  border-radius: 12px; padding: 1.25rem; display: flex; flex-direction: column; gap: .6rem;
}
.upload-label { font-size: .8rem; font-weight: 700; color: rgba(255,255,255,.6); text-transform: uppercase; }

/* Misc */
.youtube-row { display: flex; gap: .75rem; }
.youtube-row input { flex: 1; }
.actions { margin-top: .25rem; }
.divider { height: 1px; background: rgba(255,255,255,.08); margin: .25rem 0; }
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
.msg-ok    { font-size: .85rem; color: var(--color-accent); font-weight: 600; padding: .4rem 0; }
.msg-error { font-size: .82rem; color: #ff6b6b; font-weight: 600; padding: .4rem 0; }

.state-loading { display: flex; flex-direction: column; align-items: center; gap: 1rem; padding: 4rem 2rem; color: rgba(255,255,255,.4); }
.state-error   { display: flex; flex-direction: column; align-items: center; gap: 1rem; padding: 3rem; color: #ff6b6b; }
.spinner {
  width: 36px; height: 36px; border: 3px solid rgba(255,255,255,.1);
  border-left-color: var(--color-accent); border-radius: 50%; animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .fields-grid { grid-template-columns: 1fr; }
  .video-upload-grid { grid-template-columns: 1fr; }
  .editor-section { padding: 1.25rem; }
}
</style>
