# backend/crud/analytics_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, datetime, timedelta, timezone

from ..models.page_visit import PageVisit
from ..models.calendly_click import CalendlyClick
from ..models.calendly_booking import CalendlyBooking

SPAIN_TZ = timezone(timedelta(hours=1))

# Fuentes de tráfico reconocidas
KNOWN_SOURCES = ("instagram", "organic_search", "youtube", "facebook", "linkedin")

# Ubicaciones de botón reconocidas
KNOWN_BUTTONS = (
    "hero-section",
    "calculator-section",
    "results-section",
    "services-section",
    "video-section",
    "full-footer",
    "full-navbar",
    "simple-footer",
)


def get_date_range(
    days: Optional[int],
    date_from: Optional[str],
    date_to: Optional[str],
):
    """
    Devuelve (start, end) como date.
    Siempre acota end a ayer (hora España) para evitar días incompletos.
    """
    now_spain = datetime.now(SPAIN_TZ)
    yesterday = now_spain.date() - timedelta(days=1)

    if date_from and date_to:
        try:
            start = date.fromisoformat(date_from)
            end   = min(date.fromisoformat(date_to), yesterday)
            return start, end
        except ValueError:
            pass

    d     = days or 30
    start = yesterday - timedelta(days=d - 1)
    return start, yesterday


def _apply_source_filter(query, model, source: Optional[str]):
    """
    Restringe la query a KNOWN_SOURCES o campañas personalizadas yt-*.
    Si se pasa una fuente concreta, filtra solo por ella.
    Cualquier fuente genérica no reconocida (direct, internal, unknown…) queda excluida.
    """
    if source:
        if source in KNOWN_SOURCES or source.startswith("yt-"):
            return query.filter(model.traffic_source == source)
        return query.filter(model.traffic_source.in_(KNOWN_SOURCES))
    
    return query.filter(
        (model.traffic_source.in_(KNOWN_SOURCES)) |
        (model.traffic_source.like("yt-%"))
    )


def _apply_button_filter(query, button: Optional[str]):
    """
    Restringe la query de CalendlyClick a KNOWN_BUTTONS.
    Si se pasa un botón concreto (y es conocido) filtra solo por él.
    Si button es None o no reconocido, incluye todos los KNOWN_BUTTONS.
    """
    if button and button in KNOWN_BUTTONS:
        return query.filter(CalendlyClick.button_location == button)
    return query.filter(CalendlyClick.button_location.in_(KNOWN_BUTTONS))


def count_filtered(
    db: Session,
    model,
    date_col,
    start: date,
    end: date,
    source: Optional[str],
    button: Optional[str] = None,
) -> int:
    """Cuenta registros del modelo dentro del rango de fechas y fuente opcional.
    El filtro de botón solo aplica a CalendlyClick."""
    q = _apply_source_filter(
        db.query(func.count(model.id))
          .filter(func.date(date_col).between(start, end)),
        model, source,
    )
    if button and model is CalendlyClick:
        q = _apply_button_filter(q, button)
    return q.scalar() or 0


def group_by_source(
    db: Session,
    model,
    date_col,
    start: date,
    end: date,
    source: Optional[str],
    button: Optional[str] = None,
) -> dict[str, int]:
    """Devuelve {traffic_source: count} para el rango y fuente opcional."""
    q = _apply_source_filter(
        db.query(model.traffic_source, func.count(model.id).label("n"))
          .filter(func.date(date_col).between(start, end)),
        model, source,
    )
    if button and model is CalendlyClick:
        q = _apply_button_filter(q, button)
    rows = q.group_by(model.traffic_source).all()
    return {r.traffic_source: r.n for r in rows}


def daily_series(
    db: Session,
    model,
    date_col,
    start: date,
    end: date,
    source: Optional[str],
    button: Optional[str] = None,
) -> dict[str, int]:
    """Devuelve {fecha_str: count} día a día para el rango y fuente opcional."""
    q = _apply_source_filter(
        db.query(func.date(date_col).label("day"), func.count(model.id).label("n"))
          .filter(func.date(date_col).between(start, end)),
        model, source,
    )
    if button and model is CalendlyClick:
        q = _apply_button_filter(q, button)
    rows = q.group_by(func.date(date_col)).all()
    return {str(r.day): r.n for r in rows}


def group_by_button(
    db: Session,
    start: date,
    end: date,
    source: Optional[str] = None,
) -> dict[str, int]:
    """
    Devuelve {button_location: count} de clicks para el rango.
    Siempre filtra por KNOWN_SOURCES y KNOWN_BUTTONS.
    """
    q = _apply_source_filter(
        db.query(CalendlyClick.button_location, func.count(CalendlyClick.id).label("n"))
          .filter(func.date(CalendlyClick.timestamp).between(start, end))
          .filter(CalendlyClick.button_location.isnot(None)),
        CalendlyClick, source,
    )
    q = q.filter(CalendlyClick.button_location.in_(KNOWN_BUTTONS))
    rows = q.group_by(CalendlyClick.button_location).all()
    return {r.button_location: r.n for r in rows}


def visits_count(db: Session, start: date, end: date, source: Optional[str]) -> int:
    return count_filtered(db, PageVisit, PageVisit.fecha, start, end, source)

def clicks_count(db: Session, start: date, end: date, source: Optional[str],
                 button: Optional[str] = None) -> int:
    return count_filtered(db, CalendlyClick, CalendlyClick.timestamp, start, end, source, button)

def bookings_count(db: Session, start: date, end: date, source: Optional[str]) -> int:
    return count_filtered(db, CalendlyBooking, CalendlyBooking.timestamp, start, end, source)

def visits_by_source(db: Session, start: date, end: date, source: Optional[str]) -> dict:
    return group_by_source(db, PageVisit, PageVisit.fecha, start, end, source)

def clicks_by_source(db: Session, start: date, end: date, source: Optional[str],
                     button: Optional[str] = None) -> dict:
    return group_by_source(db, CalendlyClick, CalendlyClick.timestamp, start, end, source, button)

def bookings_by_source(db: Session, start: date, end: date, source: Optional[str]) -> dict:
    return group_by_source(db, CalendlyBooking, CalendlyBooking.timestamp, start, end, source)

def visits_daily(db: Session, start: date, end: date, source: Optional[str]) -> dict:
    return daily_series(db, PageVisit, PageVisit.fecha, start, end, source)

def clicks_daily(db: Session, start: date, end: date, source: Optional[str],
                 button: Optional[str] = None) -> dict:
    return daily_series(db, CalendlyClick, CalendlyClick.timestamp, start, end, source, button)

def bookings_daily(db: Session, start: date, end: date, source: Optional[str]) -> dict:
    return daily_series(db, CalendlyBooking, CalendlyBooking.timestamp, start, end, source)