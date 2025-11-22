from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from ..config.database import get_db
from ..models.consulta import Consulta
import requests
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/consultas", tags=["consultas"])


class EnviarConsultaRequest(BaseModel):
    nombre: str
    email: EmailStr
    asunto: str
    mensaje: str


@router.post("/enviar")
def enviar_consulta(data: EnviarConsultaRequest, db: Session = Depends(get_db)):
    """Envía una consulta/duda desde el formulario de contacto"""
    try:
        # Guardar en BD
        consulta = Consulta(
            nombre=data.nombre,
            email=data.email,
            asunto=data.asunto,
            mensaje=data.mensaje
        )
        db.add(consulta)
        db.commit()

        # Enviar email a Petru usando Brevo
        resultado = enviar_email_brevo(data)

        if not resultado:
            logger.warning("Email guardado en BD pero no se pudo enviar por Brevo")

        return {
            'success': True,
            'mensaje': 'Consulta enviada correctamente'
        }

    except Exception as e:
        logger.error(f"Error enviando consulta: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al enviar la consulta")


def enviar_email_brevo(data: EnviarConsultaRequest) -> bool:
    """
    Envía email a Petru usando la API de Brevo (SendinBlue)
    El remitente será el email del usuario
    """
    try:
        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "api-key": settings.EMAIL_API,
            "content-type": "application/json"
        }

        # El email viene desde el usuario que rellena el formulario
        payload = {
            "sender": {
                "name": data.nombre,
                "email": data.email
            },
            "to": [
                {
                    "email": "petruworkout@gmail.com",
                    "name": "Petru"
                }
            ],
            "subject": f"📬 Nueva consulta: {data.asunto}",
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
                        <div style="background: linear-gradient(135deg, #e63946 0%, #d62828 100%); padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">
                                💬 Nueva Consulta
                            </h1>
                            <p style="margin: 10px 0 0 0; color: rgba(255,255,255,0.9); font-size: 16px;">
                                PetruWorkout
                            </p>
                        </div>

                        <!-- Contenido -->
                        <div style="padding: 30px;">
                            <!-- Información del remitente -->
                            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #e63946; margin-bottom: 25px;">
                                <h2 style="margin: 0 0 15px 0; color: #333333; font-size: 18px; font-weight: 600;">
                                    📋 Información del contacto
                                </h2>
                                <table style="width: 100%; border-collapse: collapse;">
                                    <tr>
                                        <td style="padding: 8px 0; color: #666666; font-weight: 600; width: 100px;">Nombre:</td>
                                        <td style="padding: 8px 0; color: #333333;">{data.nombre}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px 0; color: #666666; font-weight: 600;">Email:</td>
                                        <td style="padding: 8px 0;">
                                            <a href="mailto:{data.email}" style="color: #e63946; text-decoration: none;">
                                                {data.email}
                                            </a>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px 0; color: #666666; font-weight: 600;">Asunto:</td>
                                        <td style="padding: 8px 0; color: #333333; font-weight: 600;">{data.asunto}</td>
                                    </tr>
                                </table>
                            </div>

                            <!-- Mensaje -->
                            <div style="margin-bottom: 25px;">
                                <h2 style="margin: 0 0 15px 0; color: #333333; font-size: 18px; font-weight: 600;">
                                    📝 Mensaje
                                </h2>
                                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; line-height: 1.6; color: #333333; white-space: pre-wrap; font-size: 15px;">
{data.mensaje}
                                </div>
                            </div>

                            <!-- Botón de respuesta -->
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="mailto:{data.email}?subject=Re: {data.asunto}" 
                                   style="display: inline-block; background: linear-gradient(135deg, #e63946 0%, #d62828 100%); color: #ffffff; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(230, 57, 70, 0.3);">
                                    ↩️ Responder a {data.nombre}
                                </a>
                            </div>
                        </div>

                        <!-- Footer -->
                        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0;">
                            <p style="margin: 0; color: #666666; font-size: 13px;">
                                Este mensaje fue enviado desde el formulario de contacto de 
                                <strong style="color: #e63946;">PetruWorkout.com</strong>
                            </p>
                            <p style="margin: 8px 0 0 0; color: #999999; font-size: 12px;">
                                Puedes responder directamente a este email para contactar con {data.nombre}
                            </p>
                        </div>
                    </div>
                </body>
                </html>
            """
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 201:
            logger.info(f"✅ Email enviado correctamente a Petru desde {data.email}")
            return True
        else:
            logger.error(f"❌ Error enviando email con Brevo: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ Excepción enviando email con Brevo: {e}")
        return False