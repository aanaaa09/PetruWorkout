# ========================================
# ARCHIVO CORREGIDO: backend/services/calculator_token_service.py
# ========================================
"""
Servicio para gestionar tokens de acceso a la calculadora
"""
from datetime import datetime, timedelta
import secrets
from sqlalchemy.orm import Session
from ..crud.usuario import usuario_crud
from ..models.usuario import Usuario  # ✅ MOVIDO AL INICIO
import logging

logger = logging.getLogger(__name__)


class CalculatorTokenService:
    """Gestiona tokens para acceso a la calculadora"""

    TOKEN_EXPIRY_DAYS = 30  # El token expira en 30 días

    @staticmethod
    def generate_token() -> str:
        """Genera un token único y seguro"""
        return secrets.token_urlsafe(32)

    def create_token_for_user(self, db: Session, email: str) -> dict:
        """
        Crea o actualiza el token de calculadora para un usuario

        Args:
            db: Sesión de base de datos
            email: Email del usuario

        Returns:
            dict con 'success', 'token' y 'url'
        """
        try:
            # Buscar usuario
            usuario = usuario_crud.get_by_email(db, email.lower())

            if not usuario:
                return {
                    'success': False,
                    'error': 'Usuario no encontrado'
                }

            # Generar nuevo token
            token = self.generate_token()

            # Actualizar usuario
            usuario.calculator_token = token
            usuario.calculator_token_created = datetime.now()

            db.commit()
            db.refresh(usuario)

            # Construir URL
            calculator_url = f"https://petrucalistenia.com/calculator?token={token}"

            logger.info(f"Token de calculadora creado para {email}")

            return {
                'success': True,
                'token': token,
                'url': calculator_url
            }

        except Exception as e:
            logger.error(f"Error creando token para {email}: {e}")
            db.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    def validate_token(self, db: Session, token: str) -> dict:
        """
        Valida un token de calculadora

        Args:
            db: Sesión de base de datos
            token: Token a validar

        Returns:
            dict con 'valid' y opcionalmente 'usuario' o 'error'
        """
        try:
            # ✅ VERIFICAR QUE EL TOKEN NO SEA VACÍO
            if not token or token.strip() == '':
                return {
                    'valid': False,
                    'error': 'Token vacío o inválido'
                }

            # Buscar usuario con este token
            usuario = db.query(Usuario).filter(
                Usuario.calculator_token == token
            ).first()

            if not usuario:
                logger.warning(f"Token no encontrado en BD: {token[:10]}...")
                return {
                    'valid': False,
                    'error': 'Token inválido o no existe'
                }

            # ✅ VERIFICAR SI EL TOKEN HA EXPIRADO
            if usuario.calculator_token_created:
                expiry_date = usuario.calculator_token_created + timedelta(days=self.TOKEN_EXPIRY_DAYS)

                if datetime.now() > expiry_date:
                    logger.warning(f"Token expirado para usuario: {usuario.email}")
                    return {
                        'valid': False,
                        'error': f'Token expirado. Por favor, regístrate nuevamente.'
                    }
            else:
                # Si no tiene fecha de creación, asumir que es inválido
                logger.warning(f"Token sin fecha de creación para usuario: {usuario.email}")
                return {
                    'valid': False,
                    'error': 'Token inválido (sin fecha de creación)'
                }


            logger.info(f"Token validado correctamente para usuario: {usuario.email}")
            return {
                'valid': True,
                'usuario': {
                    'id': usuario.id,
                    'email': usuario.email,
                    'nombre': usuario.nombre
                }
            }

        except Exception as e:
            logger.error(f"Error validando token: {e}")
            import traceback
            traceback.print_exc()
            return {
                'valid': False,
                'error': f'Error al validar token: {str(e)}'
            }


# Instancia global
calculator_token_service = CalculatorTokenService()