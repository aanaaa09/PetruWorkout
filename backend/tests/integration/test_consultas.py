"""Tests para consultas"""
import pytest
from unittest.mock import patch


def test_enviar_consulta(client):
    """Test enviar consulta"""

    with patch('backend.routers.consultas.enviar_email_brevo') as mock_email:
        mock_email.return_value = True

        response = client.post("/api/consultas/enviar", json={
            "nombre": "Test",
            "email": "test@test.com",
            "asunto": "Test",
            "mensaje": "Test message"
        })

        assert response.status_code == 200
        assert response.json()['success'] is True


def test_health_check(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": 1}