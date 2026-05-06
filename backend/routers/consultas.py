# backend/routers/consultas.py


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import logging

from ..config.database import get_db
from ..models.consulta import Consulta
from ..services.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/consultas", tags=["consultas"])


class EnviarConsultaRequest(BaseModel):
    nombre: str
    email:  EmailStr
    asunto: str
    mensaje: str


@router.post("/enviar")
def enviar_consulta(data: EnviarConsultaRequest, db: Session = Depends(get_db)):
    """Guarda la consulta en BD y notifica a Petru por email."""
    try:
        consulta = Consulta(
            nombre=data.nombre,
            email=data.email,
            asunto=data.asunto,
            mensaje=data.mensaje,
        )
        db.add(consulta)
        db.commit()

        resultado = email_service.send_consulta_email(
            nombre=data.nombre,
            email=data.email,
            asunto=data.asunto,
            mensaje=data.mensaje,
        )
        if not resultado:
            logger.warning("Consulta guardada en BD pero email no enviado")

        return {'success': True, 'mensaje': 'Consulta enviada correctamente'}

    except Exception as e:
        logger.error(f"Error enviando consulta: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al enviar la consulta")