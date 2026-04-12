# backend/services/calculator_service.py
"""
Lógica de dominio para el cálculo nutricional.
Extraída del router para que este solo gestione HTTP.
"""

from typing import Literal
import logging

logger = logging.getLogger(__name__)

ACTIVITY_MULTIPLIERS = {
    "sedentary":   1.2,
    "light":       1.375,
    "moderate":    1.55,
    "active":      1.725,
    "very_active": 1.9,
}


def calculate_nutrition(
    gender: Literal["male", "female"],
    age: int,
    weight: float,
    height: int,
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"],
    goal: Literal["lose", "maintain", "gain"],
) -> dict:
    """
    Calcula BMI, BMR, TDEE, calorías recomendadas y macronutrientes.

    Fórmula BMR: Harris-Benedict revisada.
    Distribución macros: 30% proteína / 40% carbohidratos / 30% grasas.

    Returns:
        dict con bmi, bmr, tdee, recommended y macros (gramos y calorías).
    """
    # BMI
    height_m = height / 100
    bmi = round(weight / (height_m ** 2), 1)

    #GEB
    if gender == "male":
        bmr = round((10 * weight) + (6.25 * height) - (5 * age) + 5)
    else:
        bmr = round((10 * weight) + (6.25 * height) - (5 * age) - 161)
    # TDEE
    tdee = round(bmr * ACTIVITY_MULTIPLIERS[activity_level])

    # Calorías ajustadas al objetivo
    if goal == "lose":
        recommended = round(tdee - 500)
    elif goal == "maintain":
        recommended = tdee
    else:  # gain
        recommended = round(tdee + 300)

    # Macronutrientes: 30% proteína / 40% carbos / 30% grasas
    protein_cal = round(recommended * 0.30)
    carbs_cal   = round(recommended * 0.40)
    fats_cal    = round(recommended * 0.30)

    protein = round(protein_cal / 4)  # 4 kcal/g
    carbs   = round(carbs_cal   / 4)  # 4 kcal/g
    fats    = round(fats_cal    / 9)  # 9 kcal/g

    return {
        "bmi":         bmi,
        "bmr":         bmr,
        "tdee":        tdee,
        "recommended": recommended,
        "macros": {
            "protein":     protein,
            "carbs":       carbs,
            "fats":        fats,
            "protein_cal": protein_cal,
            "carbs_cal":   carbs_cal,
            "fats_cal":    fats_cal,
        },
    }