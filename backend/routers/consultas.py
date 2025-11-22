from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from ..config.database import get_db
from ..models.consulta import Consulta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config.settings import settings

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

        # Enviar email a Petru
        enviar_email_notificacion(data)

        return {
            'success': True,
            'mensaje': 'Consulta enviada correctamente'
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def enviar_email_notificacion(data: EnviarConsultaRequest):
    """Envía email a Petru con la consulta"""
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = "petruworkout@gmail.com"  # Email de Petru
        msg['Subject'] = f"Nueva consulta: {data.asunto}"

        body = f"""
        Nueva consulta recibida:

        Nombre: {data.nombre}
        Email: {data.email}
        Asunto: {data.asunto}

        Mensaje:
        {data.mensaje}
        """

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        print(f"Error enviando email: {e}")