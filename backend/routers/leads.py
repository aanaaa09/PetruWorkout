# backend/routers/leads.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
import html
import logging
import hashlib
import os
import re
import requests
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict

from ..config.database import get_db
from ..models.diagnostico_lead import DiagnosticoLead
from ..services.lead_service import lead_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lead", tags=["leads"])


class LeadRegistrationRequest(BaseModel):
    email: EmailStr

class DiagnosisRequest(BaseModel):
    # Límites generosos: evitan abusos sin rechazar nunca a un cliente real
    name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=5, max_length=40)
    age: str = Field(..., max_length=100)
    level: str = Field(..., max_length=300)
    goal: str = Field(..., max_length=300)
    block: str = Field(..., max_length=300)
    solution: str = Field(..., max_length=300)


# ── Rate limiter (responsabilidad HTTP, se queda en el router) ────

class RateLimiter:
    """
    Rate limiter basado en email.
    No usa IP porque en Railway/Vercel todos comparten la misma IP del proxy.
    """

    def __init__(self, max_requests: int = 2, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.email_requests: Dict[str, list] = defaultdict(list)

    def _clean_old_requests(self, cutoff: datetime):
        for key in list(self.email_requests.keys()):
            self.email_requests[key] = [t for t in self.email_requests[key] if t > cutoff]
            if not self.email_requests[key]:
                del self.email_requests[key]

    def is_allowed(self, email: str) -> bool:
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
        now = datetime.now()
        cutoff = now - timedelta(minutes=self.window_minutes)
        self._clean_old_requests(cutoff)
        if len(self.email_requests[email_hash]) >= self.max_requests:
            return False
        self.email_requests[email_hash].append(now)
        return True

    def remaining_minutes(self, email: str) -> int:
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
        if not self.email_requests.get(email_hash):
            return 0
        oldest = min(self.email_requests[email_hash])
        available_at = oldest + timedelta(minutes=self.window_minutes)
        remaining = available_at - datetime.now()
        return max(0, int(remaining.total_seconds() / 60))


rate_limiter = RateLimiter(max_requests=2, window_minutes=60)


# ── Endpoint ──────────────────────────────────────────────────────

@router.post("/register")
def register_lead(
    data: LeadRegistrationRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Registra un lead para acceso al grupo de WhatsApp.
    Rate limit: 2 intentos por email cada 60 minutos.
    """
    logger.info(f"Intento de registro: {data.email}")

    if not rate_limiter.is_allowed(data.email.lower()):
        remaining = rate_limiter.remaining_minutes(data.email.lower())
        logger.warning(f"Rate limit excedido: {data.email}")
        raise HTTPException(
            status_code=429,
            detail=f"Has intentado registrar este email demasiadas veces. Espera {remaining} minutos.",
        )

    try:
        return lead_service.register(db, data.email)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registrando lead {data.email}: {e}")
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error al registrar el email")


# ── Diagnóstico (formulario de la home) ───────────────────────────

TELEGRAM_TIMEOUT_SECONDS = 10


def _esc(value: str) -> str:
    """
    Escapa &, < y > para que Telegram (parse_mode=HTML) no rechace el mensaje
    cuando el visitante escribe símbolos raros en su nombre.
    """
    return html.escape(str(value).strip(), quote=False)


def _format_lead_message(data: DiagnosisRequest, html_mode: bool) -> str:
    """Texto del aviso. html_mode=False genera la versión en texto plano (reintento)."""
    clean_phone = re.sub(r"\D", "", data.phone)
    wa_link = f"https://wa.me/{clean_phone}"

    def b(label: str) -> str:
        return f"<b>{label}</b>" if html_mode else label

    def v(value: str) -> str:
        return _esc(value) if html_mode else str(value).strip()

    return (
        f"🚨 {b('NUEVO POTENCIAL CLIENTE')} 🚨\n\n"
        f"👤 {b('Nombre:')} {v(data.name)}\n"
        f"📱 {b('Teléfono:')} {v(data.phone)}\n"
        f"🎂 {b('Edad:')} {v(data.age)}\n\n"
        f"📊 {b('Nivel:')} {v(data.level)}\n"
        f"🎯 {b('Objetivo:')} {v(data.goal)}\n"
        f"🛑 {b('Freno:')} {v(data.block)}\n"
        f"⚡ {b('Compromiso:')} {v(data.solution)}\n\n"
        f"{wa_link}"
    )


def _safe_error(error: Exception, bot_token: str) -> str:
    """Texto del error sin el token del bot (la URL de Telegram lo contiene)."""
    text = str(error)
    if bot_token:
        text = text.replace(bot_token, "***")
    return text[:500]


def _send_telegram(bot_token: str, chat_id: str, data: DiagnosisRequest) -> None:
    """
    Envía el aviso a Telegram. Si Telegram no entiende el formato (error 400),
    reenvía el mismo contacto en texto plano para no perderlo.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    res = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": _format_lead_message(data, html_mode=True),
            "parse_mode": "HTML",
        },
        timeout=TELEGRAM_TIMEOUT_SECONDS,
    )
    if res.status_code == 400:
        logger.warning("Telegram rechazó el formato HTML; reenviando en texto plano")
        res = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": _format_lead_message(data, html_mode=False),
            },
            timeout=TELEGRAM_TIMEOUT_SECONDS,
        )
    res.raise_for_status()


def _mark_telegram_result(db: Session, lead, sent: bool, error: str = None) -> None:
    """Anota en la BD si el aviso por Telegram llegó o no. Nunca lanza errores."""
    if lead is None:
        return
    try:
        lead.telegram_enviado = sent
        lead.telegram_error = error
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"No se pudo actualizar el estado de Telegram del contacto: {e}")


@router.post("/diagnosis")
def process_diagnosis(data: DiagnosisRequest, db: Session = Depends(get_db)):
    """
    Guarda el contacto del diagnóstico y avisa por Telegram.

    El contacto se guarda SIEMPRE primero: si Telegram falla o no está
    configurado, el contacto sigue en la tabla diagnostico_leads.
    """
    lead = None
    try:
        lead = DiagnosticoLead(
            nombre=data.name.strip(),
            telefono=data.phone.strip(),
            edad=data.age.strip(),
            nivel=data.level.strip(),
            objetivo=data.goal.strip(),
            freno=data.block.strip(),
            compromiso=data.solution.strip(),
        )
        db.add(lead)
        db.commit()
    except Exception as e:
        db.rollback()
        lead = None
        logger.error(f"No se pudo guardar el contacto en la BD: {e}")

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logger.error("Faltan las credenciales de Telegram: contacto guardado pero SIN avisar")
        _mark_telegram_result(db, lead, False, "Faltan las credenciales de Telegram")
        if lead is None:
            raise HTTPException(status_code=500, detail="Error al procesar el diagnóstico")
        return {"status": "success", "message": "Datos guardados (no enviados a Telegram por falta de credenciales)"}

    try:
        _send_telegram(bot_token, chat_id, data)
    except Exception as e:
        error = _safe_error(e, bot_token)
        logger.error(f"Error enviando mensaje a Telegram: {error}")
        _mark_telegram_result(db, lead, False, error)
        if lead is None:
            # Ni BD ni Telegram: aquí sí avisamos del fallo para que el contacto no se dé por recibido
            raise HTTPException(status_code=500, detail="Error al procesar el diagnóstico")
        return {"status": "success", "message": "Datos guardados (el aviso por Telegram falló)"}

    _mark_telegram_result(db, lead, True, None)
    return {"status": "success"}