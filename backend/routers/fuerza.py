# backend/routers/fuerza.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from ..config.database import get_db
from ..crud.usuario import usuario_crud
from ..schemas.fuerza import FuerzaRequest, FuerzaRegisterRequest, FuerzaResult, FuerzaRegisterResult
from ..services.fuerza_service import calculate_fuerza
from ..services.lead_service import lead_service

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

        if lead_result.get("nuevo"):
            usuario = usuario_crud.get_by_email(db, data.email.lower())
            if usuario:
                usuario.nombre = data.nombre.strip().capitalize()
                db.commit()

        calc = calculate_fuerza(data.sexo, data.pull, data.dips, data.push, data.squat)
        return {**calc, "registered": True, "nuevo": lead_result.get("nuevo", False)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en register-and-calculate: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar")