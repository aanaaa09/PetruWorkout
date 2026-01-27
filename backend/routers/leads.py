from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from ..config.database import get_db
from ..models.usuario import Usuario, TipoUsuario
from ..crud.usuario import usuario_crud
from ..config.settings import settings
import requests
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lead", tags=["leads"])


class LeadRegistrationRequest(BaseModel):
    email: EmailStr


def enviar_email_bienvenida(email: str, nombre: str) -> bool:
    """
    Envía email de bienvenida usando Brevo (SendinBlue)
    BASADO EN EL CÓDIGO DE CONSULTAS QUE SÍ FUNCIONA
    """
    try:
        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "api-key": settings.EMAIL_API,
            "content-type": "application/json"
        }

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
            "htmlContent": f"""
                <!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
</head>
<body style="margin:0; padding:0; font-family: Arial, Helvetica, sans-serif; background-color:#ffffff; color:#333333;">

  <div style="max-width:600px; margin:0 auto; padding:20px;">

    <p style="font-size:15px; line-height:1.6; margin-bottom:15px;">
      Hola <strong>{nombre}</strong>,
    </p>

    <p style="font-size:15px; line-height:1.6; margin-bottom:15px;">
      Me alegro mucho de que hayas decidido dar el primer paso hacia tu transformación.
      A partir de ahora te iré enseñando cómo ponerte en forma con calistenia, sin complicarte.
    </p>

    <p style="font-size:15px; line-height:1.6; margin-bottom:20px;">
      Aquí tienes tu <strong>calculadora de calorías personalizada</strong>.
      Úsala para saber exactamente cuánto necesitas comer según tu objetivo.
    </p>

    <!-- Botón CTA -->
    <div style="margin:25px 0;">
      <a href="https://petrucalistenia.com/calculator"
         style="display:inline-block;
                background-color:#06d6a0;
                color:#ffffff;
                padding:12px 24px;
                text-decoration:none;
                border-radius:6px;
                font-size:15px;
                font-weight:bold;">
        Calcular mis calorías
      </a>
    </div>

    <p style="font-size:14px; line-height:1.6; color:#555555; margin-bottom:20px;">
      Cuando hayas hecho el cálculo, podrás unirte al grupo de WhatsApp donde comparto
      consejos, rutinas y respondo dudas.
    </p>

    <p style="font-size:15px; line-height:1.6; margin-top:25px;">
      Un abrazo,<br>
      <strong>Petru</strong><br>
      <span style="font-size:13px; color:#666666;">
        Entrenador Personal de Calistenia
      </span>
    </p>

    <hr style="border:none; border-top:1px solid #eeeeee; margin:30px 0;">

    <p style="font-size:12px; color:#999999; line-height:1.5;">
      Has recibido este email porque te registraste en PetruWorkout.<br>
      📧 petruworkout@gmail.com · 🌐 petrucalistenia.com
    </p>

  </div>

</body>
</html>

            """
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 201:
            logger.info(f"✅ Email de bienvenida enviado a {email}")
            return True
        else:
            logger.error(f"❌ Error enviando email con Brevo: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ Excepción enviando email con Brevo: {e}")
        return False


@router.post("/register")
def register_lead(data: LeadRegistrationRequest, db: Session = Depends(get_db)):
    """
    Registra un lead (email) para acceso al grupo de WhatsApp
    - Si el email ya existe: retorna success=True, nuevo=False (no envía email)
    - Si es nuevo: crea usuario, envía email de bienvenida, retorna success=True, nuevo=True
    """
    try:
        # Verificar si ya existe
        usuario_existente = usuario_crud.get_by_email(db, data.email.lower())

        if usuario_existente:
            logger.info(f"Lead ya existente: {data.email}")
            return {
                'success': True,
                'mensaje': 'Email ya registrado',
                'nuevo': False
            }

        # Crear nuevo usuario tipo NEWSLETTER sin contraseña
        # Generamos una contraseña temporal aleatoria que nunca se usará
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

        # ✅ ENVIAR EMAIL DE BIENVENIDA
        email_enviado = enviar_email_bienvenida(data.email.lower(), nombre)

        if email_enviado:
            logger.info(f"✅ Nuevo lead registrado con email de bienvenida: {data.email}")
        else:
            logger.warning(f"⚠️ Lead registrado pero email no enviado: {data.email}")

        return {
            'success': True,
            'mensaje': 'Email registrado correctamente. Revisa tu bandeja de entrada.',
            'nuevo': True,
            'email_enviado': email_enviado
        }

    except Exception as e:
        logger.error(f"❌ Error registrando lead {data.email}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error al registrar el email")