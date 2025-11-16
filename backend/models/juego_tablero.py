from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, func, Boolean
from backend.config.database import Base


class PartidaTablero(Base):
    """Modelo para almacenar partidas del modo tablero"""
    __tablename__ = "partidas_tablero"

    id = Column(Integer, primary_key=True, index=True)
    playlist_key = Column(String(100), nullable=False)
    tipo_juego = Column(String(20), nullable=False)  # 'individual' o 'parejas'
    estado = Column(String(20), default='activa')  # 'activa', 'karaoke', 'finalizada'
    jugadores = Column(JSON, nullable=False)
    turno_actual = Column(Integer, default=0)

    # Canción actual y canciones servidas
    cancion_actual = Column(JSON, nullable=True)
    canciones_servidas = Column(JSON, default=list)

    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_fin = Column(DateTime(timezone=True), nullable=True)


class LineaTiempoJugador(Base):
    """
    Línea de tiempo de canciones de cada jugador/pareja
    Usa SortedDict donde key=año, value=info_cancion
    """
    __tablename__ = "lineas_tiempo_jugadores"

    id = Column(Integer, primary_key=True, index=True)
    partida_id = Column(Integer, ForeignKey("partidas_tablero.id", ondelete="CASCADE"), nullable=False)
    jugador_index = Column(Integer, nullable=False)

    # Almacenado como JSON: {año: {titulo, artista, spotify_id, spotify_url}}
    # Ejemplo: {"1985": {"titulo": "Africa", "artista": "Toto", ...}, "1990": {...}}
    canciones_por_anio = Column(JSON, default=dict)

    puntos_actuales = Column(Integer, default=0)
    completado_10 = Column(Boolean, default=False)
    karaoke_realizado = Column(Boolean, default=False)
    puntos_karaoke = Column(Integer, default=0)  # Puntos del karaoke (0-20)