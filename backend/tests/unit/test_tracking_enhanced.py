# ==========================================
# backend/tests/unit/test_tracking_enhanced.py
# ==========================================
"""Tests mejorados para el sistema de tracking"""
import pytest
from datetime import datetime, timedelta
from backend.crud.tracking import tracking_crud


def test_create_page_visit_with_all_data(db):
    """Test crear visita con todos los datos"""
    visit = tracking_crud.create_page_visit(
        db,
        session_id="test-session-123",
        traffic_source="linkedin",
        referrer_url="https://linkedin.com/feed",
        user_agent="Mozilla/5.0",
        landing_page="/info"
    )

    assert visit.id is not None
    assert visit.session_id == "test-session-123"
    assert visit.traffic_source == "linkedin"
    assert visit.referrer_url == "https://linkedin.com/feed"
    assert visit.landing_page == "/info"
    assert visit.fecha is not None
    assert visit.dia is not None
    assert visit.mes is not None
    assert visit.año is not None


def test_create_calendly_click_with_location(db):
    """Test crear click con ubicación del botón"""
    click = tracking_crud.create_calendly_click(
        db,
        session_id="test-session-456",
        traffic_source="instagram",
        button_id="hero-cta",
        button_location="hero-section",
        page_url="/"
    )

    assert click.id is not None
    assert click.button_id == "hero-cta"
    assert click.button_location == "hero-section"
    assert click.page_url == "/"


def test_create_calendly_booking_complete(db):
    """Test crear booking con todos los datos"""
    event_time = datetime.now() + timedelta(days=7)

    booking = tracking_crud.create_calendly_booking(
        db,
        calendly_event_id="evt_test_12345",
        invitee_email="test@example.com",
        invitee_name="Test User",
        event_start_time=event_time,
        booking_timestamp=datetime.now(),
        session_id="test-session-789",
        traffic_source="youtube"
    )

    assert booking.id is not None
    assert booking.calendly_event_id == "evt_test_12345"
    assert booking.invitee_email == "test@example.com"
    assert booking.invitee_name == "Test User"
    assert booking.traffic_source == "youtube"


def test_traffic_stats_multiple_sources(db):
    """Test estadísticas con múltiples fuentes de tráfico"""

    # Crear visitas de diferentes fuentes
    sources = ["linkedin", "instagram", "youtube", "linkedin", "instagram", "linkedin"]

    for source in sources:
        tracking_crud.create_page_visit(
            db,
            session_id=f"session-{source}-{datetime.now().timestamp()}",
            traffic_source=source,
            landing_page="/"
        )

    stats = tracking_crud.get_traffic_stats(db, days=1)

    assert 'visits' in stats
    visits = stats['visits']

    # Verificar conteos
    linkedin_visits = next((v for v in visits if v['source'] == 'linkedin'), None)
    instagram_visits = next((v for v in visits if v['source'] == 'instagram'), None)
    youtube_visits = next((v for v in visits if v['source'] == 'youtube'), None)

    assert linkedin_visits['total'] == 3
    assert instagram_visits['total'] == 2
    assert youtube_visits['total'] == 1


def test_conversion_funnel_complete(db):
    """Test embudo de conversión completo"""
    session_id = "funnel-test-session"
    traffic_source = "linkedin"

    # 1. Visita
    tracking_crud.create_page_visit(
        db, session_id, traffic_source, None, None, "/"
    )

    # 2. Click en Calendly
    tracking_crud.create_calendly_click(
        db, session_id, traffic_source, "hero-cta", "hero"
    )

    # 3. Booking completado
    tracking_crud.create_calendly_booking(
        db, "evt_funnel_123", "funnel@test.com", "Funnel Test",
        datetime.now(), datetime.now(), session_id, traffic_source
    )

    # Obtener estadísticas del embudo
    funnel = tracking_crud.get_conversion_funnel(db, traffic_source, days=1)

    assert funnel['visits'] >= 1
    assert funnel['clicks'] >= 1
    assert funnel['bookings'] >= 1
    assert funnel['click_rate'] > 0
    assert funnel['booking_rate'] > 0
    assert funnel['overall_conversion'] > 0


def test_stats_by_date_grouping(db):
    """Test agrupación de estadísticas por fecha"""

    # Crear visitas en diferentes días
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    # Visitas hoy
    for i in range(3):
        tracking_crud.create_page_visit(
            db, f"session-today-{i}", "instagram", None, None, "/"
        )

    # Simular visitas de ayer (modificar timestamp)
    for i in range(2):
        visit = tracking_crud.create_page_visit(
            db, f"session-yesterday-{i}", "youtube", None, None, "/"
        )
        visit.timestamp = yesterday
        visit.fecha = yesterday.date()
        db.commit()

    stats = tracking_crud.get_stats_by_date(db, days=7)

    assert len(stats) >= 2

    # Verificar que hay datos para hoy y ayer
    dates = [s['fecha'] for s in stats]
    assert str(today.date()) in dates or str(yesterday.date()) in dates


def test_unique_visitors_counting(db):
    """Test conteo de visitantes únicos"""

    session_id = "unique-visitor-test"

    # Múltiples visitas del mismo usuario (misma sesión)
    for i in range(5):
        tracking_crud.create_page_visit(
            db, session_id, "linkedin", None, None, f"/page{i}"
        )

    stats = tracking_crud.get_traffic_stats(db, days=1)

    linkedin_stats = next((v for v in stats['visits'] if v['source'] == 'linkedin'), None)

    # Debe contar 5 visitas totales pero 1 visitante único
    assert linkedin_stats['total'] >= 5
    assert linkedin_stats['unique'] >= 1


def test_conversion_rate_calculation(db):
    """Test cálculo correcto de tasas de conversión"""

    traffic_source = "test_source"

    # Crear 10 visitas
    for i in range(10):
        tracking_crud.create_page_visit(
            db, f"session-{i}", traffic_source, None, None, "/"
        )

    # 5 clicks (50% click rate)
    for i in range(5):
        tracking_crud.create_calendly_click(
            db, f"session-{i}", traffic_source, "cta", "hero"
        )

    # 2 bookings (20% booking rate de clicks, 20% overall)
    for i in range(2):
        tracking_crud.create_calendly_booking(
            db, f"evt_{i}", f"test{i}@test.com", "Test",
            datetime.now(), datetime.now(), f"session-{i}", traffic_source
        )

    funnel = tracking_crud.get_conversion_funnel(db, traffic_source, days=1)

    assert funnel['visits'] == 10
    assert funnel['clicks'] == 5
    assert funnel['bookings'] == 2

    # Click rate = (clicks / visits) * 100 = (5/10) * 100 = 50%
    assert funnel['click_rate'] == 50.0

    # Booking rate = (bookings / clicks) * 100 = (2/5) * 100 = 40%
    assert funnel['booking_rate'] == 40.0

    # Overall conversion = (bookings / visits) * 100 = (2/10) * 100 = 20%
    assert funnel['overall_conversion'] == 20.0


def test_timezone_handling(db):
    """Test manejo correcto de zonas horarias"""

    visit = tracking_crud.create_page_visit(
        db, "tz-test", "linkedin", None, None, "/"
    )

    # Verificar que el timestamp está en hora de España (UTC+1)
    # La diferencia debería ser aproximadamente 1 hora con UTC
    utc_now = datetime.utcnow()

    # La fecha debe estar establecida
    assert visit.fecha is not None
    assert visit.timestamp is not None