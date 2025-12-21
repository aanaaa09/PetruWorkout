# ==========================================
# backend/tests/unit/test_tracking.py
# ==========================================
"""Tests unitarios para tracking"""
import pytest
from datetime import datetime
from backend.crud.tracking import tracking_crud


def test_create_page_visit(db):
    """Test registrar visita"""
    visit = tracking_crud.create_page_visit(
        db,
        session_id="test-123",
        traffic_source="linkedin",
        referrer_url="https://linkedin.com",
        landing_page="/info"
    )

    assert visit.id is not None
    assert visit.traffic_source == "linkedin"


def test_create_calendly_click(db):
    """Test registrar click"""
    click = tracking_crud.create_calendly_click(
        db,
        session_id="test-123",
        traffic_source="instagram",
        button_id="hero-cta",
        button_location="hero-section"
    )

    assert click.id is not None
    assert click.button_id == "hero-cta"


def test_create_calendly_booking(db):
    """Test registrar booking"""
    booking = tracking_crud.create_calendly_booking(
        db,
        calendly_event_id="evt_123",
        invitee_email="test@test.com",
        invitee_name="Test User",
        event_start_time=datetime.now(),
        booking_timestamp=datetime.now(),
        session_id="test-123",
        traffic_source="youtube"
    )

    assert booking.id is not None
    assert booking.invitee_email == "test@test.com"


def test_get_conversion_funnel(db):
    """Test embudo de conversión"""
    tracking_crud.create_page_visit(db, "s1", "linkedin", None, None, "/")
    tracking_crud.create_calendly_click(db, "s1", "linkedin", "btn", "hero")
    tracking_crud.create_calendly_booking(
        db, "evt_1", "test@test.com", "Test",
        datetime.now(), datetime.now(), "s1", "linkedin"
    )

    funnel = tracking_crud.get_conversion_funnel(db, "linkedin", days=30)

    assert funnel['visits'] >= 1
    assert funnel['clicks'] >= 1
    assert funnel['bookings'] >= 1
