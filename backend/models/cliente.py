from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.config.database import Base


class Cliente(Base):
    """Cliente con suscripción activa"""
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Suscripción
    activo = Column(Boolean, default=True, index=True)
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_expiracion = Column(DateTime(timezone=True), nullable=True)
    codigo_acceso = Column(String(50), unique=True, nullable=True)  # Código único para activar suscripción

    # Créditos de clases
    creditos_disponibles = Column(Integer, default=0)

    # Ubicación (solo ciudad y país)
    ciudad = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="cliente")
    clases_asistidas = relationship("AsistenciaClase", back_populates="cliente", cascade="all, delete-orphan")
    tickets_sorteo = relationship("TicketSorteo", back_populates="cliente", cascade="all, delete-orphan")

