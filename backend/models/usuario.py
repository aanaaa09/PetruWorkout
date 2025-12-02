# backend/models/usuario.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from backend.config.database import Base
import bcrypt
import enum


class TipoUsuario(enum.Enum):
    """Tipos de usuario"""
    NEWSLETTER = "newsletter"  # Usuario registrado solo para newsletter
    ADMIN = "admin"            # Administrador (Petru)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    # Datos básicos
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Tipo de usuario
    tipo_usuario = Column(
        SQLEnum(TipoUsuario),
        default=TipoUsuario.NEWSLETTER,
        nullable=False,
        index=True
    )

    # Newsletter
    suscrito_newsletter = Column(Boolean, default=True, nullable=False)
    fecha_suscripcion = Column(DateTime(timezone=True), server_default=func.now())

    # Fechas
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    ultima_conexion = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    sesiones = relationship("Sesion", back_populates="usuario", cascade="all, delete-orphan")

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashea una contraseña usando bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verificar_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def es_admin(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.tipo_usuario == TipoUsuario.ADMIN