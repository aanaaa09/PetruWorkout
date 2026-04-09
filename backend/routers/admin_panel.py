# backend/routers/admin_panel.py
"""
Panel de administración.
Solo gestión HTTP: login, usuarios, consultas, bookings y envío de emails.
Toda la lógica de negocio vive en los servicios correspondientes.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..config.database import get_db
from ..crud import admin_crud
from ..models.usuario import Usuario, TipoUsuario
from ..crud.usuario import usuario_crud
from ..crud.sesion import sesion_crud
from ..schemas.admin import AdminLoginRequest,AdminChangePasswordRequest
from ..services.auth_service import verify_admin_token
from ..services.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── Login ─────────────────────────────────────────────────────────

@router.post("/login")
def admin_login(data: AdminLoginRequest, db: Session = Depends(get_db)):
    """Login exclusivo para administradores."""
    try:
        usuario = admin_crud.authenticate_admin(db, data.email, data.password)
        if not usuario:
            raise HTTPException(status_code=401, detail="Credenciales inválidas o no es administrador")

        usuario_crud.update_last_login(db, usuario.id)
        sesion = sesion_crud.create(db, usuario.id)

        logger.info(f"Admin login exitoso: {usuario.email}")
        return {
            'success': True,
            'token': sesion.token,
            'admin': {'id': usuario.id, 'nombre': usuario.nombre, 'email': usuario.email},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login de admin: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/change-password")
def change_password(
    data: AdminChangePasswordRequest,
    admin: Usuario = Depends(verify_admin_token),
    db: Session = Depends(get_db),
):
    """Cambia la contraseña del administrador autenticado."""
    try:
        if not usuario_crud.verify_password(data.current_password, admin.password_hash):
            raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")

        if len(data.new_password) < 6:
            raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 6 caracteres")

        admin.password_hash = usuario_crud.hash_password(data.new_password)
        db.commit()

        logger.info(f"Contraseña cambiada para admin: {admin.email}")
        return {"success": True, "mensaje": "Contraseña actualizada correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cambiando contraseña: {e}")
        raise HTTPException(status_code=500, detail="Error al cambiar la contraseña")

# ── Usuarios ──────────────────────────────────────────────────────

@router.get("/users")
def get_users(
    admin: Usuario = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    tipo: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """Lista usuarios con filtros opcionales."""
    try:
        result = admin_crud.get_users_list(db, tipo, limit, offset)
        return {'success': True, **result}
    except Exception as e:
        logger.error(f"Error listando usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error al listar usuarios")


@router.delete("/users/{user_id}")
def delete_user_endpoint(
    user_id: int,
    admin: Usuario = Depends(verify_admin_token),
    db: Session = Depends(get_db),
):
    """Elimina un usuario (solo tipo NEWSLETTER)."""
    try:
        result = admin_crud.delete_user(db, user_id, admin.id)
        logger.info(f"Usuario {user_id} eliminado por admin {admin.email}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error eliminando usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar usuario")


# ── Consultas ─────────────────────────────────────────────────────

@router.get("/consultas")
def get_consultas(
    admin: Usuario = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
):
    """Lista consultas recibidas."""
    try:
        result = admin_crud.get_consultas_list(db, limit, offset)
        return {'success': True, **result}
    except Exception as e:
        logger.error(f"Error listando consultas: {e}")
        raise HTTPException(status_code=500, detail="Error al listar consultas")


# ── Bookings ──────────────────────────────────────────────────────

@router.get("/bookings")
def get_bookings(
    admin: Usuario = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
):
    """Lista reservas de Calendly."""
    try:
        result = admin_crud.get_bookings_list(db, limit, offset)
        return {'success': True, **result}
    except Exception as e:
        logger.error(f"Error listando bookings: {e}")
        raise HTTPException(status_code=500, detail="Error al listar bookings")


# ── Envío masivo de emails ─────────────────────────────────────────

@router.post("/send-email")
async def send_email_to_users(
    admin: Usuario = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    subject: str = Form(...),
    message: str = Form(...),
    send_to: str = Form(...),
    selected_ids: Optional[str] = Form(None),
    attachments: Optional[List[UploadFile]] = File(None),
):
    """
    Envía email a usuarios con adjuntos opcionales.
    send_to: "all" o "selected".
    selected_ids: IDs separados por coma (solo si send_to="selected").
    """
    try:
        if send_to == "all":
            destinatarios = db.query(Usuario).filter(
                Usuario.tipo_usuario == TipoUsuario.NEWSLETTER,
                Usuario.suscrito_newsletter == True,
            ).all()
        elif send_to == "selected" and selected_ids:
            ids = [int(i.strip()) for i in selected_ids.split(',')]
            destinatarios = db.query(Usuario).filter(Usuario.id.in_(ids)).all()
        else:
            raise HTTPException(status_code=400, detail="Debe especificar destinatarios válidos")

        if not destinatarios:
            raise HTTPException(status_code=400, detail="No hay destinatarios seleccionados")

        # Preparar adjuntos
        attachment_data = []
        if attachments:
            for file in attachments:
                content = await file.read()
                attachment_data.append({'content': content, 'name': file.filename})

        # Enviar
        enviados, errores = 0, 0
        for usuario in destinatarios:
            try:
                success = email_service.send_newsletter_email(
                    to_email=usuario.email,
                    to_name=usuario.nombre,
                    subject=subject,
                    message=message,
                    attachments=attachment_data,
                )
                if success:
                    enviados += 1
                else:
                    errores += 1
            except Exception as e:
                logger.error(f"Error enviando a {usuario.email}: {e}")
                errores += 1

        logger.info(f"Emails enviados: {enviados}, Errores: {errores}")
        return {'success': True, 'enviados': enviados, 'errores': errores, 'total': len(destinatarios)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en envío masivo: {e}")
        raise HTTPException(status_code=500, detail=f"Error al enviar emails: {str(e)}")