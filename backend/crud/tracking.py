from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from ..models import SessionTracking
from ..models.page_visit import PageVisit
from ..models.calendly_click import CalendlyClick
from ..models.calendly_booking import CalendlyBooking
from ..services.traffic_source import detect_source
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TrackingCRUD:

    def _ensure_session(self, db: Session, session_id: str, traffic_source: str):
        if not session_id:
            return
        existe = db.query(SessionTracking).filter(
            SessionTracking.session_id == session_id
        ).first()
        if not existe:
            try:
                db.add(SessionTracking(
                    session_id=session_id,
                    traffic_source=traffic_source or "unknown"
                ))
                db.commit()
            except Exception:
                db.rollback()

    def create_page_visit(self, db: Session, session_id: str, traffic_source: str,
                          referrer_url: str = None, user_agent: str = None,
                          landing_page: str = None) -> PageVisit:
        detected = detect_source(referrer_url, user_agent)
        self._ensure_session(db, session_id, detected)

        now_spain = datetime.utcnow() + timedelta(hours=1)
        visit = PageVisit(
            session_id=session_id,
            traffic_source=detected,
            referrer_url=referrer_url,
            user_agent=user_agent,
            landing_page=landing_page,
            timestamp=now_spain,
            fecha=now_spain.date(),
            dia=now_spain.day,
            mes=now_spain.month,
            año=now_spain.year,
            hora=now_spain.time()
        )
        db.add(visit)
        db.commit()
        return visit

    def create_calendly_click(self, db: Session, session_id: str, traffic_source: str,
                              button_id: str = None, button_location: str = None,
                              page_url: str = None) -> CalendlyClick:
        session = db.query(SessionTracking).filter(
            SessionTracking.session_id == session_id
        ).first()
        detected = session.traffic_source if session else detect_source(None, None)
        self._ensure_session(db, session_id, detected)

        now_spain = datetime.utcnow() + timedelta(hours=1)
        click = CalendlyClick(
            session_id=session_id,
            traffic_source=detected,
            button_id=button_id,
            button_location=button_location,
            page_url=page_url,
            timestamp=now_spain,
            fecha=now_spain.date(),
            dia=now_spain.day,
            mes=now_spain.month,
            año=now_spain.year,
            hora=now_spain.time()
        )
        db.add(click)
        db.commit()
        return click

    def create_calendly_booking(self, db: Session, calendly_event_id: str,
                                invitee_email: str = None, invitee_name: str = None,
                                event_start_time: datetime = None, booking_timestamp: datetime = None,
                                session_id: str = None, traffic_source: str = None) -> CalendlyBooking:
        session = db.query(SessionTracking).filter(
            SessionTracking.session_id == session_id
        ).first()
        detected = session.traffic_source if session else (traffic_source or "unknown")
        self._ensure_session(db, session_id, detected)

        if booking_timestamp:
            time_spain = booking_timestamp
        elif event_start_time:
            if event_start_time.tzinfo:
                from datetime import timezone
                spain_tz = timezone(timedelta(hours=1))
                time_spain = event_start_time.astimezone(spain_tz).replace(tzinfo=None)
            else:
                time_spain = event_start_time + timedelta(hours=1)
        else:
            time_spain = datetime.utcnow() + timedelta(hours=1)

        booking = CalendlyBooking(
            session_id=session_id,
            traffic_source=detected,
            calendly_event_id=calendly_event_id,
            invitee_email=invitee_email,
            invitee_name=invitee_name,
            event_start_time=event_start_time,
            timestamp=time_spain,
            fecha=time_spain.date(),
            dia=time_spain.day,
            mes=time_spain.month,
            año=time_spain.year,
            hora=time_spain.time()
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    def get_traffic_stats(self, db: Session, days: int = 30):
        fecha_inicio = datetime.now() - timedelta(days=days)
        visits = db.query(
            PageVisit.traffic_source,
            func.count(PageVisit.id).label('total_visits'),
            func.count(distinct(PageVisit.session_id)).label('unique_visitors')
        ).filter(PageVisit.timestamp >= fecha_inicio).group_by(PageVisit.traffic_source).all()

        clicks = db.query(
            CalendlyClick.traffic_source,
            func.count(CalendlyClick.id).label('total_clicks')
        ).filter(CalendlyClick.timestamp >= fecha_inicio).group_by(CalendlyClick.traffic_source).all()

        bookings = db.query(
            CalendlyBooking.traffic_source,
            func.count(CalendlyBooking.id).label('total_bookings')
        ).filter(CalendlyBooking.timestamp >= fecha_inicio).group_by(CalendlyBooking.traffic_source).all()

        return {
            'visits':   [{'source': v.traffic_source, 'total': v.total_visits, 'unique': v.unique_visitors} for v in visits],
            'clicks':   [{'source': c.traffic_source, 'total': c.total_clicks} for c in clicks],
            'bookings': [{'source': b.traffic_source, 'total': b.total_bookings} for b in bookings],
        }

    def get_conversion_funnel(self, db: Session, traffic_source: str = None, days: int = 30):
        fecha_inicio = datetime.now() - timedelta(days=days)
        query_visits   = db.query(func.count(distinct(PageVisit.session_id)))
        query_clicks   = db.query(func.count(distinct(CalendlyClick.session_id)))
        query_bookings = db.query(func.count(CalendlyBooking.id))

        if traffic_source:
            query_visits   = query_visits.filter(PageVisit.traffic_source == traffic_source)
            query_clicks   = query_clicks.filter(CalendlyClick.traffic_source == traffic_source)
            query_bookings = query_bookings.filter(CalendlyBooking.traffic_source == traffic_source)

        query_visits   = query_visits.filter(PageVisit.timestamp >= fecha_inicio)
        query_clicks   = query_clicks.filter(CalendlyClick.timestamp >= fecha_inicio)
        query_bookings = query_bookings.filter(CalendlyBooking.timestamp >= fecha_inicio)

        total_visits   = query_visits.scalar() or 0
        total_clicks   = query_clicks.scalar() or 0
        total_bookings = query_bookings.scalar() or 0

        return {
            'visits':              total_visits,
            'clicks':              total_clicks,
            'bookings':            total_bookings,
            'click_rate':          round((total_clicks   / total_visits * 100) if total_visits > 0 else 0, 2),
            'booking_rate':        round((total_bookings / total_clicks * 100) if total_clicks > 0 else 0, 2),
            'overall_conversion':  round((total_bookings / total_visits * 100) if total_visits > 0 else 0, 2),
        }

    def get_stats_by_date(self, db: Session, days: int = 30):
        fecha_inicio = datetime.now() - timedelta(days=days)
        stats = db.query(
            PageVisit.fecha, PageVisit.dia, PageVisit.mes, PageVisit.año,
            func.count(PageVisit.id).label('visitas')
        ).filter(PageVisit.timestamp >= fecha_inicio
        ).group_by(PageVisit.fecha, PageVisit.dia, PageVisit.mes, PageVisit.año
        ).order_by(PageVisit.fecha.desc()).all()

        return [{'fecha': str(s.fecha), 'dia': s.dia, 'mes': s.mes, 'año': s.año, 'visitas': s.visitas} for s in stats]


tracking_crud = TrackingCRUD()