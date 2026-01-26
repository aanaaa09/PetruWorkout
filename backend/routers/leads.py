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
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>
                <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
                    <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">

                        <!-- Header -->
                        <div style="background: linear-gradient(135deg, #06d6a0 0%, #05b589 100%); padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">
                                🎉 ¡Bienvenido al Equipo!
                            </h1>
                            <p style="margin: 10px 0 0 0; color: rgba(255,255,255,0.9); font-size: 16px;">
                                Estás a punto de transformar tu vida
                            </p>
                        </div>

                        <!-- Contenido -->
                        <div style="padding: 30px;">
                            <p style="font-size: 16px; line-height: 1.6; color: #333333; margin: 0 0 15px 0;">
                                Hola <strong style="color: #06d6a0;">{nombre}</strong>,
                            </p>

                            <p style="font-size: 15px; line-height: 1.7; color: #666666; margin: 0 0 20px 0;">
                                ¡Me alegro mucho de que hayas decidido dar el primer paso hacia tu transformación! 
                                Has tomado una decisión que va a cambiar tu vida para siempre.
                            </p>

                            <!-- Beneficios -->
                            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #06d6a0; margin: 25px 0;">
                                <h2 style="margin: 0 0 15px 0; color: #06d6a0; font-size: 18px; font-weight: 600;">
                                    🎁 Tu regalo de bienvenida incluye:
                                </h2>
                                <ul style="margin: 0; padding-left: 20px; color: #333333;">
                                    <li style="margin-bottom: 10px; line-height: 1.5;">
                                        <strong>Calculadora de calorías personalizada</strong> - Calcula exactamente cuánto necesitas comer
                                    </li>
                                    <li style="margin-bottom: 10px; line-height: 1.5;">
                                        <strong>Acceso al grupo exclusivo de WhatsApp</strong> - Comunidad activa y motivadora
                                    </li>
                                    <li style="margin-bottom: 10px; line-height: 1.5;">
                                        <strong>Contenido premium semanal</strong> - Tips, rutinas y consejos exclusivos
                                    </li>
                                    <li style="line-height: 1.5;">
                                        <strong>Soporte directo</strong> - Yo personalmente respondo tus dudas
                                    </li>
                                </ul>
                            </div>

                            <!-- Botón CTA -->
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="https://chat.whatsapp.com/EPtwBr6DqUk0Y9kfUF0YB1" 
                                   style="display: inline-block; background: linear-gradient(135deg, #06d6a0 0%, #05b589 100%); color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(6, 214, 160, 0.3);">
                                    📲 UNIRME AL GRUPO AHORA
                                </a>
                            </div>

                            <!-- Nota importante -->
                            <div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 15px; margin: 20px 0;">
                                <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.6;">
                                    <strong>💡 Importante:</strong> Una vez dentro del grupo, recibirás tu calculadora de calorías 
                                    y toda la información necesaria para empezar tu transformación.
                                </p>
                            </div>

                            <!-- Despedida -->
                            <p style="font-size: 15px; line-height: 1.7; margin: 25px 0 0 0; color: #333333;">
                                ¡Nos vemos dentro del grupo! 💪
                            </p>

                            <p style="font-size: 15px; line-height: 1.7; margin: 10px 0 0 0; color: #06d6a0; font-weight: 600;">
                                Petru<br>
                                <span style="font-size: 13px; color: #666666; font-weight: 400;">
                                    Entrenador Personal Especializado en Calistenia
                                </span>
                            </p>
                        </div>

                        <!-- Footer -->
                        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0;">
                            <p style="margin: 0; color: #666666; font-size: 13px;">
                                PetruWorkout - Entrenador Personal de Calistenia
                            </p>
                            <p style="margin: 8px 0 0 0; color: #999999; font-size: 12px;">
                                📧 petruworkout@gmail.com | 🌐 <a href="https://petrucalistenia.com" style="color: #06d6a0; text-decoration: none;">petrucalistenia.com</a>
                            </p>
                            <p style="margin: 12px 0 0 0; color: #999999; font-size: 11px;">
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