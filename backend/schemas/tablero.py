from pydantic import BaseModel
from typing import List, Optional


class JugadorIndividual(BaseModel):
    tipo: str  # 'registrado' o 'invitado'
    nombre: str
    email: Optional[str] = None
    puntos: int = 0
    token: Optional[str] = None
    usuario_id: Optional[int] = None


class MiembroPareja(BaseModel):
    tipo: str
    nombre: str
    email: Optional[str] = None
    token: Optional[str] = None
    usuario_id: Optional[int] = None


class Pareja(BaseModel):
    nombre_pareja: str
    miembro1: MiembroPareja
    miembro2: MiembroPareja


class ConfiguracionJugadores(BaseModel):
    tipo_juego: str  # 'individual' o 'parejas'
    jugadores_individuales: Optional[List[JugadorIndividual]] = None
    parejas: Optional[List[Pareja]] = None


class IniciarPartidaRequest(BaseModel):
    playlist_key: str
    configuracion: ConfiguracionJugadores


class ColocarCancionRequest(BaseModel):
    partida_id: int
    jugador_index: int
    posicion: int  # Posición en el TreeMap donde se coloca
    titulo: Optional[str] = None
    artista: Optional[str] = None
    # Datos de la canción actual (en producción esto debería estar en servidor)
    titulo_real: str
    artista_real: str
    anio_real: int
    spotify_id: str
    spotify_url: str


class KaraokeRequest(BaseModel):
    partida_id: int
    jugador_index: int
    puntos_karaoke: int  # Entre 0 y 20


class CancionTreeMap(BaseModel):
    titulo: str
    artista: str
    anio: int
    correcta: bool
    spotify_id: str
    spotify_url: str


class EstadoTreeMap(BaseModel):
    canciones: List[CancionTreeMap]
    puntos: int
    completado_10: bool
    karaoke_realizado: bool