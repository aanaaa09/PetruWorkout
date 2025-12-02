# backend/sync_calendly.py
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.config.database import SessionLocal
from backend.config.settings import settings
from backend.crud.tracking import tracking_crud
from backend.models.calendly_booking import CalendlyBooking
from backend.models.calendly_click import CalendlyClick
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_calendly_bookings():
    """
    Obtiene eventos de Calendly de las últimas 24 horas
    y los vincula con los clicks registrados
    """
    db = SessionLocal()

    try:
        headers = {
            'Authorization': f'Bearer {settings.CALENDLY_API_KEY}',
            'Content-Type': 'application/json'
        }

        # Obtener eventos de las últimas 24 horas
        min_time = (datetime.now() - timedelta(hours=24)).isoformat()

        url = "https://api.calendly.com/scheduled_events"
        params = {
            'user': settings.CALENDLY_USER_URI,
            'min_start_time': min_time,
            'status': 'active',
            'count': 100
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            logger.error(f"Error API Calendly: {response.status_code} - {response.text}")
            return

        events = response.json().get('collection', [])
        logger.info(f"📅 Encontrados {len(events)} eventos en Calendly")

        nuevas_reservas = 0

        for event in events:
            event_uri = event['uri']
            event_start = event['start_time']

            # Obtener datos del invitee
            invitees_url = f"{event_uri}/invitees"
            inv_response = requests.get(invitees_url, headers=headers)

            if inv_response.status_code != 200:
                logger.warning(f"No se pudo obtener invitee para {event_uri}")
                continue

            invitees = inv_response.json().get('collection', [])
            if not invitees:
                continue

            invitee = invitees[0]
            email = invitee.get('email')
            name = invitee.get('name')

            # Parsear fecha
            try:
                event_datetime = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
            except:
                event_datetime = datetime.now()

            # ✅ VERIFICAR SI YA EXISTE POR EMAIL Y FECHA (más confiable)
            existe = db.query(CalendlyBooking).filter(
                CalendlyBooking.invitee_email == email,
                CalendlyBooking.event_start_time == event_datetime
            ).first()

            if existe:
                logger.info(f"⏭️  Reserva duplicada ignorada: {email} - {event_datetime}")
                continue  # Ya está registrada

            # Buscar session_id y traffic_source del último click antes de la reserva
            time_window = datetime.now() - timedelta(hours=48)

            last_click = db.query(CalendlyClick).filter(
                CalendlyClick.timestamp >= time_window,
                CalendlyClick.timestamp <= event_datetime
            ).order_by(CalendlyClick.timestamp.desc()).first()

            session_id = last_click.session_id if last_click else None
            traffic_source = last_click.traffic_source if last_click else 'calendly_api'

            # Crear booking
            tracking_crud.create_calendly_booking(
                db=db,
                calendly_event_id=event_uri,
                invitee_email=email,
                invitee_name=name,
                event_start_time=event_datetime,
                session_id=session_id,
                traffic_source=traffic_source
            )

            nuevas_reservas += 1
            logger.info(f"✅ Nueva reserva: {email} - Fuente: {traffic_source}")

        logger.info(f"🎉 Sincronización completada: {nuevas_reservas} nuevas reservas")

    except Exception as e:
        logger.error(f"❌ Error en sync: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    logger.info("🔄 Iniciando sincronización con Calendly...")
    sync_calendly_bookings()