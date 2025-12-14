from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from ..models.page_visit import PageVisit
from ..models.calendly_click import CalendlyClick
from ..models.calendly_booking import CalendlyBooking
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TrackingCRUD:
    """CRUD para tracking de conversión"""

    def create_page_visit(
            self,
            db: Session,
            session_id: str,
            traffic_source: str,
            referrer_url: str = None,
            user_agent: str = None,
            landing_page: str = None
            # ❌ ELIMINADO: ip_address
    ) -> PageVisit:
        """Registra una visita a la página"""
        now_utc = datetime.utcnow()
        now_spain = now_utc + timedelta(hours=1)

        visit = PageVisit(
            session_id=session_id,
            traffic_source=traffic_source,
            referrer_url=referrer_url,
            user_agent=user_agent,
            landing_page=landing_page,
            # ❌ ELIMINADO: ip_address=ip_address,
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

    def create_calendly_click(
            self,
            db: Session,
            session_id: str,
            traffic_source: str,
            button_id: str = None,
            button_location: str = None,
            page_url: str = None
    ) -> CalendlyClick:
        """Registra un click en botón de Calendly"""
        now_utc = datetime.utcnow()
        now_spain = now_utc + timedelta(hours=1)

        click = CalendlyClick(
            session_id=session_id,
            traffic_source=traffic_source,
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

    def create_calendly_booking(
            self,
            db: Session,
            calendly_event_id: str,
            invitee_email: str = None,
            invitee_name: str = None,
            event_start_time: datetime = None,
            session_id: str = None,
            traffic_source: str = None
    ) -> CalendlyBooking:
        """Registra una reserva completada en Calendly"""
        now_utc = datetime.utcnow()
        now_spain = now_utc + timedelta(hours=1)

        booking = CalendlyBooking(
            session_id=session_id,
            traffic_source=traffic_source,
            calendly_event_id=calendly_event_id,
            invitee_email=invitee_email,
            invitee_name=invitee_name,
            event_start_time=event_start_time,
            timestamp=now_spain,
            fecha=now_spain.date(),
            dia=now_spain.day,
            mes=now_spain.month,
            año=now_spain.year,
            hora=now_spain.time()
        )
        db.add(booking)
        db.commit()
        return booking

    def get_traffic_stats(self, db: Session, days: int = 30):
        """Obtiene estadísticas de tráfico por fuente"""
        fecha_inicio = datetime.now() - timedelta(days=days)

        visits = db.query(
            PageVisit.traffic_source,
            func.count(PageVisit.id).label('total_visits'),
            func.count(distinct(PageVisit.session_id)).label('unique_visitors')
        ).filter(
            PageVisit.timestamp >= fecha_inicio
        ).group_by(
            PageVisit.traffic_source
        ).all()

        clicks = db.query(
            CalendlyClick.traffic_source,
            func.count(CalendlyClick.id).label('total_clicks')
        ).filter(
            CalendlyClick.timestamp >= fecha_inicio
        ).group_by(
            CalendlyClick.traffic_source
        ).all()

        bookings = db.query(
            CalendlyBooking.traffic_source,
            func.count(CalendlyBooking.id).label('total_bookings')
        ).filter(
            CalendlyBooking.timestamp >= fecha_inicio
        ).group_by(
            CalendlyBooking.traffic_source
        ).all()

        return {
            'visits': [{'source': v.traffic_source, 'total': v.total_visits, 'unique': v.unique_visitors} for v in visits],
            'clicks': [{'source': c.traffic_source, 'total': c.total_clicks} for c in clicks],
            'bookings': [{'source': b.traffic_source, 'total': b.total_bookings} for b in bookings]
        }

    def get_conversion_funnel(self, db: Session, traffic_source: str = None, days: int = 30):
        """Obtiene el embudo de conversión completo"""
        fecha_inicio = datetime.now() - timedelta(days=days)

        query_visits = db.query(func.count(distinct(PageVisit.session_id)))
        query_clicks = db.query(func.count(distinct(CalendlyClick.session_id)))
        query_bookings = db.query(func.count(CalendlyBooking.id))

        if traffic_source:
            query_visits = query_visits.filter(PageVisit.traffic_source == traffic_source)
            query_clicks = query_clicks.filter(CalendlyClick.traffic_source == traffic_source)
            query_bookings = query_bookings.filter(CalendlyBooking.traffic_source == traffic_source)

        query_visits = query_visits.filter(PageVisit.timestamp >= fecha_inicio)
        query_clicks = query_clicks.filter(CalendlyClick.timestamp >= fecha_inicio)
        query_bookings = query_bookings.filter(CalendlyBooking.timestamp >= fecha_inicio)

        total_visits = query_visits.scalar() or 0
        total_clicks = query_clicks.scalar() or 0
        total_bookings = query_bookings.scalar() or 0

        click_rate = (total_clicks / total_visits * 100) if total_visits > 0 else 0
        booking_rate = (total_bookings / total_clicks * 100) if total_clicks > 0 else 0
        overall_conversion = (total_bookings / total_visits * 100) if total_visits > 0 else 0

        return {
            'visits': total_visits,
            'clicks': total_clicks,
            'bookings': total_bookings,
            'click_rate': round(click_rate, 2),
            'booking_rate': round(booking_rate, 2),
            'overall_conversion': round(overall_conversion, 2)
        }

    def get_stats_by_date(self, db: Session, days: int = 30):
        """Obtiene estadísticas agrupadas por fecha"""
        fecha_inicio = datetime.now() - timedelta(days=days)

        stats = db.query(
            PageVisit.fecha,
            PageVisit.dia,
            PageVisit.mes,
            PageVisit.año,
            func.count(PageVisit.id).label('visitas')
        ).filter(
            PageVisit.timestamp >= fecha_inicio
        ).group_by(
            PageVisit.fecha,
            PageVisit.dia,
            PageVisit.mes,
            PageVisit.año
        ).order_by(
            PageVisit.fecha.desc()
        ).all()

        return [
            {
                'fecha': str(s.fecha),
                'dia': s.dia,
                'mes': s.mes,
                'año': s.año,
                'visitas': s.visitas
            } for s in stats
        ]


tracking_crud = TrackingCRUD()