from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.config.database import Base

class Cliente(Base):
    """Cliente con código de acceso válido"""
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Estado del cliente
    activo = Column(Boolean, default=True, index=True)
    codigo_acceso = Column(String(50), unique=True, nullable=False)  # Código único dado por admin
    fecha_activacion = Column(DateTime(timezone=True), server_default=func.now())

    # Ubicación (opcional - para funcionalidad de "gente cerca")
    ciudad = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=True)
    latitud = Column(String(50), nullable=True)  # Para buscar gente cerca
    longitud = Column(String(50), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="cliente")