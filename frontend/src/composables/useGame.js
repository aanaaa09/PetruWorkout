// Composable para gestionar la lógica del juego
export function useGame() {
  async function syncPlaylist(playlistKey) {
    try {
      const resp = await fetch(`/sync/${playlistKey}`)
      if (!resp.ok) {
        console.warn('Sincronización devolvió status:', resp.status)
      }
      return { success: resp.ok }
    } catch (error) {
      console.error('Error sincronizando playlist:', error)
      return { success: false, error }
    }
  }

  async function loadSong(playlistKey) {
    try {
      const resp = await fetch(`/cancion/${playlistKey}`)
      if (!resp.ok) {
        console.error('Error HTTP cargando canción:', resp.status)
        return { success: false, song: null }
      }
      const data = await resp.json()
      return { success: true, song: data }
    } catch (error) {
      console.error('Error cargando canción:', error)
      return { success: false, song: null, error }
    }
  }

  async function verifyAnswer(playlistKey, titulo, artista) {
    try {
      const resp = await fetch(`/verificar/${playlistKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          titulo: titulo.trim(),
          artista: artista.trim()
        })
      })

      if (!resp.ok) {
        throw new Error('HTTP ' + resp.status)
      }

      const data = await resp.json()

      if (data.correcto) {
        return {
          success: true,
          correcto: true,
          tipo: 'correcto',
          mensaje: `🎉 ¡Correcto!<br><strong>${data.titulo_real}</strong> - ${data.artista_real}`,
          qr: {
            img: data.qr_code,
            url: data.spotify_url,
            titulo: data.titulo_real,
            artista: data.artista_real
          }
        }
      } else {
        const tipoResultado = data.titulo_correcto || data.artista_correcto ? 'parcial' : 'incorrecto'
        return {
          success: true,
          correcto: false,
          tipo: tipoResultado,
          mensaje: data.mensaje
        }
      }
    } catch (error) {
      console.error('Error verificando respuesta:', error)
      return {
        success: false,
        tipo: 'incorrecto',
        mensaje: 'Error al verificar la respuesta 😞'
      }
    }
  }

  async function surrender(playlistKey) {
    try {
      const resp = await fetch(`/rendirse/${playlistKey}`)
      if (!resp.ok) throw new Error('HTTP ' + resp.status)
      const data = await resp.json()

      return {
        success: true,
        tipo: 'incorrecto',
        mensaje: `🏳️ Te rendiste. La respuesta era:<br><strong>${data.titulo_real}</strong> - ${data.artista_real}`,
        qr: {
          img: data.qr_code,
          url: data.spotify_url,
          titulo: data.titulo_real,
          artista: data.artista_real
        }
      }
    } catch (error) {
      console.error('Error al rendirse:', error)
      return {
        success: false,
        tipo: 'incorrecto',
        mensaje: 'Error al obtener la respuesta 😞'
      }
    }
  }

  return {
    syncPlaylist,
    loadSong,
    verifyAnswer,
    surrender
  }
}
