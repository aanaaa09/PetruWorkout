# backend/routers/tracking.py
"""
Router de tracking de visitas, clicks y bookings.
El webhook de Calendly se elimina (no se usa, se usa sync_calendly.py via GitHub Actions).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from ..config.database import get_db
from ..crud.tracking import tracking_crud
from ..schemas.tracking import PageVisitCreate, CalendlyClickCreate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/visit")
async def register_page_visit(
    visit_data: PageVisitCreate,
    db: Session = Depends(get_db),
):
    """Registra una visita a la página."""
    try:
        visit = tracking_crud.create_page_visit(
            db=db,
            session_id=visit_data.session_id,
            traffic_source=visit_data.traffic_source,
            referrer_url=visit_data.referrer_url,
            user_agent=visit_data.user_agent,
            landing_page=visit_data.landing_page,
        )
        return {"success": True, "message": "Visita registrada correctamente", "visit_id": visit.id}
    except Exception as e:
        logger.error(f"Error al registrar visita: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/click")
async def register_calendly_click(
    click_data: CalendlyClickCreate,
    db: Session = Depends(get_db),
):
    """Registra un click en botón de Calendly."""
    try:
        click = tracking_crud.create_calendly_click(
            db=db,
            session_id=click_data.session_id,
            traffic_source=click_data.traffic_source,
            button_id=click_data.button_id,
            button_location=click_data.button_location,
            page_url=click_data.page_url,
        )
        return {"success": True, "message": "Click registrado correctamente", "click_id": click.id}
    except Exception as e:
        logger.error(f"Error al registrar click: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/booking-completed")
async def booking_completed(
    data: dict,
    db: Session = Depends(get_db),
):
    """
    Registra una reserva completada detectada desde el frontend
    cuando Calendly emite el evento 'calendly.event_scheduled'.
    """
    try:
        session_id      = data.get('session_id')
        traffic_source  = data.get('traffic_source', 'unknown')
        invitee_email   = data.get('invitee_email', 'unknown')
        invitee_name    = data.get('invitee_name', 'unknown')
        event_uri       = data.get('event_uri')
        event_start_str = data.get('event_start_time')

        event_start_time = None
        if event_start_str:
            try:
                event_start_time = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
            except ValueError:
                pass

        booking = tracking_crud.create_calendly_booking(
            db=db,
            calendly_event_id=event_uri or f"frontend_{session_id}_{datetime.now().timestamp()}",
            invitee_email=invitee_email,
            invitee_name=invitee_name,
            event_start_time=event_start_time,
            session_id=session_id,
            traffic_source=traffic_source,
        )
        logger.info(f"Reserva completada registrada: {invitee_email} desde {traffic_source}")
        return {"success": True, "message": "Reserva registrada correctamente", "booking_id": booking.id}

    except Exception as e:
        logger.error(f"Error al registrar booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))