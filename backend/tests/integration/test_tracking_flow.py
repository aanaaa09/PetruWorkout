"""Tests de integración para tracking"""
import pytest


def test_flujo_tracking_completo(client):
    """Test flujo: visita -> click -> booking"""

    # 1. Visita
    response = client.post("/api/tracking/visit", json={
        "session_id": "test-session",
        "traffic_source": "linkedin",
        "landing_page": "/info"
    })
    assert response.status_code == 200
    assert response.json()['success'] is True

    # 2. Click
    response = client.post("/api/tracking/click", json={
        "session_id": "test-session",
        "traffic_source": "linkedin",
        "button_id": "hero-cta",
        "button_location": "hero-section"
    })
    assert response.status_code == 200

    # 3. Booking
    response = client.post("/api/tracking/booking-completed", json={
        "session_id": "test-session",
        "traffic_source": "linkedin",
        "invitee_email": "test@example.com",
        "invitee_name": "Test User",
        "event_uri": "evt_test"
    })
    assert response.status_code == 200

    # 4. Verificar funnel
    response = client.get("/api/tracking/funnel?traffic_source=linkedin&days=1")
    assert response.status_code == 200
    funnel = response.json()['funnel']
    assert funnel['visits'] >= 1