# backend/services/email_service.py
"""
Servicio de envío de emails usando Brevo (SendinBlue)
Con soporte para adjuntos (PDF, imágenes, etc)
"""

import requests
import base64
import logging
from typing import List, Optional, Dict
from ..config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para envío de emails usando Brevo"""

    BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

    def __init__(self):
        self.api_key = settings.EMAIL_API
        self.sender_email = "petruworkout@gmail.com"
        self.sender_name = "PetruWorkout"

    async def send_newsletter_email(
            self,
            to_email: str,
            to_name: str,
            subject: str,
            message: str,
            attachments: Optional[List[Dict]] = None
    ) -> bool:
        """
        Envía un email de newsletter con opcional adjuntos

        Args:
            to_email: Email del destinatario
            to_name: Nombre del destinatario
            subject: Asunto del email
            message: Mensaje (puede incluir HTML)
            attachments: Lista de dicts con 'content' (bytes) y 'name' (str)

        Returns:
            bool: True si se envió correctamente
        """
        try:
            headers = {
                "accept": "application/json",
                "api-key": self.api_key,
                "content-type": "application/json"
            }

            # Convertir mensaje a HTML si no lo es
            if not message.strip().startswith('<'):
                # Convertir saltos de línea a <br>
                html_message = message.replace('\n', '<br>')
                html_content = f"""
                <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color:#f4f4f4;">
    <div style="max-width:600px; margin:20px auto; background:#ffffff; border-radius:10px; overflow:hidden; box-shadow:0 4px 6px rgba(0,0,0,0.1);">

        <!-- Contenido -->
        <div style="padding:40px 30px;">
            <div style="color:#333333; font-size:15px; line-height:1.7;">
                {html_message}
            </div>
        </div>

        <!-- Footer -->
        <div style="background:#f8f9fa; padding:20px 30px; text-align:center; border-top:1px solid #e0e0e0;">
            <p style="margin:0 0 10px 0; color:#666666; font-size:13px;">
                Este mensaje fue enviado desde <strong style="color:#06d6a0;">PetruWorkout</strong>
            </p>
            <p style="margin:0; color:#999999; font-size:12px;">
                📧 petruworkout@gmail.com · 🌐 petrucalistenia.com
            </p>
        </div>
    </div>
</body>
</html>

                """
            else:
                html_content = message

            # Payload base
            payload = {
                "sender": {
                    "name": self.sender_name,
                    "email": self.sender_email
                },
                "to": [
                    {
                        "email": to_email,
                        "name": to_name
                    }
                ],
                "subject": subject,
                "htmlContent": html_content
            }

            # Añadir adjuntos si existen
            if attachments:
                attachment_list = []
                for attach in attachments:
                    # Convertir bytes a base64
                    content_b64 = base64.b64encode(attach['content']).decode('utf-8')

                    attachment_list.append({
                        "content": content_b64,
                        "name": attach['name']
                    })

                payload["attachment"] = attachment_list
                logger.info(f"📎 Añadiendo {len(attachment_list)} adjuntos al email")

            # Enviar
            response = requests.post(
                self.BREVO_API_URL,
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code == 201:
                logger.info(f"Email enviado a {to_email}")
                return True
            else:
                logger.error(f"Error enviando email a {to_email}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Excepción enviando email a {to_email}: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def send_plain_email(
            self,
            to_email: str,
            to_name: str,
            subject: str,
            html_content: str
    ) -> bool:
        """
        Envía un email simple sin template
        """
        try:
            headers = {
                "accept": "application/json",
                "api-key": self.api_key,
                "content-type": "application/json"
            }

            payload = {
                "sender": {
                    "name": self.sender_name,
                    "email": self.sender_email
                },
                "to": [{"email": to_email, "name": to_name}],
                "subject": subject,
                "htmlContent": html_content
            }

            response = requests.post(
                self.BREVO_API_URL,
                json=payload,
                headers=headers,
                timeout=10
            )

            return response.status_code == 201

        except Exception as e:
            logger.error(f"Error enviando email plain: {e}")
            return False


# Instancia global
email_service = EmailService()