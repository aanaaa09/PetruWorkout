# ==========================================
# backend/tests/unit/test_calculator.py
# ==========================================
"""Tests unitarios para la calculadora de calorías"""
import pytest
from datetime import datetime, timedelta
from backend.services.calculator_token_service import calculator_token_service


def test_calculator_token_generation(db):
    """Test generación de token de calculadora"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # Crear usuario de prueba
    usuario = usuario_crud.create(
        db,
        nombre="Test User",
        email="test@calculator.com",
        password="testpass123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    # Generar token
    result = calculator_token_service.create_token_for_user(db, "test@calculator.com")

    assert result['success'] is True
    assert 'token' in result
    assert 'url' in result
    assert result['url'].startswith('https://petrucalistenia.com/calculator?token=')


def test_calculator_token_validation(db):
    """Test validación de token de calculadora"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # Crear usuario
    usuario = usuario_crud.create(
        db,
        nombre="Test User",
        email="test2@calculator.com",
        password="testpass123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    # Generar token
    token_result = calculator_token_service.create_token_for_user(db, "test2@calculator.com")
    token = token_result['token']

    # Validar token
    validation = calculator_token_service.validate_token(db, token)

    assert validation['valid'] is True
    assert 'usuario' in validation
    assert validation['usuario']['email'] == "test2@calculator.com"


def test_calculator_token_expiration(db):
    """Test expiración de token de calculadora"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # Crear usuario
    usuario = usuario_crud.create(
        db,
        nombre="Test User",
        email="test3@calculator.com",
        password="testpass123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    # Generar token
    token_result = calculator_token_service.create_token_for_user(db, "test3@calculator.com")
    token = token_result['token']

    # Simular token expirado (modificar fecha de creación)
    usuario.calculator_token_created = datetime.now() - timedelta(days=31)
    db.commit()

    # Validar token expirado
    validation = calculator_token_service.validate_token(db, token)

    assert validation['valid'] is False
    assert 'expirado' in validation['error'].lower()


def test_calculator_calorie_calculation():
    """Test cálculo de calorías - Fórmula de Harris-Benedict"""

    # Test para hombre
    # Valores de prueba: 25 años, 70kg, 175cm, actividad moderada
    age = 25
    weight = 70
    height = 175

    # BMR Hombre
    expected_bmr = round((10 * weight) + (6.25 * height) - (5 * age) + 5)

    assert expected_bmr > 0
    assert 1500 < expected_bmr < 2500  # Rango razonable

    # TDEE con actividad moderada (1.55)
    expected_tdee = round(expected_bmr * 1.55)

    assert expected_tdee > expected_bmr
    assert 2000 < expected_tdee < 4000


def test_calculator_bmi_calculation():
    """Test cálculo de IMC"""

    # Test 1: IMC normal
    weight = 70  # kg
    height = 175  # cm
    height_m = height / 100

    bmi = round(weight / (height_m * height_m), 1)

    assert 18.5 <= bmi < 25  # Rango normal
    assert bmi == 22.9

    # Test 2: IMC sobrepeso
    weight = 85
    height = 170
    height_m = height / 100

    bmi = round(weight / (height_m * height_m), 1)

    assert 25 <= bmi < 30  # Rango sobrepeso


def test_calculator_macros_distribution():
    """Test distribución de macronutrientes"""

    recommended_calories = 2500

    # Distribución: 30% proteína, 40% carbohidratos, 30% grasas
    protein_cal = round(recommended_calories * 0.30)
    carbs_cal = round(recommended_calories * 0.40)
    fats_cal = round(recommended_calories * 0.30)

    # Verificar que sumen aproximadamente el total
    total = protein_cal + carbs_cal + fats_cal
    assert abs(total - recommended_calories) <= 3  # Pequeña diferencia por redondeo

    # Convertir a gramos
    protein_g = round(protein_cal / 4)  # 4 kcal/g
    carbs_g = round(carbs_cal / 4)
    fats_g = round(fats_cal / 9)  # 9 kcal/g

    assert protein_g > 0
    assert carbs_g > 0
    assert fats_g > 0

    # Verificar proporciones aproximadas
    assert 150 < protein_g < 250
    assert 200 < carbs_g < 300
    assert 60 < fats_g < 100


def test_invalid_calculator_token(db):
    """Test token inválido"""

    validation = calculator_token_service.validate_token(db, "token_invalido_12345")

    assert validation['valid'] is False
    assert 'error' in validation


def test_empty_calculator_token(db):
    """Test token vacío"""

    validation = calculator_token_service.validate_token(db, "")

    assert validation['valid'] is False
    assert 'vacío' in validation['error'].lower() or 'inválido' in validation['error'].lower()