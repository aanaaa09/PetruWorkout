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
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>
                <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d0d0d;">
                    <div style="max-width: 600px; margin: 20px auto; background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%); border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);">
                        <!-- Header -->
                        <div style="background: linear-gradient(135deg, #06d6a0 0%, #05b589 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 900; letter-spacing: -0.5px;">
                                🎉 ¡BIENVENIDO AL EQUIPO!
                            </h1>
                            <p style="margin: 15px 0 0 0; color: rgba(255,255,255,0.95); font-size: 18px; font-weight: 600;">
                                Estás a punto de transformar tu vida
                            </p>
                        </div>

                        <!-- Contenido -->
                        <div style="padding: 40px 30px; color: #edf2f4;">
                            <p style="font-size: 18px; line-height: 1.6; margin: 0 0 20px 0;">
                                Hola <strong style="color: #06d6a0;">{nombre}</strong>,
                            </p>

                            <p style="font-size: 16px; line-height: 1.7; margin: 0 0 25px 0; color: #8d99ae;">
                                ¡Me alegro mucho de que hayas decidido dar el primer paso hacia tu transformación! 
                                Has tomado una decisión que va a cambiar tu vida para siempre.
                            </p>

                            <!-- Beneficios -->
                            <div style="background: rgba(6, 214, 160, 0.1); border-left: 4px solid #06d6a0; padding: 25px; border-radius: 12px; margin: 30px 0;">
                                <h2 style="margin: 0 0 20px 0; color: #06d6a0; font-size: 20px; font-weight: 700;">
                                    🎁 Tu regalo de bienvenida incluye:
                                </h2>
                                <ul style="margin: 0; padding-left: 20px; color: #edf2f4;">
                                    <li style="margin-bottom: 12px; line-height: 1.6;">
                                        <strong>Calculadora de calorías personalizada</strong> - Calcula exactamente cuánto necesitas comer
                                    </li>
                                    <li style="margin-bottom: 12px; line-height: 1.6;">
                                        <strong>Acceso al grupo exclusivo de WhatsApp</strong> - Comunidad activa y motivadora
                                    </li>
                                    <li style="margin-bottom: 12px; line-height: 1.6;">
                                        <strong>Contenido premium semanal</strong> - Tips, rutinas y consejos exclusivos
                                    </li>
                                    <li style="line-height: 1.6;">
                                        <strong>Soporte directo</strong> - Yo personalmente respondo tus dudas
                                    </li>
                                </ul>
                            </div>

                            <!-- CTA Button -->
                            <div style="text-align: center; margin: 35px 0;">
                                <a href="https://petrucalistenia.com/team" 
                                   style="display: inline-block; background: linear-gradient(135deg, #06d6a0 0%, #05b589 100%); color: white; padding: 18px 40px; text-decoration: none; border-radius: 12px; font-weight: 700; font-size: 18px; box-shadow: 0 8px 30px rgba(6, 214, 160, 0.4);">
                                    📲 UNIRME AL GRUPO AHORA
                                </a>
                            </div>

                            <!-- Nota importante -->
                            <div style="background: rgba(255, 193, 7, 0.15); border: 1px solid rgba(255, 193, 7, 0.3); border-radius: 12px; padding: 20px; margin: 30px 0;">
                                <p style="margin: 0; color: #ffd60a; font-size: 14px; line-height: 1.6;">
                                    <strong>💡 Importante:</strong> Una vez dentro del grupo, recibirás tu calculadora de calorías 
                                    y toda la información necesaria para empezar tu transformación.
                                </p>
                            </div>

                            <!-- Despedida -->
                            <p style="font-size: 16px; line-height: 1.7; margin: 30px 0 0 0; color: #edf2f4;">
                                ¡Nos vemos dentro del grupo! 💪
                            </p>

                            <p style="font-size: 16px; line-height: 1.7; margin: 10px 0 0 0; color: #06d6a0; font-weight: 700;">
                                Petru<br>
                                <span style="font-size: 14px; color: #8d99ae; font-weight: 400;">
                                    Entrenador Personal Especializado en Calistenia
                                </span>
                            </p>
                        </div>

                        <!-- Footer -->
                        <div style="background: rgba(0, 0, 0, 0.3); padding: 25px 30px; text-align: center; border-top: 1px solid rgba(255, 255, 255, 0.05);">
                            <p style="margin: 0 0 10px 0; color: #8d99ae; font-size: 13px;">
                                PetruWorkout - Entrenador Personal de Calistenia
                            </p>
                            <p style="margin: 0; color: #666; font-size: 12px;">
                                📧 petruworkout@gmail.com | 🌐 <a href="https://petrucalistenia.com" style="color: #06d6a0; text-decoration: none;">petrucalistenia.com</a>
                            </p>
                            <p style="margin: 15px 0 0 0; color: #666; font-size: 11px;">
                                Has recibido este email porque te registraste en PetruWorkout
                            </p>
                        </div>
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

        # Enviar email de bienvenida
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
        raise HTTPException(status_code=500, detail="Error al registrar el email")