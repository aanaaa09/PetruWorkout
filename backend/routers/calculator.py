# backend/routers/calculator.py

from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Literal, Optional
import logging

from ..config.database import get_db
from ..services.calculator_token_service import calculator_token_service
from ..services.calculator_service import calculate_nutrition

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/calculator", tags=["calculator"])


# ── Schemas ───────────────────────────────────────────────────────

class CalorieCalculatorRequest(BaseModel):
    gender:         Literal["male", "female"]
    age:            int   = Field(..., ge=15, le=100)
    weight:         float = Field(..., ge=30, le=300)
    height:         int   = Field(..., ge=100, le=250)
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"]
    goal:           Literal["lose", "maintain", "gain"]


class MacronutrientsResponse(BaseModel):
    protein:     int
    carbs:       int
    fats:        int
    protein_cal: int
    carbs_cal:   int
    fats_cal:    int


class CalorieCalculatorResponse(BaseModel):
    bmi:         float
    bmr:         int
    tdee:        int
    recommended: int
    macros:      MacronutrientsResponse


# ── Dependencia de seguridad ──────────────────────────────────────

async def verify_calculator_token(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """Valida el Bearer token de la calculadora."""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Se requiere autenticación. Regístrate para acceder a la calculadora.",
        )
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Esquema de autenticación inválido")
    except ValueError:
        raise HTTPException(status_code=401, detail="Formato de token inválido")

    result = calculator_token_service.validate_token(db, token)
    if not result['valid']:
        logger.warning(f"Acceso con token inválido: {result.get('error')}")
        raise HTTPException(status_code=401, detail=f"Acceso denegado: {result.get('error', 'Token inválido')}")

    return result['usuario']


# ── Endpoints ─────────────────────────────────────────────────────

@router.post("/calculate", response_model=CalorieCalculatorResponse)
async def calculate_calories(
    data: CalorieCalculatorRequest,
    usuario: dict = Depends(verify_calculator_token),
):
    """Calcula calorías y macronutrientes. Requiere token de acceso."""
    try:
        logger.info(f"Cálculo para usuario: {usuario['email']}")
        result = calculate_nutrition(
            gender=data.gender,
            age=data.age,
            weight=data.weight,
            height=data.height,
            activity_level=data.activity_level,
            goal=data.goal,
        )
        return CalorieCalculatorResponse(
            bmi=result["bmi"],
            bmr=result["bmr"],
            tdee=result["tdee"],
            recommended=result["recommended"],
            macros=MacronutrientsResponse(**result["macros"]),
        )
    except Exception as e:
        logger.error(f"Error calculando calorías: {e}")
        raise HTTPException(status_code=500, detail=f"Error al calcular calorías: {str(e)}")


@router.get("/verify-access")
async def verify_access(token: str, db: Session = Depends(get_db)):
    """Verifica si un token es válido para acceder a la calculadora."""
    result = calculator_token_service.validate_token(db, token)
    if result['valid']:
        return {"valid": True, "message": "Token válido. Acceso concedido.", "usuario": result['usuario']}
    return {"valid": False, "message": result.get('error', 'Token inválido')}