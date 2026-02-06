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
    """
    Elimina un usuario
    - Solo permite eliminar usuarios tipo NEWSLETTER
    - Rechaza eliminación de usuarios ADMIN
    """
    try:
        result = admin_crud.delete_user(db, user_id, admin.id)
        logger.info(f"Usuario {user_id} eliminado por admin {admin.email}")
        return result

    except ValueError as e:
        logger.warning(f"Error validación: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))  # 403 Forbidden
    except Exception as e:
        logger.error(f"Error eliminando usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar usuario")
# ============================================
# LISTAR CONSULTAS
# ============================================

@router.get("/consultas")
def get_consultas(
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db),
        limit: int = 100,
        offset: int = 0
):
    """Lista consultas recibidas"""
    try:
        result = admin_crud.get_consultas_list(db, limit, offset)
        return {
            'success': True,
            **result
        }
    except Exception as e:
        logger.error(f"Error listando consultas: {e}")
        raise HTTPException(status_code=500, detail="Error al listar consultas")


# ============================================
# LISTAR BOOKINGS
# ============================================

@router.get("/bookings")
def get_bookings(
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db),
        limit: int = 100,
        offset: int = 0
):
    """Lista reservas de Calendly"""
    try:
        result = admin_crud.get_bookings_list(db, limit, offset)
        return {
            'success': True,
            **result
        }
    except Exception as e:
        logger.error(f"Error listando bookings: {e}")
        raise HTTPException(status_code=500, detail="Error al listar bookings")


# ============================================
# ENVIAR EMAIL (CON ADJUNTOS)
# ============================================

@router.post("/send-email")
async def send_email_to_users(
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db),
        subject: str = Form(...),
        message: str = Form(...),
        send_to: str = Form(...),  # "all" o "selected"
        selected_ids: Optional[str] = Form(None),  # IDs separados por coma
        attachments: Optional[List[UploadFile]] = File(None)
):
    """
    Envía email a usuarios con opción de adjuntos

    send_to: "all" (todos los newsletter) o "selected" (IDs específicos)
    selected_ids: "1,2,3,4" (string de IDs separados por coma)
    attachments: Lista de archivos (PDF, imágenes, etc)
    """
    try:
        # Obtener destinatarios
        if send_to == "all":
            destinatarios = db.query(Usuario).filter(
                Usuario.tipo_usuario == TipoUsuario.NEWSLETTER,
                Usuario.suscrito_newsletter == True
            ).all()
        elif send_to == "selected" and selected_ids:
            ids = [int(id.strip()) for id in selected_ids.split(',')]
            destinatarios = db.query(Usuario).filter(Usuario.id.in_(ids)).all()
        else:
            raise HTTPException(
                status_code=400,
                detail="Debe especificar destinatarios válidos"
            )

        if not destinatarios:
            raise HTTPException(
                status_code=400,
                detail="No hay destinatarios seleccionados"
            )

        logger.info(f"📧 Enviando email a {len(destinatarios)} usuarios...")

        # Preparar adjuntos si existen
        attachment_data = []
        if attachments:
            for file in attachments:
                content = await file.read()
                attachment_data.append({
                    'content': content,
                    'name': file.filename
                })

        # Enviar emails
        enviados = 0
        errores = 0

        for usuario in destinatarios:
            try:
                success = await email_service.send_newsletter_email(
                    to_email=usuario.email,
                    to_name=usuario.nombre,
                    subject=subject,
                    message=message,
                    attachments=attachment_data
                )

                if success:
                    enviados += 1
                else:
                    errores += 1

            except Exception as e:
                logger.error(f"Error enviando a {usuario.email}: {e}")
                errores += 1

        logger.info(f"✅ Emails enviados: {enviados}, Errores: {errores}")

        return {
            'success': True,
            'enviados': enviados,
            'errores': errores,
            'total': len(destinatarios)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en envío masivo: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al enviar emails: {str(e)}")