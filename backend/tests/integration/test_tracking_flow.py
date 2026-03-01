"""Tests de integración para tracking"""
import pytest
from datetime import datetime, date, timedelta


def _move_to_yesterday(db, obj):
    """Mueve un registro a ayer para que entre en el rango del dashboard.
    El dashboard siempre corta en 'ayer' como máximo (get_date_range lo fuerza)."""
    yesterday = date.today() - timedelta(days=1)
    obj.fecha = yesterday
    if hasattr(obj, 'timestamp'):
        obj.timestamp = datetime.now() - timedelta(days=1)
    db.commit()
    return obj


def test_flujo_tracking_completo(client, db):
    """Test flujo: visita -> click -> booking -> funnel"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.models.page_visit import PageVisit
    from backend.models.calendly_click import CalendlyClick
    from backend.models.calendly_booking import CalendlyBooking

    # 1. Visita — fuente conocida (KNOWN_SOURCES: instagram/youtube/facebook/organic_search)
    response = client.post("/api/tracking/visit", json={
        "session_id": "test-session",
        "traffic_source": "instagram",
        "landing_page": "/info"
    })
    assert response.status_code == 200
    assert response.json()['success'] is True
    visit = db.query(PageVisit).filter(PageVisit.session_id == "test-session").first()
    _move_to_yesterday(db, visit)

    # 2. Click — mover a ayer
    response = client.post("/api/tracking/click", json={
        "session_id": "test-session",
        "traffic_source": "instagram",
        "button_id": "hero-cta",
        "button_location": "hero-section"
    })
    assert response.status_code == 200
    click = db.query(CalendlyClick).filter(CalendlyClick.session_id == "test-session").first()
    _move_to_yesterday(db, click)

    # 3. Booking — mover a ayer
    response = client.post("/api/tracking/booking-completed", json={
        "session_id": "test-session",
        "traffic_source": "instagram",
        "invitee_email": "test@example.com",
        "invitee_name": "Test User",
        "event_uri": "evt_test"
    })
    assert response.status_code == 200
    booking = db.query(CalendlyBooking).filter(
        CalendlyBooking.invitee_email == "test@example.com"
    ).first()
    _move_to_yesterday(db, booking)

    # 4. /funnel requiere auth admin
    usuario_crud.create(
        db, nombre="Admin", email="admin_funnel@test.com",
        password="admin123", tipo_usuario=TipoUsuario.ADMIN
    )
    token = client.post("/api/admin/login", json={
        "email": "admin_funnel@test.com", "password": "admin123"
    }).json()['token']

    # Rango por defecto — los datos están en ayer, entran en los últimos 30 días
    response = client.get(
        "/api/tracking/funnel?source=instagram",
        headers={"token": token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['visits'] >= 1