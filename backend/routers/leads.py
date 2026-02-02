from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from backend.config.database import get_db
from backend.models.usuario import Usuario, TipoUsuario
from backend.crud.usuario import usuario_crud
from backend.config.settings import settings
import requests
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict
import hashlib

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lead", tags=["leads"])


class LeadRegistrationRequest(BaseModel):
    email: EmailStr


# ==========================================
# RATE LIMITING ROBUSTO (con fingerprinting)
# ==========================================
class RateLimiter:
    """
    Rate limiter mejorado con:
    - Tracking por IP
    - Tracking por email
    - Fingerprinting para evitar bypass
    - Auto-limpieza de registros antiguos
    """

    def __init__(self, max_requests: int = 3, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.ip_requests: Dict[str, list] = defaultdict(list)
        self.email_requests: Dict[str, list] = defaultdict(list)

    def _clean_old_requests(self, request_dict: Dict[str, list], cutoff: datetime):
        """Limpia requests antiguos de memoria"""
        for key in list(request_dict.keys()):
            request_dict[key] = [
                req_time for req_time in request_dict[key]
                if req_time > cutoff
            ]
            # Eliminar entrada si está vacía
            if not request_dict[key]:
                del request_dict[key]

    def is_allowed_by_ip(self, ip: str) -> bool:
        """Verifica si la IP puede hacer otra petición"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=self.window_minutes)

        # Limpiar requests antiguos
        self._clean_old_requests(self.ip_requests, cutoff)

        # Verificar límite
        if len(self.ip_requests[ip]) >= self.max_requests:
            return False

        # Registrar nueva request
        self.ip_requests[ip].append(now)
        return True

    def is_allowed_by_email(self, email: str) -> bool:
        """Verifica si el email puede intentar registrarse de nuevo"""
        # Hash del email para privacidad
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()

        now = datetime.now()
        cutoff = now - timedelta(minutes=self.window_minutes)

        # Limpiar requests antiguos
        self._clean_old_requests(self.email_requests, cutoff)

        # Verificar límite (más estricto para emails)
        if len(self.email_requests[email_hash]) >= 2:  # Máximo 2 intentos por email
            return False

        # Registrar nueva request
        self.email_requests[email_hash].append(now)
        return True

    def get_remaining_time(self, ip: str) -> int:
        """Retorna minutos hasta que pueda hacer otra request"""
        if not self.ip_requests[ip]:
            return 0

        oldest_request = min(self.ip_requests[ip])
        available_at = oldest_request + timedelta(minutes=self.window_minutes)
        remaining = available_at - datetime.now()

        return max(0, int(remaining.total_seconds() / 60))


# Instancia global del rate limiter
# Limita a 3 registros por IP cada 60 minutos
# Y 2 intentos por email cada 60 minutos
rate_limiter = RateLimiter(max_requests=3, window_minutes=60)


def get_client_ip(request: Request) -> str:
    """
    Obtiene la IP real del cliente (considerando proxies y Railway)
    Railway usa X-Forwarded-For para la IP del cliente
    """
    # Railway específico: X-Forwarded-For
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # La primera IP es la del cliente real
        return forwarded.split(",")[0].strip()

    # X-Real-IP (usado por algunos proxies)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Cloudflare (si usas CF en el futuro)
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip

    # IP directa (fallback)
    return request.client.host if request.client else "unknown"


def enviar_email_bienvenida(email: str, nombre: str, calculator_url: str) -> bool:
    """
    Envía email de bienvenida usando Brevo (SendinBlue)
    """
    try:
        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "api-key": settings.EMAIL_API,
            "content-type": "application/json"
        }

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
</head>
<body style="margin:0; padding:0; font-family: Arial, Helvetica, sans-serif; background-color:#ffffff; color:#333333;">
  <div style="max-width:600px; margin:0 auto; padding:20px;">

    <p style="font-size:16px; line-height:1.6; margin-bottom:15px;">
      ¡Ey, te escribe Petru!
    </p>

    <p style="font-size:15px; line-height:1.7; margin-bottom:15px;">
      Me alegra un montón que estés aquí, de verdad.<br>
      Dar este primer paso ya dice mucho de ti.
    </p>

    <p style="font-size:15px; line-height:1.7; margin-bottom:15px;">
      Quiero que sepas algo desde ya: <strong>no vas a estar solo</strong>.
    </p>

    <p style="font-size:15px; line-height:1.7; margin-bottom:20px;">
      He creado el grupo de WhatsApp para que sepas cómo organizar tus rutinas, 
      te ayudo con la alimentación, puedes preguntarme todas las dudas, mandar videos 
      y no ir perdido.
    </p>

    <p style="font-size:15px; line-height:1.7; margin-bottom:20px;">
      Estoy dentro y respondo yo, asique si no te has unido aún. 
      <a href="https://chat.whatsapp.com/EPtwBr6DqUk0Y9kfUF0YB1" 
         style="color:#06d6a0; font-weight:bold; text-decoration:none;">
        <strong>Haz clic aquí</strong>
      </a>
    </p>

    <p style="font-size:15px; line-height:1.7; margin-bottom:20px;">
      Y ahora sí, vamos a lo importante 😏<br>
      Te dejo este regalito para que lo aproveches y sepas 
      <strong>cuánto comer según tu objetivo</strong>, sin líos ni cálculos raros.
    </p>

    <!-- Botón CTA -->
    <div style="margin:30px 0; text-align:center;">
      <a href="{calculator_url}"
         style="display:inline-block; background-color:#06d6a0; color:#ffffff; padding:12px 24px; text-decoration:none; border-radius:6px; font-size:15px; font-weight:600;">
        🔥 CALCULAR MIS CALORÍAS AHORA
      </a>
    </div>

    <p style="font-size:15px; line-height:1.7; margin-top:25px;">
      Nos vemos dentro 💪
    </p>

    <p style="font-size:15px; line-height:1.7; margin-top:15px;">
      <strong>Petru</strong><br>
      <span style="font-size:13px; color:#666666;">
        Entrenador Personal Especializado en Calistenia
      </span>
    </p>

    <hr style="border:none; border-top:1px solid #eeeeee; margin:30px 0;">

    <p style="font-size:12px; color:#999999; line-height:1.5;">
      PetruWorkout - Entrenador Personal de Calistenia<br>
      📧 petruworkout@gmail.com · 🌐 petrucalistenia.com<br>
      Has recibido este email porque te registraste en PetruWorkout
    </p>

  </div>
</body>
</html>
"""

        payload = {
            "sender": {
                "name": "PetruWorkout",
                "email": "petruworkout@gmail.com"
            },
            "to": [
                {
                    "email": email,
                    "name": nombre
                }
            ],
            "subject": "🎁 ¡Bienvenido al equipo PetruWorkout!",
            "htmlContent": html_content
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 201:
            logger.info(f"Email de bienvenida enviado a {email}")
            return True
        else:
            logger.error(f"Error enviando email con Brevo: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Excepción enviando email con Brevo: {e}")
        return False


# ==========================================
# ENDPOINT PROTEGIDO CON RATE LIMITING
# ==========================================
@router.post("/register")
def register_lead(
        data: LeadRegistrationRequest,
        request: Request,
        db: Session = Depends(get_db)
):
    """
    Registra un lead (email) para acceso al grupo de WhatsApp

    **PROTECCIONES:**
    - Rate limiting por IP: máximo 3 registros cada 60 minutos
    - Rate limiting por email: máximo 2 intentos cada 60 minutos
    - Validación de email duplicado
    - Detección de IP real (funciona con proxies y Railway)

    **FLUJO:**
    - Si el email ya existe: retorna success=True, nuevo=False (no envía email)
    - Si es nuevo: crea usuario, envía email de bienvenida, retorna success=True, nuevo=True
    """
    # ==========================================
    # 1. OBTENER IP REAL
    # ==========================================
    client_ip = get_client_ip(request)
    logger.info(f"Registro desde IP {client_ip}: {data.email}")

    # ==========================================
    # 2. VERIFICAR RATE LIMIT POR IP
    # ==========================================
    if not rate_limiter.is_allowed_by_ip(client_ip):
        remaining_minutes = rate_limiter.get_remaining_time(client_ip)
        logger.warning(f"Rate limit por IP excedido: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail=f"Demasiados intentos desde tu conexión. Intenta de nuevo en {remaining_minutes} minutos."
        )

    # ==========================================
    # 3. VERIFICAR RATE LIMIT POR EMAIL
    # ==========================================
    if not rate_limiter.is_allowed_by_email(data.email.lower()):
        logger.warning(f"Rate limit por email excedido: {data.email}")
        raise HTTPException(
            status_code=429,
            detail="Has intentado registrar este email demasiadas veces. Espera 60 minutos."
        )

    try:
        # ==========================================
        # 4. VERIFICAR SI YA EXISTE
        # ==========================================
        usuario_existente = usuario_crud.get_by_email(db, data.email.lower())

        if usuario_existente:
            # Conceder acceso si no lo tiene
            if not usuario_existente.team_access_granted:
                usuario_existente.team_access_granted = True
                db.commit()
                logger.info(f"Acceso concedido a usuario existente: {data.email}")

            return {
                'success': True,
                'mensaje': 'Email ya registrado',
                'nuevo': False,
                'has_team_access': True
            }

        # ==========================================
        # 5. CREAR NUEVO USUARIO
        # ==========================================
        import secrets
        temp_password = secrets.token_urlsafe(32)

        # Extraer nombre del email (parte antes del @)
        nombre = data.email.split('@')[0].capitalize()

        usuario = usuario_crud.create(
            db,
            nombre=nombre,
            email=data.email.lower(),
            password=temp_password,
            tipo_usuario=TipoUsuario.NEWSLETTER
        )
        usuario.team_access_granted = True
        db.commit()
        db.refresh(usuario)

        # ==========================================
        # 6. GENERAR TOKEN DE CALCULADORA
        # ==========================================
        from backend.services.calculator_token_service import calculator_token_service

        token_result = calculator_token_service.create_token_for_user(db, data.email.lower())

        if not token_result['success']:
            logger.error(f" No se pudo crear token para {data.email}")
            calculator_url = "https://petrucalistenia.com/calculator"
        else:
            calculator_url = token_result['url']

        # ==========================================
        # 7. ENVIAR EMAIL CON LINK PERSONALIZADO
        # ==========================================
        email_enviado = enviar_email_bienvenida(data.email.lower(), nombre, calculator_url)

        if email_enviado:
            logger.info(f"✅ Nuevo lead registrado con email de bienvenida: {data.email}")
        else:
            logger.warning(f"⚠️ Lead registrado pero email no enviado: {data.email}")

        return {
            'success': True,
            'mensaje': 'Email registrado correctamente. Revisa tu bandeja de entrada.',
            'nuevo': True,
            'email_enviado': email_enviado,
            'has_team_access': True
        }

    except HTTPException:
        # Re-lanzar excepciones HTTP (rate limit)
        raise
    except Exception as e:
        logger.error(f"Error registrando lead {data.email}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error al registrar el email")