from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

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


@router.post("/calculate", response_model=CalorieCalculatorResponse)
def calculate_calories(data: CalorieCalculatorRequest):
    """
    Calcula calorías y macronutrientes basándose en los datos del usuario.

    - **BMI**: Índice de Masa Corporal
    - **BMR**: Gasto Energético Basal (calorías en reposo)
    - **TDEE**: Gasto Energético Total Diario
    - **Recommended**: Calorías recomendadas según objetivo
    - **Macros**: Distribución de macronutrientes (30% proteína, 40% carbohidratos, 30% grasas)
    """
    try:
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
        raise HTTPException(status_code=500, detail=f"Error al calcular calorías: {str(e)}")