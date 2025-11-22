from sqlalchemy.orm import Session
from ..models.usuario import Usuario
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

    def create(self, db: Session, nombre: str, email: str, password: str) -> Usuario:
        """Crea un nuevo usuario"""
        password_hash = self.hash_password(password)

        # Generar nombre_usuario del email si no se proporciona
        nombre_usuario = email.split('@')[0].lower()

        usuario = Usuario(
            nombre=nombre,
            apellidos="",
            email=email.lower(),
            nombre_usuario=nombre_usuario,
            password_hash=password_hash
        )

        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        logger.info(f"Usuario creado: {email}")
        return usuario

    def get_by_email(self, db: Session, email: str) -> Usuario | None:
        """Busca un usuario por email"""
        return db.query(Usuario).filter(Usuario.email == email.lower()).first()

    def get_by_id(self, db: Session, usuario_id: int) -> Usuario | None:
        """Busca un usuario por ID"""
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def authenticate(self, db: Session, email: str, password: str) -> Usuario | None:
        """Autentica un usuario usando bcrypt"""
        usuario = self.get_by_email(db, email.lower())

        if not usuario:
            return None

        # Verificar password con bcrypt
        if self.verify_password(password, usuario.password_hash):
            return usuario

        return None

    def update_last_login(self, db: Session, usuario_id: int):
        """Actualiza última conexión"""
        usuario = self.get_by_id(db, usuario_id)
        if usuario:
            usuario.ultima_conexion = datetime.now()
            db.commit()


usuario_crud = UsuarioCRUD()