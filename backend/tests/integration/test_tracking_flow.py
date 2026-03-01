"""Tests de integración para tracking"""
import pytest
from datetime import date


def test_flujo_tracking_completo(client, db):
    """Test flujo: visita -> click -> booking"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # 1. Visita — fuente conocida (KNOWN_SOURCES: instagram/youtube/facebook/organic_search)
    response = client.post("/api/tracking/visit", json={
        "session_id": "test-session",
        "traffic_source": "instagram",
        "landing_page": "/info"
    })
    assert response.status_code == 200
    assert response.json()['success'] is True

    # 2. Click
    response = client.post("/api/tracking/click", json={
        "session_id": "test-session",
        "traffic_source": "instagram",
        "button_id": "hero-cta",
        "button_location": "hero-section"
    })
    assert response.status_code == 200

    # 3. Booking
    response = client.post("/api/tracking/booking-completed", json={
        "session_id": "test-session",
        "traffic_source": "instagram",
        "invitee_email": "test@example.com",
        "invitee_name": "Test User",
        "event_uri": "evt_test"
    })
    assert response.status_code == 200

    # 4. /funnel ahora requiere auth admin (movido a analytics.py)
    usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_funnel@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    token = client.post("/api/admin/login", json={
        "email": "admin_funnel@test.com",
        "password": "admin123"
    }).json()['token']

    # Incluir hoy en el rango porque el default termina en ayer
    today = str(date.today())
    response = client.get(
        f"/api/tracking/funnel?source=instagram&date_from={today}&date_to={today}",
        headers={"token": token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['visits'] >= 1