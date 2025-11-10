from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.config.database import Base
import secrets


class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_expiracion = Column(DateTime(timezone=True), nullable=False, index=True)

    # Relación con usuario
    usuario = relationship("Usuario", back_populates="sesiones")

    @staticmethod
    def generar_token() -> str:
        """Genera un token único para la sesión"""
        return secrets.token_urlsafe(32)