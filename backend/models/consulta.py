from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func
from backend.config.database import Base


class Consulta(Base):
    """Consultas/dudas enviadas por usuarios no registrados"""
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True)

    # Datos del remitente
    nombre = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)

    # Contenido
    asunto = Column(String(300), nullable=False)
    mensaje = Column(Text, nullable=False)

    # Estado
    leida = Column(Boolean, default=False, index=True)
    respondida = Column(Boolean, default=False)

    # Fecha
    fecha_envio = Column(DateTime(timezone=True), server_default=func.now())