# backend/services/auth_service.py
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
import logging

from ..config.database import get_db
from ..crud import usuario_crud, sesion_crud
from ..utils.validators import validar_email, validar_password, validar_nombre
from ..models.usuario import Usuario, TipoUsuario

logger = logging.getLogger(__name__)


# ============================================================
# DEPENDENCIA FASTAPI — compartida por todos los routers admin
# ============================================================

def verify_admin_token(
    token: str = Header(None, alias="token"),
    db: Session = Depends(get_db),
) -> Usuario:
    """
    Dependencia FastAPI reutilizable.
    Verifica que el header 'token' pertenezca a una sesión ADMIN activa.

    Raises:
        HTTPException 401: Token ausente, sesión expirada o usuario no encontrado.
        HTTPException 403: El usuario existe pero no es ADMIN.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado en el header")

    sesion = sesion_crud.validate_token(db, token)
    if not sesion:
        raise HTTPException(status_code=401, detail="Sesión expirada o inválida")

    usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if usuario.tipo_usuario != TipoUsuario.ADMIN:
        logger.warning(f"Intento de acceso no autorizado: {usuario.email}")
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Se requieren permisos de administrador.",
        )

    return usuario


# ============================================================
# SERVICIO DE AUTENTICACIÓN
# ============================================================

class AuthService:
    """Servicio de autenticación simplificado"""

    @staticmethod
    def registrar_newsletter(db, nombre: str, email: str, password: str):
        """Registra un usuario para la newsletter"""
        if not validar_nombre(nombre):
            return {'success': False, 'error': 'El nombre debe tener al menos 2 caracteres'}
        if not validar_email(email):
            return {'success': False, 'error': 'Email inválido'}
        if not validar_password(password):
            return {'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres'}

        usuario_existente = usuario_crud.get_by_email(db, email.lower())
        if usuario_existente:
            return {'success': False, 'error': 'Este email ya está registrado'}

        usuario = usuario_crud.create(
            db,
            nombre=nombre,
            email=email.lower(),
            password=password,
            tipo_usuario=TipoUsuario.NEWSLETTER,
        )
        if not usuario:
            return {'success': False, 'error': 'Error al crear el usuario'}

        logger.info(f"Usuario newsletter registrado: {email}")
        return {
            'success': True,
            'mensaje': '¡Registro exitoso! Te has suscrito a nuestra newsletter',
            'usuario': {'id': usuario.id, 'nombre': usuario.nombre, 'email': usuario.email},
        }

    @staticmethod
    def login_admin(db, email: str, password: str):
        """Login solo para admin"""
        if not email or not password:
            return {'success': False, 'error': 'Email y contraseña son requeridos'}

        usuario = usuario_crud.authenticate(db, email.lower(), password)
        if not usuario:
            return {'success': False, 'error': 'Email o contraseña incorrectos'}

        if not usuario.es_admin():
            return {'success': False, 'error': 'No tienes permisos de administrador'}

        usuario_crud.update_last_login(db, usuario.id)

        sesion = sesion_crud.create(db, usuario.id)
        if not sesion:
            return {'success': False, 'error': 'Error al crear la sesión'}

        logger.info(f"Admin autenticado: {email}")
        return {
            'success': True,
            'data': {
                'token': sesion.token,
                'usuario': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'tipo_usuario': usuario.tipo_usuario.value,
                },
            },
        }

    @staticmethod
    def cerrar_sesion(db, token: str):
        """Cierra sesión (solo admin)"""
        if not token:
            return {'success': False, 'error': 'Token no proporcionado'}
        if sesion_crud.delete_by_token(db, token):
            return {'success': True}
        return {'success': False, 'error': 'Error al cerrar sesión'}

    @staticmethod
    def verificar_admin(db, token: str):
        """Verifica si el token es de un admin"""
        if not token:
            return {'valida': False, 'error': 'Token no proporcionado'}

        sesion = sesion_crud.validate_token(db, token)
        if sesion:
            usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
            if usuario and usuario.es_admin():
                return {
                    'valida': True,
                    'usuario': {
                        'id': usuario.id,
                        'nombre': usuario.nombre,
                        'email': usuario.email,
                        'tipo_usuario': usuario.tipo_usuario.value,
                    },
                }

        return {'valida': False, 'error': 'Sesión expirada o no eres administrador'}

    @staticmethod
    def cancelar_suscripcion(db, email: str):
        """Cancela suscripción a newsletter"""
        usuario = usuario_crud.get_by_email(db, email.lower())
        if not usuario:
            return {'success': False, 'error': 'Email no encontrado'}
        if not usuario.suscrito_newsletter:
            return {'success': False, 'error': 'Ya no estás suscrito'}

        usuario.suscrito_newsletter = False
        db.commit()
        logger.info(f"Usuario canceló suscripción: {email}")
        return {'success': True, 'mensaje': 'Te has dado de baja de la newsletter'}