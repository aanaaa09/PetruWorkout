# ==========================================
# backend/tests/unit/test_leads.py
# ==========================================
"""Tests unitarios para el sistema de leads"""
import pytest
from unittest.mock import patch, MagicMock


def test_lead_registration_new_user(client, db):
    """Test registro de nuevo lead"""

    with patch('backend.services.email_service.email_service.send_welcome_lead_email') as mock_email:
        mock_email.return_value = True

        response = client.post("/api/lead/register", json={
            "email": "newlead@test.com"
        })

        assert response.status_code == 200
        data = response.json()

        assert data['success'] is True
        assert data['nuevo'] is True
        assert data['has_team_access'] is True


def test_lead_registration_existing_user(client, db):
    """Test registro de lead existente"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # Crear usuario existente
    usuario_crud.create(
        db,
        nombre="Existing",
        email="existing@test.com",
        password="testpass123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    response = client.post("/api/lead/register", json={
        "email": "existing@test.com"
    })

    assert response.status_code == 200
    data = response.json()

    assert data['success'] is True
    assert data['nuevo'] is False
    assert data['has_team_access'] is True


def test_lead_registration_invalid_email(client):
    """Test registro con email inválido"""

    response = client.post("/api/lead/register", json={
        "email": "invalid-email"
    })

    assert response.status_code == 422  # Validation error


def test_lead_registration_rate_limit(client, db):
    """Test rate limiting por email"""

    email = "ratelimit@test.com"

    with patch('backend.services.email_service.email_service.send_welcome_lead_email') as mock_email:
        mock_email.return_value = True

        # Primer intento (OK)
        response1 = client.post("/api/lead/register", json={"email": email})
        assert response1.status_code == 200

        # Segundo intento (OK - límite es 2)
        response2 = client.post("/api/lead/register", json={"email": email})
        assert response2.status_code == 200

        # Tercer intento (debe fallar por rate limit)
        response3 = client.post("/api/lead/register", json={"email": email})
        assert response3.status_code == 429  # Too Many Requests


def test_team_access_grant(db):
    """Test concesión de acceso al equipo"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # Crear usuario sin acceso
    usuario = usuario_crud.create(
        db,
        nombre="Test",
        email="team@test.com",
        password="testpass123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    assert usuario.team_access_granted is False

    # Conceder acceso
    usuario.team_access_granted = True
    db.commit()
    db.refresh(usuario)

    assert usuario.team_access_granted is True


def test_calculator_token_creation_on_lead_registration(client, db):
    """Test que se crea token de calculadora al registrar lead"""

    with patch('backend.services.email_service.email_service.send_welcome_lead_email') as mock_email:
        mock_email.return_value = True

        response = client.post("/api/lead/register", json={
            "email": "leadtoken@test.com"
        })

        assert response.status_code == 200

        # Verificar que el usuario tiene token de calculadora
        from backend.crud.usuario import usuario_crud
        usuario = usuario_crud.get_by_email(db, "leadtoken@test.com")

        assert usuario is not None
        assert usuario.calculator_token is not None
        assert usuario.calculator_token_created is not None