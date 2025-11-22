from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.config.database import Base


class Resena(Base):
    """Reseñas de clientes (aprobadas por admin)"""
    __tablename__ = "resenas"

    id = Column(Integer, primary_key=True, index=True)

    # Autor
    nombre_autor = Column(String(200), nullable=False)

    # Contenido
    texto = Column(Text, nullable=False)
    valoracion = Column(Integer, nullable=False)  # 1-5 estrellas

    # Estado
    aprobada = Column(Boolean, default=False, index=True)  # Solo admin puede aprobar
    visible = Column(Boolean, default=True)  # Admin puede ocultar sin borrar

    # Fechas
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_aprobacion = Column(DateTime(timezone=True), nullable=True)