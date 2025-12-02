# backend/crud/usuario.py
from sqlalchemy.orm import Session
from ..models.usuario import Usuario, TipoUsuario
from datetime import datetime
import bcrypt
import logging

logger = logging.getLogger(__name__)


class UsuarioCRUD:
    """CRUD para usuarios"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashea una contraseña usando bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def create(
            self,
            db: Session,
            nombre: str,
            email: str,
            password: str,
            tipo_usuario: TipoUsuario = TipoUsuario.NEWSLETTER
    ) -> Usuario:
        """Crea un nuevo usuario"""
        password_hash = self.hash_password(password)

        usuario = Usuario(
            nombre=nombre,
            email=email.lower(),
            password_hash=password_hash,
            tipo_usuario=tipo_usuario,
            suscrito_newsletter=True  # Por defecto suscrito
        )

        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        logger.info(f"Usuario creado: {email} ({tipo_usuario.value})")
        return usuario

    def get_by_email(self, db: Session, email: str) -> Usuario | None:
        """Busca un usuario por email"""
        return db.query(Usuario).filter(Usuario.email == email.lower()).first()

    def get_by_id(self, db: Session, usuario_id: int) -> Usuario | None:
        """Busca un usuario por ID"""
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def authenticate(self, db: Session, email: str, password: str) -> Usuario | None:
        """Autentica un usuario"""
        usuario = self.get_by_email(db, email.lower())

        if not usuario:
            return None

        if self.verify_password(password, usuario.password_hash):
            return usuario

        return None

    def update_last_login(self, db: Session, usuario_id: int):
        """Actualiza última conexión"""
        usuario = self.get_by_id(db, usuario_id)
        if usuario:
            usuario.ultima_conexion = datetime.now()
            db.commit()

    def get_subscribers(self, db: Session):
        """Obtiene todos los usuarios suscritos a la newsletter"""
        return db.query(Usuario).filter(
            Usuario.suscrito_newsletter == True
        ).all()


usuario_crud = UsuarioCRUD()