# backend/routers/fuerza.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from ..config.database import get_db
from ..crud.usuario import usuario_crud
from ..schemas.fuerza import FuerzaRequest, FuerzaRegisterRequest, FuerzaResult, FuerzaRegisterResult
from ..services.fuerza_service import calculate_fuerza
from ..services.lead_service import lead_service
from ..services.email_sequence_service import send_day0

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/fuerza", tags=["fuerza"])


@router.post("/calculate", response_model=FuerzaResult)
def calculate(data: FuerzaRequest):
    try:
        return calculate_fuerza(data.sexo, data.pull, data.dips, data.push, data.squat)
    except Exception as e:
        logger.error(f"Error calculando fuerza: {e}")
        raise HTTPException(status_code=500, detail="Error al calcular")


@router.post("/register-and-calculate", response_model=FuerzaRegisterResult)
def register_and_calculate(data: FuerzaRegisterRequest, db: Session = Depends(get_db)):
    try:
        lead_result = lead_service.register(db, data.email)

        nombre = data.nombre.strip().capitalize()

        if lead_result.get("nuevo"):
            usuario = usuario_crud.get_by_email(db, data.email.lower())
            if usuario:
                usuario.nombre = nombre
                db.commit()

        calc = calculate_fuerza(data.sexo, data.pull, data.dips, data.push, data.squat)

        # Enviar email día 0 con el resultado personalizado
        # (los datos ya están en memoria, no se guarda nada extra)
        try:
            send_day0(
                to_email=data.email,
                nombre=nombre,
                score=calc["score"],
                level=calc["level"],
                scores=calc["scores"],
                reps=calc["reps"],
            )
        except Exception as e:
            # El email no es bloqueante — si falla, el resultado igual se devuelve
            logger.error(f"Error enviando email día 0 a {data.email}: {e}")

        return {**calc, "registered": True, "nuevo": lead_result.get("nuevo", False)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en register-and-calculate: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar")