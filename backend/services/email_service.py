# backend/services/email_service.py
"""
Servicio de envío de emails usando Brevo (SendinBlue).
Con soporte para adjuntos (PDF, imágenes, etc).
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

    # ──────────────────────────────────────────────────────────
    # PRIVADO: envío base contra la API de Brevo
    # ──────────────────────────────────────────────────────────

    def _send(self, payload: dict) -> bool:
        """Envía el payload JSON a Brevo y devuelve True si fue 201."""
        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json",
        }
        try:
            response = requests.post(self.BREVO_API_URL, json=payload, headers=headers, timeout=10)
            if response.status_code == 201:
                return True
            logger.error(f"Brevo error {response.status_code}: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Excepción enviando email: {e}")
            return False

    # ──────────────────────────────────────────────────────────
    # NEWSLETTER con adjuntos opcionales
    # ──────────────────────────────────────────────────────────

    async def send_newsletter_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        message: str,
        attachments: Optional[List[Dict]] = None,
    ) -> bool:
        """
        Envía un email de newsletter con adjuntos opcionales.

        Args:
            attachments: Lista de dicts con 'content' (bytes) y 'name' (str).
        """
        # Convertir texto plano a HTML si hace falta
        if not message.strip().startswith('<'):
            html_message = message.replace('\n', '<br>')
            html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;background-color:#f4f4f4;">
  <div style="max-width:600px;margin:20px auto;background:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
    <div style="padding:40px 30px;">
      <div style="color:#333333;font-size:15px;line-height:1.7;">{html_message}</div>
    </div>
    <div style="background:#f8f9fa;padding:20px 30px;text-align:center;border-top:1px solid #e0e0e0;">
      <p style="margin:0 0 10px 0;color:#666666;font-size:13px;">
        Este mensaje fue enviado desde <strong style="color:#06d6a0;">PetruWorkout</strong>
      </p>
      <p style="margin:0;color:#999999;font-size:12px;">
        📧 petruworkout@gmail.com · 🌐 petrucalistenia.com
      </p>
    </div>
  </div>
</body>
</html>"""
        else:
            html_content = message

        payload = {
            "sender":      {"name": self.sender_name, "email": self.sender_email},
            "to":          [{"email": to_email, "name": to_name}],
            "subject":     subject,
            "htmlContent": html_content,
        }

        if attachments:
            payload["attachment"] = [
                {
                    "content": base64.b64encode(a['content']).decode('utf-8'),
                    "name":    a['name'],
                }
                for a in attachments
            ]
            logger.info(f"📎 {len(attachments)} adjuntos añadidos")

        return self._send(payload)

    # ──────────────────────────────────────────────────────────
    # EMAIL SIMPLE (sin template)
    # ──────────────────────────────────────────────────────────

    async def send_plain_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
    ) -> bool:
        payload = {
            "sender":      {"name": self.sender_name, "email": self.sender_email},
            "to":          [{"email": to_email, "name": to_name}],
            "subject":     subject,
            "htmlContent": html_content,
        }
        return self._send(payload)

    # ──────────────────────────────────────────────────────────
    # EMAIL DE BIENVENIDA PARA LEADS (antes función suelta en leads.py)
    # ──────────────────────────────────────────────────────────

    async def send_welcome_lead_email(
        self,
        to_email: str,
        to_name: str,
        calculator_url: str,
    ) -> bool:
        """
        Email de bienvenida que se envía al registrar un nuevo lead.
        Incluye enlace al grupo de WhatsApp y a la calculadora personalizada.
        """
        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;font-family:Arial,Helvetica,sans-serif;background-color:#ffffff;color:#333333;">
  <div style="max-width:600px;margin:0 auto;padding:20px;">

    <p style="font-size:16px;line-height:1.6;margin-bottom:15px;">¡Ey, te escribe Petru!</p>

    <p style="font-size:15px;line-height:1.7;margin-bottom:15px;">
      Me alegra un montón que estés aquí, de verdad.<br>
      Dar este primer paso ya dice mucho de ti.
    </p>

    <p style="font-size:15px;line-height:1.7;margin-bottom:15px;">
      Quiero que sepas algo desde ya: <strong>no vas a estar solo</strong>.
    </p>

    <p style="font-size:15px;line-height:1.7;margin-bottom:20px;">
      He creado el grupo de WhatsApp para que sepas cómo organizar tus rutinas,
      te ayudo con la alimentación, puedes preguntarme todas las dudas, mandar videos
      y no ir perdido.
    </p>

    <p style="font-size:15px;line-height:1.7;margin-bottom:20px;">
      Estoy dentro y respondo yo, asique si no te has unido aún.
      <a href="https://chat.whatsapp.com/EPtwBr6DqUk0Y9kfUF0YB1"
         style="color:#06d6a0;font-weight:bold;text-decoration:none;">
        <strong>Haz clic aquí</strong>
      </a>
    </p>

    <p style="font-size:15px;line-height:1.7;margin-bottom:20px;">
      Y ahora sí, vamos a lo importante 😏<br>
      Te dejo este regalito para que lo aproveches y sepas
      <strong>cuánto comer según tu objetivo</strong>, sin líos ni cálculos raros.
    </p>

    <div style="margin:30px 0;text-align:center;">
      <a href="{calculator_url}"
         style="display:inline-block;background-color:#06d6a0;color:#ffffff;padding:12px 24px;text-decoration:none;border-radius:6px;font-size:15px;font-weight:600;">
        🔥 CALCULAR MIS CALORÍAS AHORA
      </a>
    </div>

    <p style="font-size:15px;line-height:1.7;margin-top:25px;">Nos vemos dentro 💪</p>

    <p style="font-size:15px;line-height:1.7;margin-top:15px;">
      <strong>Petru</strong><br>
      <span style="font-size:13px;color:#666666;">Entrenador Personal Especializado en Calistenia</span>
    </p>

    <hr style="border:none;border-top:1px solid #eeeeee;margin:30px 0;">

    <p style="font-size:12px;color:#999999;line-height:1.5;">
      PetruWorkout - Entrenador Personal de Calistenia<br>
      📧 petruworkout@gmail.com · 🌐 petrucalistenia.com<br>
      Has recibido este email porque te registraste en PetruWorkout
    </p>

  </div>
</body>
</html>"""

        payload = {
            "sender": {"name": "PetruWorkout", "email": self.sender_email},
            "to":     [{"email": to_email, "name": to_name}],
            "subject": "🎁 ¡Bienvenido al equipo PetruWorkout!",
            "htmlContent": html_content,
        }

        result = self._send(payload)
        if result:
            logger.info(f"Email de bienvenida enviado a {to_email}")
        else:
            logger.error(f"Error enviando email de bienvenida a {to_email}")
        return result

    # ──────────────────────────────────────────────────────────
    # EMAIL DE CONSULTA A PETRU (antes función suelta en consultas.py)
    # ──────────────────────────────────────────────────────────

    def send_consulta_email(
        self,
        nombre: str,
        email: str,
        asunto: str,
        mensaje: str,
    ) -> bool:
        """
        Notifica a Petru cuando llega una consulta del formulario de contacto.
        El replyTo apunta al email del usuario para que Petru pueda responder directamente.
        """
        payload = {
            "sender":  {"name": "PetruWorkout Bot", "email": self.sender_email},
            "replyTo": {"email": email, "name": nombre},
            "to":      [{"email": "petruworkout@gmail.com", "name": "Petru"}],
            "subject": f"📬 Nueva consulta de {nombre}: {asunto}",
            "htmlContent": f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background-color:#f4f4f4;">
  <div style="max-width:600px;margin:20px auto;background-color:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
    <div style="background:linear-gradient(135deg,#e63946 0%,#d62828 100%);padding:30px;text-align:center;">
      <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:700;">🤖 PetruWorkout Bot</h1>
      <p style="margin:10px 0 0 0;color:rgba(255,255,255,0.9);font-size:16px;">Nueva consulta desde el formulario web</p>
    </div>
    <div style="padding:30px;">
      <div style="background-color:#f8f9fa;padding:20px;border-radius:8px;border-left:4px solid #e63946;margin-bottom:25px;">
        <h2 style="margin:0 0 15px 0;color:#333333;font-size:18px;font-weight:600;">👤 Datos del contacto</h2>
        <table style="width:100%;border-collapse:collapse;">
          <tr>
            <td style="padding:8px 0;color:#666666;font-weight:600;width:100px;">Nombre:</td>
            <td style="padding:8px 0;color:#333333;">{nombre}</td>
          </tr>
          <tr>
            <td style="padding:8px 0;color:#666666;font-weight:600;">Email:</td>
            <td style="padding:8px 0;">
              <a href="mailto:{email}" style="color:#e63946;text-decoration:none;">{email}</a>
            </td>
          </tr>
          <tr>
            <td style="padding:8px 0;color:#666666;font-weight:600;">Asunto:</td>
            <td style="padding:8px 0;color:#333333;font-weight:600;">{asunto}</td>
          </tr>
        </table>
      </div>
      <div style="margin-bottom:25px;">
        <h2 style="margin:0 0 15px 0;color:#333333;font-size:18px;font-weight:600;">💬 Mensaje</h2>
        <div style="background-color:#f8f9fa;padding:20px;border-radius:8px;line-height:1.6;color:#333333;white-space:pre-wrap;font-size:15px;">{mensaje}</div>
      </div>
      <div style="text-align:center;margin:30px 0;">
        <a href="mailto:{email}?subject=Re: {asunto}"
           style="display:inline-block;background:linear-gradient(135deg,#e63946 0%,#d62828 100%);color:#ffffff;padding:14px 32px;text-decoration:none;border-radius:8px;font-weight:600;font-size:16px;box-shadow:0 4px 12px rgba(230,57,70,0.3);">
          ↩️ Responder a {nombre}
        </a>
      </div>
      <div style="background-color:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:15px;margin-top:20px;">
        <p style="margin:0;color:#856404;font-size:14px;">
          💡 <strong>Tip:</strong> Puedes responder directamente a este email,
          tu respuesta llegará automáticamente a <strong>{email}</strong>
        </p>
      </div>
    </div>
    <div style="background-color:#f8f9fa;padding:20px;text-align:center;border-top:1px solid #e0e0e0;">
      <p style="margin:0;color:#666666;font-size:13px;">
        Este mensaje fue enviado desde el formulario de contacto de
        <strong style="color:#e63946;">PetruWorkout.com</strong>
      </p>
      <p style="margin:8px 0 0 0;color:#999999;font-size:12px;">
        Puedes responder directamente a este email para contactar con {nombre}
      </p>
    </div>
  </div>
</body>
</html>""",
        }
        return self._send(payload)


# Instancia global
email_service = EmailService()