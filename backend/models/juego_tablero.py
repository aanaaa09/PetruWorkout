from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, func, Boolean
from backend.config.database import Base


class PartidaTablero(Base):
    """Modelo para almacenar partidas del modo tablero"""
    __tablename__ = "partidas_tablero"

    id = Column(Integer, primary_key=True, index=True)
    playlist_key = Column(String(100), nullable=False)
    tipo_juego = Column(String(20), nullable=False)  # 'individual' o 'parejas'
    estado = Column(String(20), default='activa')  # 'activa', 'finalizada'
    jugadores = Column(JSON, nullable=False)  # Lista de jugadores con su info
    turno_actual = Column(Integer, default=0)
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_fin = Column(DateTime(timezone=True), nullable=True)


class TreeMapJugador(Base):
    """TreeMap de canciones de cada jugador/pareja"""
    __tablename__ = "treemap_jugadores"

    id = Column(Integer, primary_key=True, index=True)
    partida_id = Column(Integer, ForeignKey("partidas_tablero.id", ondelete="CASCADE"), nullable=False)
    jugador_index = Column(Integer, nullable=False)  # Índice del jugador en la partida
    canciones = Column(JSON, default=list)  # Lista ordenada de canciones con año
    puntos_actuales = Column(Integer, default=0)
    completado_10 = Column(Boolean, default=False)  # Si ya completó 10 canciones
    karaoke_realizado = Column(Boolean, default=False)