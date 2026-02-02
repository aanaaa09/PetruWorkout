from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Literal, Optional
from backend.config.database import get_db
from backend.services.calculator_token_service import calculator_token_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/calculator", tags=["calculator"])


class CalorieCalculatorRequest(BaseModel):
    """Request para calcular calorías"""
    gender: Literal["male", "female"] = Field(..., description="Sexo del usuario")
    age: int = Field(..., ge=15, le=100, description="Edad en años")
    weight: float = Field(..., ge=30, le=300, description="Peso en kg")
    height: int = Field(..., ge=100, le=250, description="Estatura en cm")
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"] = Field(
        ..., description="Nivel de actividad física"
    )
    goal: Literal["lose", "maintain", "gain"] = Field(..., description="Objetivo del usuario")


class MacronutrientsResponse(BaseModel):
    """Respuesta de macronutrientes"""
    protein: int
    carbs: int
    fats: int
    protein_cal: int
    carbs_cal: int
    fats_cal: int


class CalorieCalculatorResponse(BaseModel):
    """Respuesta completa del cálculo de calorías"""
    bmi: float
    bmr: int
    tdee: int
    recommended: int
    macros: MacronutrientsResponse


# ==========================================
# DEPENDENCIA DE SEGURIDAD
# ==========================================
async def verify_calculator_token(
        authorization: Optional[str] = Header(None),
        db: Session = Depends(get_db)
):
    """
    Verifica que el usuario tenga un token válido para usar la calculadora

    El token se envía en el header Authorization como: Bearer <token>
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Se requiere autenticación. Regístrate para acceder a la calculadora."
        )

    # Extraer token del header "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Esquema de autenticación inválido"
            )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Formato de token inválido"
        )

    # Validar token
    result = calculator_token_service.validate_token(db, token)

    if not result['valid']:
        logger.warning(f"Intento de acceso con token inválido: {result.get('error')}")
        raise HTTPException(
            status_code=401,
            detail=f"Acceso denegado: {result.get('error', 'Token inválido')}"
        )

    return result['usuario']


# ==========================================
# ENDPOINT PROTEGIDO
# ==========================================
@router.post("/calculate", response_model=CalorieCalculatorResponse)
async def calculate_calories(
        data: CalorieCalculatorRequest,
        usuario: dict = Depends(verify_calculator_token)
):
    """
    Calcula calorías y macronutrientes basándose en los datos del usuario.

    **REQUIERE AUTENTICACIÓN**: Debes registrarte y usar tu token de acceso.

    - **BMI**: Índice de Masa Corporal
    - **BMR**: Gasto Energético Basal (calorías en reposo)
    - **TDEE**: Gasto Energético Total Diario
    - **Recommended**: Calorías recomendadas según objetivo
    - **Macros**: Distribución de macronutrientes (30% proteína, 40% carbohidratos, 30% grasas)
    """
    try:
        logger.info(f"Cálculo de calorías para usuario: {usuario['email']}")

        # 1. Calcular IMC
        height_in_meters = data.height / 100
        bmi = round(data.weight / (height_in_meters * height_in_meters), 1)

        # 2. Calcular Gasto Energético Basal (GEB) - Fórmula de Harris-Benedict
        if data.gender == "male":
            bmr = round(
                88.362 +
                (13.397 * data.weight) +
                (4.799 * data.height) -
                (5.677 * data.age)
            )
        else:  # female
            bmr = round(
                447.593 +
                (9.247 * data.weight) +
                (3.098 * data.height) -
                (4.330 * data.age)
            )

        # 3. Calcular Gasto Energético Total (GET)
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        tdee = round(bmr * activity_multipliers[data.activity_level])

        # 4. Ajustar según objetivo
        if data.goal == "lose":
            recommended = round(tdee - 500)  # Déficit de 500 kcal
        elif data.goal == "maintain":
            recommended = tdee
        else:  # gain
            recommended = round(tdee + 300)  # Superávit de 300 kcal

        # 5. Calcular macronutrientes (30% proteína, 40% carbohidratos, 30% grasas)
        protein_cal = round(recommended * 0.30)
        carbs_cal = round(recommended * 0.40)
        fats_cal = round(recommended * 0.30)

        protein = round(protein_cal / 4)  # 4 kcal por gramo
        carbs = round(carbs_cal / 4)  # 4 kcal por gramo
        fats = round(fats_cal / 9)  # 9 kcal por gramo

        macros = MacronutrientsResponse(
            protein=protein,
            carbs=carbs,
            fats=fats,
            protein_cal=protein_cal,
            carbs_cal=carbs_cal,
            fats_cal=fats_cal
        )

        return CalorieCalculatorResponse(
            bmi=bmi,
            bmr=bmr,
            tdee=tdee,
            recommended=recommended,
            macros=macros
        )

    except Exception as e:
        logger.error(f"Error al calcular calorías: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al calcular calorías: {str(e)}")


# ==========================================
# ENDPOINT PÚBLICO PARA VERIFICAR TOKEN
# ==========================================
@router.get("/verify-access")
async def verify_access(
        token: str,
        db: Session = Depends(get_db)
):
    """
    Verifica si un token es válido para acceder a la calculadora

    Útil para el frontend para verificar antes de mostrar la calculadora
    """
    result = calculator_token_service.validate_token(db, token)

    if result['valid']:
        return {
            "valid": True,
            "message": "Token válido. Acceso concedido.",
            "usuario": result['usuario']
        }
    else:
        return {
            "valid": False,
            "message": result.get('error', 'Token inválido')
        }