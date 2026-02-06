# backend/routers/admin_panel.py
"""
Router para el panel de administración
Incluye: Login, Dashboard, Gestión de usuarios, Envío de emails con adjuntos
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..config.database import get_db
from ..crud import admin_crud
from ..models.usuario import Usuario, TipoUsuario
from ..models.page_visit import PageVisit
from ..models.calendly_click import CalendlyClick
from ..models.calendly_booking import CalendlyBooking
from ..models.consulta import Consulta
from ..crud.usuario import usuario_crud
from ..crud.sesion import sesion_crud
from ..schemas.admin import (
    AdminLoginRequest,
    AdminChangePasswordRequest,
    AdminSendEmailRequest,
    AdminDashboardResponse
)
from ..services.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ============================================
# DEPENDENCIA: VERIFICAR ADMIN (CON HEADER)
# ============================================

def verify_admin_token(
        token: str = Header(None, alias="token"),  # ← ALIAS EXPLÍCITO
        db: Session = Depends(get_db)
) -> Usuario:
    """
    Verifica que el token pertenezca a un usuario admin

    El token se recibe en el header 'token'

    Raises:
        HTTPException: Si el token es inválido o no es admin
    """
    # Verificar que el token fue proporcionado
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token no proporcionado en el header"
        )

    # Verificar sesión
    sesion = sesion_crud.validate_token(db, token)
    if not sesion:
        raise HTTPException(
            status_code=401,
            detail="Sesión expirada o inválida"
        )

    # Obtener usuario
    usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    # Verificar que sea admin
    if usuario.tipo_usuario != TipoUsuario.ADMIN:
        logger.warning(f"Intento de acceso no autorizado: {usuario.email}")
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Se requieren permisos de administrador."
        )

    return usuario


# ============================================
# LOGIN DE ADMIN
# ============================================

@router.post("/login")
def admin_login(
        data: AdminLoginRequest,
        db: Session = Depends(get_db)
):
    """Login exclusivo para administradores"""
    try:
        # Usar admin_crud para autenticar
        usuario = admin_crud.authenticate_admin(db, data.email, data.password)

        if not usuario:
            raise HTTPException(
                status_code=401,
                detail="Credenciales inválidas o no es administrador"
            )

        # Actualizar última conexión
        usuario_crud.update_last_login(db, usuario.id)

        # Crear sesión
        sesion = sesion_crud.create(db, usuario.id)

        logger.info(f"✅ Admin login exitoso: {usuario.email}")

        return {
            'success': True,
            'token': sesion.token,
            'admin': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.email
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login de admin: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# ============================================
# DASHBOARD - ESTADÍSTICAS
# ============================================

@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_dashboard(
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db)
):
    """Retorna estadísticas del dashboard"""
    try:
        stats = admin_crud.get_dashboard_stats(db)
        return AdminDashboardResponse(**stats)

    except Exception as e:
        logger.error(f"Error obteniendo dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas")


# ============================================
# LISTAR USUARIOS
# ============================================

@router.get("/users")
def get_users(
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db),
        tipo: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
):
    """Lista usuarios con filtros opcionales"""
    try:
        result = admin_crud.get_users_list(db, tipo, limit, offset)
        return {
            'success': True,
            **result
        }

    except Exception as e:
        logger.error(f"Error listando usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error al listar usuarios")


# ============================================
# ELIMINAR USUARIO
# ============================================

@router.delete("/users/{user_id}")
def delete_user_endpoint(
        user_id: int,
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db)
):
    """Elimina un usuario"""
    try:
        result = admin_crud.delete_user(db, user_id, admin.id)
        logger.info(f"✅ Usuario {user_id} eliminado por admin {admin.email}")
        return result

    except ValueError as e:
        logger.warning(f"Error validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error eliminando usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar usuario")