from ..crud import usuario_crud, sesion_crud
from ..utils.validators import validar_email, validar_password, validar_nombre
from ..models.usuario import Usuario
from ..models.sesion import Sesion
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Servicio de autenticación - lógica de negocio"""

    @staticmethod
    def registrar_usuario(db, nombre: str, email: str, password: str):
        """Registra un nuevo usuario"""
        # Validaciones
        if not validar_nombre(nombre):
            return {'success': False, 'error': 'El nombre debe tener al menos 2 caracteres'}

        if not validar_email(email):
            return {'success': False, 'error': 'Email inválido'}

        if not validar_password(password):
            return {'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres'}

        # Verificar si existe
        usuario_existente = usuario_crud.get_by_email(db, email.lower())
        if usuario_existente:
            return {'success': False, 'error': 'Este email ya está registrado'}

        # Crear usuario
        usuario = usuario_crud.create(db, nombre, email.lower(), password)
        if not usuario:
            return {'success': False, 'error': 'Error al crear el usuario'}

        # Crear sesión
        sesion = sesion_crud.create(db, usuario.id)
        if not sesion:
            return {'success': False, 'error': 'Usuario creado pero error al crear sesión'}

        logger.info(f"Usuario registrado: {email}")

        return {
            'success': True,
            'data': {
                'token': sesion.token,
                'usuario': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'puntos': usuario.puntos
                }
            }
        }

    @staticmethod
    def iniciar_sesion(db, email: str, password: str):
        """Inicia sesión"""
        if not email or not password:
            return {'success': False, 'error': 'Email y contraseña son requeridos'}

        usuario = usuario_crud.authenticate(db, email.lower(), password)
        if not usuario:
            return {'success': False, 'error': 'Email o contraseña incorrectos'}

        # Actualizar última conexión
        usuario_crud.update_last_login(db, usuario.id)

        # Crear sesión
        sesion = sesion_crud.create(db, usuario.id)
        if not sesion:
            return {'success': False, 'error': 'Error al crear la sesión'}

        logger.info(f"Usuario autenticado: {email}")

        return {
            'success': True,
            'data': {
                'token': sesion.token,
                'usuario': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'puntos': usuario.puntos
                }
            }
        }

    @staticmethod
    def cerrar_sesion(db, token: str):
        """Cierra sesión"""
        if not token:
            return {'success': False, 'error': 'Token no proporcionado'}

        if sesion_crud.delete_by_token(db, token):
            return {'success': True}

        return {'success': False, 'error': 'Error al cerrar sesión'}

    @staticmethod
    def verificar_sesion(db, token: str):
        """Verifica si una sesión es válida"""
        if not token:
            return {'valida': False, 'error': 'Token no proporcionado'}

        sesion = sesion_crud.validate_token(db, token)
        if sesion:
            usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
            if usuario:
                return {
                    'valida': True,
                    'usuario': {
                        'id': usuario.id,
                        'nombre': usuario.nombre,
                        'email': usuario.email,
                        'puntos': usuario.puntos
                    }
                }

        return {'valida': False, 'error': 'Sesión expirada o inválida'}

    @staticmethod
    def actualizar_puntos(db, token: str, puntos_adicionales: int):
        """Actualiza los puntos de un usuario"""
        sesion = sesion_crud.validate_token(db, token)
        if not sesion:
            return {'success': False, 'error': 'Sesión inválida'}

        usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
        if not usuario:
            return {'success': False, 'error': 'Usuario no encontrado'}

        usuario_crud.add_points(db, usuario.id, puntos_adicionales)

        logger.info(f"Puntos actualizados para usuario {usuario.id}: +{puntos_adicionales}")

        return {
            'success': True,
            'puntos': usuario.puntos + puntos_adicionales
        }

    @staticmethod
    def obtener_ranking(db, limit: int = 10):
        """Obtiene el ranking de usuarios"""
        ranking = usuario_crud.get_ranking(db, limit)
        return {'success': True, 'ranking': ranking or []}