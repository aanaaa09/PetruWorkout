from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from backend.models.usuario import Usuario, TipoUsuario
from backend.models.page_visit import PageVisit
from backend.models.calendly_click import CalendlyClick
from backend.models.calendly_booking import CalendlyBooking
from backend.models.consulta import Consulta
from backend.crud.usuario import usuario_crud

logger = logging.getLogger(__name__)


def authenticate_admin(db: Session, email: str, password: str) -> Optional[Usuario]:
    """
    Autentica un administrador (verifica credenciales y que sea ADMIN)
    """
    usuario = usuario_crud.authenticate(db, email, password)

    if not usuario:
        return None

    if usuario.tipo_usuario != TipoUsuario.ADMIN:
        logger.warning(f"Intento de login no-admin: {email}")
        return None

    return usuario


def get_dashboard_stats(db: Session) -> dict:
    """
    Obtiene estadísticas para el dashboard de administración
    """
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

    # Tasa de conversión
    tasa_conversion = (total_bookings / total_visitas * 100) if total_visitas > 0 else 0

    return {
        'total_usuarios_newsletter': total_newsletter,
        'total_consultas': total_consultas,
        'total_visitas': total_visitas,
        'visitas_unicas': visitas_unicas,
        'total_clicks_calendly': total_clicks,
        'total_bookings': total_bookings,
        'tasa_conversion': round(tasa_conversion, 2),
        'trafico_por_fuente': [
            {'fuente': t[0], 'total': t[1]}
            for t in trafico_fuentes
        ]
    }


def get_users_list(
        db: Session,
        tipo: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
) -> dict:
    """
    Lista usuarios con filtros opcionales
    """
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


def delete_user(db: Session, user_id: int, admin_id: int) -> dict:
    """
    Elimina un usuario de la base de datos.
    No permite que un admin se elimine a sí mismo.
    """
    # Verificar que no sea auto-eliminación
    if user_id == admin_id:
        raise ValueError("Un administrador no puede eliminarse a sí mismo")

    # Buscar el usuario
    user = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not user:
        raise ValueError("Usuario no encontrado")

    # Guardar info antes de eliminar
    user_email = user.email

    # Eliminar el usuario (cascada elimina sesiones automáticamente)
    db.delete(user)
    db.commit()

    logger.info(f"Usuario eliminado: {user_email} (ID: {user_id})")

    return {
        "deleted": True,
        "user_id": user_id,
        "email": user_email
    }


def get_consultas_list(
        db: Session,
        limit: int = 100,
        offset: int = 0
) -> dict:
    """
    Lista consultas recibidas
    """
    query = db.query(Consulta).order_by(Consulta.fecha_envio.desc())

    total = query.count()
    consultas = query.limit(limit).offset(offset).all()

    return {
        'total': total,
        'consultas': [
            {
                'id': c.id,
                'nombre': c.nombre,
                'email': c.email,
                'asunto': c.asunto,
                'mensaje': c.mensaje,
                'fecha_envio': c.fecha_envio.isoformat() if c.fecha_envio else None
            }
            for c in consultas
        ]
    }


def get_bookings_list(
        db: Session,
        limit: int = 100,
        offset: int = 0
) -> dict:
    """
    Lista reservas de Calendly
    """
    query = db.query(CalendlyBooking).order_by(CalendlyBooking.timestamp.desc())

    total = query.count()
    bookings = query.limit(limit).offset(offset).all()

    return {
        'total': total,
        'bookings': [
            {
                'id': b.id,
                'invitee_name': b.invitee_name,
                'invitee_email': b.invitee_email,
                'event_start_time': b.event_start_time.isoformat() if b.event_start_time else None,
                'traffic_source': b.traffic_source,
                'timestamp': b.timestamp.isoformat() if b.timestamp else None
            }
            for b in bookings
        ]
    }