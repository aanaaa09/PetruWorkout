from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from backend.config.database import Base
import hashlib


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    puntos = Column(Integer, default=0, index=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    ultima_conexion = Column(DateTime(timezone=True), nullable=True)

    # Relación con sesiones
    sesiones = relationship("Sesion", back_populates="usuario", cascade="all, delete-orphan")

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashea una contraseña usando SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verificar_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return self.password_hash == self.hash_password(password)