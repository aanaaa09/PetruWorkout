from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.config.database import Base


class Sorteo(Base):
    """Sorteos creados por admin"""
    __tablename__ = "sorteos"

    id = Column(Integer, primary_key=True, index=True)

    # Info del sorteo
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    imagen_url = Column(String(500), nullable=True)

    # Fechas
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_fin = Column(DateTime(timezone=True), nullable=False)
    fecha_sorteo = Column(DateTime(timezone=True), nullable=True)  # Cuando se elige ganador

    # Estado
    activo = Column(Boolean, default=True, index=True)
    finalizado = Column(Boolean, default=False)

    # Ganador
    ganador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # Relaciones
    ganador = relationship("Usuario")
    participantes = relationship("ParticipanteSorteo", back_populates="sorteo", cascade="all, delete-orphan")


class ParticipanteSorteo(Base):
    """Participantes en sorteos (solo clientes activos)"""
    __tablename__ = "participantes_sorteo"

    id = Column(Integer, primary_key=True, index=True)
    sorteo_id = Column(Integer, ForeignKey("sorteos.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    fecha_participacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    sorteo = relationship("Sorteo", back_populates="participantes")
    usuario = relationship("Usuario")