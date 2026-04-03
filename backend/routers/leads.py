# backend/routers/leads.py
"""
Router de registro de leads.
El flujo de negocio (crear usuario, token, email) vive en lead_service.
El rate limiter se queda aquí porque es responsabilidad de la capa HTTP.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import logging
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict

from ..config.database import get_db
from ..services.lead_service import lead_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lead", tags=["leads"])


class LeadRegistrationRequest(BaseModel):
    email: EmailStr


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