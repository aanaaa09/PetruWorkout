# backend/services/lead_service.py
"""
Lógica de negocio para el registro de leads.
Orquesta: verificar existente → crear usuario → conceder acceso → generar token → enviar email.
"""

import secrets
import logging
from sqlalchemy.orm import Session

from ..crud.usuario import usuario_crud
from ..models.usuario import TipoUsuario
from .calculator_token_service import calculator_token_service
from .email_service import email_service

logger = logging.getLogger(__name__)


class LeadService:

    @staticmethod
    def register(db: Session, email: str) -> dict:
        email = email.lower()

        # ── Usuario ya existe ──────────────────────────────────────
        usuario_existente = usuario_crud.get_by_email(db, email)
        if usuario_existente:
            if not usuario_existente.team_access_granted:
                usuario_existente.team_access_granted = True
                db.commit()
                logger.info(f"Acceso concedido a usuario existente: {email}")
            return {
                'success': True,
                'mensaje': 'Email ya registrado',
                'nuevo': False,
                'has_team_access': True,
            }

        # ── Usuario nuevo ──────────────────────────────────────────
        temp_password = secrets.token_urlsafe(32)
        nombre = email.split('@')[0].capitalize()

        usuario = usuario_crud.create(
            db,
            nombre=nombre,
            email=email,
            password=temp_password,
            tipo_usuario=TipoUsuario.NEWSLETTER,
        )
        usuario.team_access_granted = True
        db.commit()
        db.refresh(usuario)

        # ── Token calculadora ──────────────────────────────────────
        token_result = calculator_token_service.create_token_for_user(db, email)
        calculator_url = (
            token_result['url']
            if token_result['success']
            else "https://petrucalistenia.com/calculator"
        )
        if not token_result['success']:
            logger.error(f"No se pudo crear token calculadora para {email}")

        # ── Email de bienvenida ────────────────────────────────────
        email_enviado = False
        try:
            email_enviado = email_service.send_welcome_lead_email(email, nombre, calculator_url)
        except Exception as e:
            logger.error(f"Error enviando email bienvenida a {email}: {e}")

        if email_enviado:
            logger.info(f"Nuevo lead registrado con email de bienvenida: {email}")
        else:
            logger.warning(f"Lead registrado pero email no enviado: {email}")

        return {
            'success': True,
            'mensaje': 'Email registrado correctamente. Revisa tu bandeja de entrada.',
            'nuevo': True,
            'email_enviado': email_enviado,
            'has_team_access': True,
        }


lead_service = LeadService()