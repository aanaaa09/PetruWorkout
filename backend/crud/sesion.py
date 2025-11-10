from sqlalchemy.orm import Session
from ..models.sesion import Sesion
from datetime import datetime, timedelta
from ..config.settings import settings
import secrets
import logging

logger = logging.getLogger(__name__)

class SesionCRUD:
    """CRUD para sesiones"""

    @staticmethod
    def generate_token() -> str:
        """Genera un token único"""
        return secrets.token_urlsafe(32)

    def create(self, db: Session, usuario_id: int) -> Sesion:
        """Crea una nueva sesión"""
        token = self.generate_token()
        fecha_expiracion = datetime.now() + timedelta(days=settings.SESSION_DURATION_DAYS)

        sesion = Sesion(
            usuario_id=usuario_id,
            token=token,
            fecha_expiracion=fecha_expiracion
        )

        db.add(sesion)
        db.commit()
        db.refresh(sesion)

        logger.info(f"Sesión creada para usuario {usuario_id}")
        return sesion

    def get_by_token(self, db: Session, token: str) -> Sesion | None:
        """Busca una sesión por token"""
        return db.query(Sesion).filter(
            Sesion.token == token,
            Sesion.fecha_expiracion > datetime.now()
        ).first()

    def validate_token(self, db: Session, token: str) -> Sesion | None:
        """Valida un token"""
        return self.get_by_token(db, token)

    def delete_by_token(self, db: Session, token: str) -> bool:
        """Elimina una sesión por token"""
        sesion = db.query(Sesion).filter(Sesion.token == token).first()
        if sesion:
            db.delete(sesion)
            db.commit()
            logger.info(f"Sesión eliminada: {token[:10]}...")
            return True
        return False

    def clean_expired(self, db: Session) -> int:
        """Limpia sesiones expiradas"""
        count = db.query(Sesion).filter(Sesion.fecha_expiracion < datetime.now()).delete()
        db.commit()
        logger.info(f"Sesiones expiradas eliminadas: {count}")
        return count

sesion_crud = SesionCRUD()