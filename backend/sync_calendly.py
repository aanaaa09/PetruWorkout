# backend/sync_calendly.py
import requests
from datetime import datetime, timedelta
from backend.config.database import SessionLocal
from backend.config.settings import settings
from backend.crud.tracking import tracking_crud
from backend.models.calendly_booking import CalendlyBooking
from backend.models.calendly_click import CalendlyClick
from backend.models.page_visit import PageVisit
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_calendly_bookings():
    """
    Obtiene eventos de Calendly de las últimas 24 horas
    y los vincula con los clicks registrados más cercanos previos.
    """
    # Obtener DATABASE_URL si existe (GitHub Actions), sino usar config normal
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(database_url)
        SessionLocal_temp = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal_temp()
    else:
        db = SessionLocal()

    try:
        headers = {
            'Authorization': f'Bearer {settings.CALENDLY_API_KEY}',
            'Content-Type': 'application/json'
        }

        # Buscar eventos de las últimas 26h + próximos 30 días
        min_time = (datetime.utcnow() - timedelta(hours=26)).isoformat() + "Z"
        max_time = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"

        url = "https://api.calendly.com/scheduled_events"
        params = {
            'user': settings.CALENDLY_USER_URI,
            'min_start_time': min_time,
            'max_start_time': max_time,
            'status': 'active',
            'count': 100
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            logger.error(f"❌ Error API Calendly: {response.status_code} - {response.text}")
            return

        events = response.json().get('collection', [])
        logger.info(f"📅 Eventos encontrados (últimas 26h + próximos 30 días): {len(events)}")

        # Filtrar solo eventos cuyo booking fue en las últimas 26h
        eventos_recientes = []
        ahora = datetime.utcnow()
        limite_booking = ahora - timedelta(hours=26)

        for event in events:
            created_at = event.get("created_at")
            if created_at:
                try:
                    created_datetime = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    if created_datetime.replace(tzinfo=None) >= limite_booking:
                        eventos_recientes.append(event)
                except:
                    eventos_recientes.append(event)
            else:
                eventos_recientes.append(event)

        logger.info(f"📌 Eventos con booking reciente (últimas 26h): {len(eventos_recientes)}")

        nuevas_reservas = 0

        for event in eventos_recientes:
            event_uri = event["uri"]
            event_start = event["start_time"]
            created_at = event.get("created_at")

            # Obtener datos del asistente
            invitees_url = f"{event_uri}/invitees"
            inv_response = requests.get(invitees_url, headers=headers)

            if inv_response.status_code != 200:
                logger.warning(f"⚠️ No se pudieron obtener invitees para {event_uri}")
                continue

            invitees = inv_response.json().get("collection", [])
            if not invitees:
                logger.warning(f"⚠️ Sin invitees para {event_uri}")
                continue

            invitee = invitees[0]
            email = invitee.get("email", "unknown@email.com")
            name = invitee.get("name", "Unknown")

            try:
                event_datetime = datetime.fromisoformat(event_start.replace("Z", "+00:00"))
            except:
                event_datetime = datetime.utcnow()

            try:
                if created_at:
                    booking_datetime = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                else:
                    booking_datetime = None
            except:
                booking_datetime = None

            # Comprobar si ya existe
            existe = db.query(CalendlyBooking).filter(
                CalendlyBooking.calendly_event_id == event_uri
            ).first()

            if existe:
                logger.info(f"⏭️ Ya existe: {email} - {event_uri[:30]}...")
                continue

            # Buscar click más cercano
            search_time = booking_datetime if booking_datetime else event_datetime

            clicks = db.query(CalendlyClick).filter(
                CalendlyClick.timestamp <= search_time
            ).order_by(
                CalendlyClick.timestamp.desc()
            ).limit(50).all()

            session_id = None
            traffic_source = "direct"

            if clicks:
                closest_click = min(
                    clicks,
                    key=lambda c: abs((search_time - c.timestamp).total_seconds())
                )

                diferencia_segundos = (search_time - closest_click.timestamp).total_seconds()
                if diferencia_segundos <= 7 * 24 * 3600:
                    session_id = closest_click.session_id
                    traffic_source = closest_click.traffic_source
                    logger.info(
                        f"🔗 Click vinculado: {traffic_source} ({diferencia_segundos / 3600:.1f}h antes del booking)")
                else:
                    logger.info(f"⏰ Click muy antiguo ({diferencia_segundos / 86400:.1f} días), marcando como 'direct'")
            else:
                logger.info(f"🔍 Sin clicks, buscando visitas alternativas...")
                visitas = db.query(PageVisit).filter(
                    PageVisit.timestamp >= search_time - timedelta(days=30),
                    PageVisit.timestamp <= search_time
                ).order_by(PageVisit.timestamp.desc()).limit(20).all()

                if visitas:
                    sources = [v.traffic_source for v in visitas]
                    traffic_source = max(set(sources), key=sources.count)
                    logger.info(f"📊 Usando source más común: {traffic_source}")

            # Guardar reserva
            tracking_crud.create_calendly_booking(
                db=db,
                calendly_event_id=event_uri,
                invitee_email=email,
                invitee_name=name,
                event_start_time=event_datetime,
                booking_timestamp=booking_datetime,
                session_id=session_id,
                traffic_source=traffic_source
            )

            nuevas_reservas += 1

            booking_time_str = booking_datetime.strftime("%Y-%m-%d %H:%M") if booking_datetime else "N/A"
            logger.info(f"✅ Reserva guardada: {email}")
            logger.info(f"   📅 Booking: {booking_time_str} | Reunión: {event_datetime.strftime('%Y-%m-%d %H:%M')}")
            logger.info(f"   🎯 Source: {traffic_source} | Session: {session_id[:10] if session_id else 'N/A'}")

        logger.info(f"🎉 Finalizado. Nuevas reservas: {nuevas_reservas}/{len(eventos_recientes)}")

        if nuevas_reservas > 0:
            logger.info(f"💾 Se guardaron {nuevas_reservas} nuevas reservas en la BD")
        else:
            logger.info(f"ℹ️ No hay reservas nuevas para procesar")

    except Exception as e:
        logger.error(f"❌ Error en sincronización: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    logger.info("🔄 Iniciando sync con Calendly...")
    sync_calendly_bookings()