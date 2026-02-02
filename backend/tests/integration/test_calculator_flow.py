# ==========================================
# backend/tests/integration/test_calculator_flow.py
# ==========================================
"""Tests de integración para el flujo completo de calculadora"""
import pytest
from unittest.mock import patch


def test_flujo_completo_calculadora(client, db):
    """Test flujo: registro → token → cálculo de calorías"""

    # 1. Registro de lead
    with patch('backend.routers.leads.enviar_email_bienvenida') as mock_email:
        mock_email.return_value = True

        response = client.post("/api/lead/register", json={
            "email": "fullflow@test.com"
        })

        assert response.status_code == 200

    # 2. Obtener token del usuario
    from backend.crud.usuario import usuario_crud
    usuario = usuario_crud.get_by_email(db, "fullflow@test.com")
    token = usuario.calculator_token

    assert token is not None

    # 3. Verificar acceso con token
    response = client.get(f"/api/calculator/verify-access?token={token}")
    assert response.status_code == 200
    data = response.json()
    assert data['valid'] is True

    # 4. Calcular calorías
    response = client.post(
        "/api/calculator/calculate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "gender": "male",
            "age": 25,
            "weight": 70,
            "height": 175,
            "activity_level": "moderate",
            "goal": "maintain"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert 'bmi' in data
    assert 'bmr' in data
    assert 'tdee' in data
    assert 'recommended' in data
    assert 'macros' in data

    # Verificar valores razonables
    assert 18.5 <= data['bmi'] <= 25
    assert 1500 <= data['bmr'] <= 2500
    assert 2000 <= data['tdee'] <= 4000
    assert data['macros']['protein'] > 0
    assert data['macros']['carbs'] > 0
    assert data['macros']['fats'] > 0


def test_calculadora_sin_token(client):
    """Test acceso a calculadora sin token"""

    response = client.post(
        "/api/calculator/calculate",
        json={
            "gender": "male",
            "age": 25,
            "weight": 70,
            "height": 175,
            "activity_level": "moderate",
            "goal": "maintain"
        }
    )

    assert response.status_code == 401  # Unauthorized


def test_calculadora_token_invalido(client):
    """Test acceso con token inválido"""

    response = client.post(
        "/api/calculator/calculate",
        headers={"Authorization": "Bearer token_invalido_12345"},
        json={
            "gender": "male",
            "age": 25,
            "weight": 70,
            "height": 175,
            "activity_level": "moderate",
            "goal": "maintain"
        }
    )

    assert response.status_code == 401


def test_calculadora_diferentes_objetivos(client, db):
    """Test cálculo con diferentes objetivos"""

    # Crear usuario con token
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.services.calculator_token_service import calculator_token_service

    usuario = usuario_crud.create(
        db,
        nombre="Test",
        email="goals@test.com",
        password="testpass123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    result = calculator_token_service.create_token_for_user(db, "goals@test.com")
    token = result['token']

    base_data = {
        "gender": "male",
        "age": 25,
        "weight": 70,
        "height": 175,
        "activity_level": "moderate"
    }

    # Test objetivo: perder peso
    response_lose = client.post(
        "/api/calculator/calculate",
        headers={"Authorization": f"Bearer {token}"},
        json={**base_data, "goal": "lose"}
    )

    # Test objetivo: mantener
    response_maintain = client.post(
        "/api/calculator/calculate",
        headers={"Authorization": f"Bearer {token}"},
        json={**base_data, "goal": "maintain"}
    )

    # Test objetivo: ganar
    response_gain = client.post(
        "/api/calculator/calculate",
        headers={"Authorization": f"Bearer {token}"},
        json={**base_data, "goal": "gain"}
    )

    assert response_lose.status_code == 200
    assert response_maintain.status_code == 200
    assert response_gain.status_code == 200

    calories_lose = response_lose.json()['recommended']
    calories_maintain = response_maintain.json()['recommended']
    calories_gain = response_gain.json()['recommended']

    # Verificar que las calorías son coherentes
    assert calories_lose < calories_maintain < calories_gain
    assert calories_maintain - calories_lose == 500  # Déficit de 500
    assert calories_gain - calories_maintain == 300  # Superávit de 300


def test_calculadora_genero_femenino(client, db):
    """Test cálculo para género femenino"""

    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.services.calculator_token_service import calculator_token_service

    usuario = usuario_crud.create(
        db,
        nombre="Test",
        email="female@test.com",
        password="testpass123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    result = calculator_token_service.create_token_for_user(db, "female@test.com")
    token = result['token']

    response = client.post(
        "/api/calculator/calculate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "gender": "female",
            "age": 25,
            "weight": 60,
            "height": 165,
            "activity_level": "moderate",
            "goal": "maintain"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # BMR femenino es generalmente menor que masculino
    assert 1200 <= data['bmr'] <= 1800
    assert data['bmi'] > 0
    assert data['tdee'] > data['bmr']


def test_calculadora_niveles_actividad(client, db):
    """Test diferentes niveles de actividad"""

    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.services.calculator_token_service import calculator_token_service

    usuario = usuario_crud.create(
        db,
        nombre="Test",
        email="activity@test.com",
        password="testpass123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    result = calculator_token_service.create_token_for_user(db, "activity@test.com")
    token = result['token']

    base_data = {
        "gender": "male",
        "age": 25,
        "weight": 70,
        "height": 175,
        "goal": "maintain"
    }

    # Test diferentes niveles
    levels = ["sedentary", "light", "moderate", "active", "very_active"]
    results = []

    for level in levels:
        response = client.post(
            "/api/calculator/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json={**base_data, "activity_level": level}
        )
        assert response.status_code == 200
        results.append(response.json()['tdee'])

    # Verificar que TDEE aumenta con el nivel de actividad
    for i in range(len(results) - 1):
        assert results[i] < results[i + 1]