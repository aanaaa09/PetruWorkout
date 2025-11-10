// Configuración centralizada de playlists
export const PLAYLISTS = {
  juego_clasico: {
    id: 'juego_clasico',
    nombre: 'Juego Clásico',
    icon: '🎮',
    gradient: 'linear-gradient(135deg, #f093fb, #f5576c)',
    shadow: 'rgba(240, 147, 251, 0.3)'
  },
  urban_hits: {
    id: 'urban_hits',
    nombre: 'Urban Hits',
    icon: '🔥',
    gradient: 'linear-gradient(135deg, #4ecdc4, #44a08d)',
    shadow: 'rgba(68, 160, 141, 0.3)'
  },
  ochenta_noventa: {
    id: 'ochenta_noventa',
    nombre: 'Los 80 y 90',
    icon: '📻',
    gradient: 'linear-gradient(135deg, #45b7d1, #96c93d)',
    shadow: 'rgba(69, 183, 209, 0.3)'
  },
  flamenco_rumba: {
    id: 'flamenco_rumba',
    nombre: 'Flamenco y Rumba',
    icon: '💃',
    gradient: 'linear-gradient(135deg, #ff6b6b, #ee5a52)',
    shadow: 'rgba(238, 90, 82, 0.3)'
  },
  pop_espanol: {
    id: 'pop_espanol',
    nombre: 'Pop Español',
    icon: '🎤',
    gradient: 'linear-gradient(135deg, #6c5ce7, #a29bfe)',
    shadow: 'rgba(108, 92, 231, 0.3)'
  }
}

export const GAME_MODES = {
  individual: {
    id: 'individual',
    nombre: 'Individual',
    descripcion: 'A tu ritmo',
    icon: '🎵',
    disponible: true
  },
  tablero: {
    id: 'tablero',
    nombre: 'Tablero',
    descripcion: 'Con casillas',
    icon: '🎲',
    disponible: false
  },
  online: {
    id: 'online',
    nombre: 'Online',
    descripcion: 'Multijugador',
    icon: '🌍',
    disponible: false
  }
}

export const API_BASE_URL = 'http://localhost:5001/api'
