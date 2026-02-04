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
    """
    Login exclusivo para administradores

    Verifica:
    - Email y contraseña correctos
    - tipo_usuario = ADMIN
    """
    try:
        # Autenticar usuario
        usuario = usuario_crud.authenticate(db, data.email, data.password)

        if not usuario:
            logger.warning(f"Intento de login fallido: {data.email}")
            raise HTTPException(
                status_code=401,
                detail="Email o contraseña incorrectos"
            )

        # CRÍTICO: Verificar que sea admin
        if usuario.tipo_usuario != TipoUsuario.ADMIN:
            logger.warning(f"Intento de acceso no admin: {data.email}")
            raise HTTPException(
                status_code=403,
                detail="Acceso denegado. Esta cuenta no tiene permisos de administrador."
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
# LOGOUT DE ADMIN
# ============================================

@router.post("/logout")
def admin_logout(
        token: str = Header(None, alias="token"),  # ← ALIAS EXPLÍCITO
        db: Session = Depends(get_db)
):
    """Cierra la sesión del admin"""
    try:
        if not token:
            raise HTTPException(status_code=400, detail="Token no proporcionado")

        if sesion_crud.delete_by_token(db, token):
            logger.info("Admin logout exitoso")
            return {'success': True, 'message': 'Sesión cerrada correctamente'}

        raise HTTPException(status_code=400, detail="Error al cerrar sesión")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        raise HTTPException(status_code=500, detail="Error al cerrar sesión")


# ============================================
# VERIFICAR SESIÓN
# ============================================

@router.post("/verify")
def verify_admin_session(
        token: str = Header(None, alias="token"),  # ← ALIAS EXPLÍCITO
        db: Session = Depends(get_db)
):
    """Verifica si el token de admin es válido"""
    try:
        if not token:
            return {
                'valid': False,
                'error': 'Token no proporcionado'
            }

        admin = verify_admin_token(token, db)

        return {
            'valid': True,
            'admin': {
                'id': admin.id,
                'nombre': admin.nombre,
                'email': admin.email
            }
        }

    except HTTPException as e:
        return {
            'valid': False,
            'error': e.detail
        }


# ============================================
# CAMBIAR CONTRASEÑA
# ============================================

@router.post("/change-password")
def change_password(
        data: AdminChangePasswordRequest,
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del admin
    Requiere la contraseña actual para confirmar
    """
    try:
        # Verificar contraseña actual
        if not usuario_crud.verify_password(data.current_password, admin.password_hash):
            raise HTTPException(
                status_code=400,
                detail="Contraseña actual incorrecta"
            )

        # Validar nueva contraseña
        if len(data.new_password) < 6:
            raise HTTPException(
                status_code=400,
                detail="La nueva contraseña debe tener al menos 6 caracteres"
            )

        # Hashear nueva contraseña
        new_password_hash = usuario_crud.hash_password(data.new_password)

        # Actualizar en BD
        admin.password_hash = new_password_hash
        db.commit()

        logger.info(f"✅ Contraseña actualizada para admin: {admin.email}")

        return {
            'success': True,
            'message': 'Contraseña actualizada correctamente'
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cambiando contraseña: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al cambiar contraseña")


# ============================================
# DASHBOARD - ESTADÍSTICAS
# ============================================

@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_dashboard(
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db)
):
    """
    Retorna estadísticas del dashboard
    """
    try:
        # Total usuarios newsletter
        total_newsletter = db.query(Usuario).filter(
            Usuario.tipo_usuario == TipoUsuario.NEWSLETTER,
            Usuario.suscrito_newsletter == True
        ).count()

        # Total consultas
        total_consultas = db.query(Consulta).count()

        # Total visitas
        total_visitas = db.query(PageVisit).count()

        # Visitas únicas
        visitas_unicas = db.query(func.count(distinct(PageVisit.session_id))).scalar()

        # Clicks a Calendly
        total_clicks = db.query(CalendlyClick).count()

        # Bookings completados
        total_bookings = db.query(CalendlyBooking).count()

        # Tráfico por fuente (últimos 30 días)
        fecha_limite = datetime.now() - timedelta(days=30)
        trafico_fuentes = db.query(
            PageVisit.traffic_source,
            func.count(PageVisit.id).label('total')
        ).filter(
            PageVisit.timestamp >= fecha_limite
        ).group_by(
            PageVisit.traffic_source
        ).all()

        # Conversión (clicks / visitas * 100)
        tasa_conversion = (total_bookings / total_visitas * 100) if total_visitas > 0 else 0

        return AdminDashboardResponse(
            total_usuarios_newsletter=total_newsletter,
            total_consultas=total_consultas,
            total_visitas=total_visitas,
            visitas_unicas=visitas_unicas,
            total_clicks_calendly=total_clicks,
            total_bookings=total_bookings,
            tasa_conversion=round(tasa_conversion, 2),
            trafico_por_fuente=[
                {'fuente': t[0], 'total': t[1]}
                for t in trafico_fuentes
            ]
        )

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
    """
    Lista usuarios con filtros opcionales
    """
    try:
        query = db.query(Usuario)

        # Filtrar por tipo
        if tipo == 'newsletter':
            query = query.filter(Usuario.tipo_usuario == TipoUsuario.NEWSLETTER)
        elif tipo == 'admin':
            query = query.filter(Usuario.tipo_usuario == TipoUsuario.ADMIN)

        # Ordenar por fecha de registro (más recientes primero)
        query = query.order_by(Usuario.fecha_registro.desc())

        # Paginación
        total = query.count()
        usuarios = query.limit(limit).offset(offset).all()

        return {
            'success': True,
            'total': total,
            'usuarios': [
                {
                    'id': u.id,
                    'nombre': u.nombre,
                    'email': u.email,
                    'tipo_usuario': u.tipo_usuario.value,
                    'suscrito_newsletter': u.suscrito_newsletter,
                    'fecha_registro': u.fecha_registro.isoformat() if u.fecha_registro else None,
                    'ultima_conexion': u.ultima_conexion.isoformat() if u.ultima_conexion else None
                }
                for u in usuarios
            ]
        }

    except Exception as e:
        logger.error(f"Error listando usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error al listar usuarios")


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

        logger.info(f"Emails enviados: {enviados}, Errores: {errores}")

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