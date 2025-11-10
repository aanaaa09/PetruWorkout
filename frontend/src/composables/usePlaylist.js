// Composable para gestionar playlists
import { PLAYLISTS } from '../config/playlists'

export function usePlaylist() {
  function getPlaylistInfo(playlistKey) {
    return PLAYLISTS[playlistKey] || {
      nombre: 'Playlist',
      icono: '🎵',
      clase: ''
    }
  }

  function getAllPlaylists() {
    return PLAYLISTS
  }

  function getPlaylistName(playlistKey) {
    const playlist = PLAYLISTS[playlistKey]
    return playlist ? `${playlist.icono} ${playlist.nombre}` : 'Playlist'
  }

  return {
    getPlaylistInfo,
    getAllPlaylists,
    getPlaylistName
  }
}
