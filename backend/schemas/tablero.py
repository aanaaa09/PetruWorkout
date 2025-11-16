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
    tipo: str  # 'registrado' o 'invitado'
    nombre: str
    email: Optional[str] = None
    token: Optional[str] = None
    usuario_id: Optional[int] = None


class Pareja(BaseModel):
    nombre_pareja: str  # Nombre de la pareja
    miembro1: MiembroPareja
    miembro2: MiembroPareja
    puntos: int = 0  # Puntos acumulados de la pareja


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
    posicion: int  # Posición donde se quiere insertar (índice)
    titulo: Optional[str] = None
    artista: Optional[str] = None


class CrearCasillaRequest(BaseModel):
    partida_id: int
    jugador_index: int
    posicion: int  # 0=al inicio, -1=al final, n=después de índice n


class KaraokeRequest(BaseModel):
    partida_id: int
    jugador_index: int
    audio_base64: str  # Audio grabado del karaoke


class ReiniciarPartidaRequest(BaseModel):
    partida_id: int
    mismos_jugadores: bool


class CancionLineaTiempo(BaseModel):
    titulo: str
    artista: str
    anio: int
    spotify_id: str
    spotify_url: str


class EstadoLineaTiempo(BaseModel):
    canciones_ordenadas: List[CancionLineaTiempo]  # Lista ordenada por año
    puntos: int
    completado_10: bool
    karaoke_realizado: bool
    necesita_karaoke: bool