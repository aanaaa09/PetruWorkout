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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_calendly_bookings():
    """
    Obtiene eventos de Calendly de las últimas 24 horas
    y los vincula con los clicks registrados más cercanos previos.
    """
    db = SessionLocal()

    try:
        headers = {
            'Authorization': f'Bearer {settings.CALENDLY_API_KEY}',
            'Content-Type': 'application/json'
        }

        # ✅ Buscar eventos de las últimas 26h (overlap de 2h para no perder nada)
        # Si el cron corre a las 18:37, busca desde ayer a las 16:37
        # Esto garantiza capturar eventos creados justo cuando corrió el cron anterior
        min_time = (datetime.utcnow() - timedelta(hours=26)).isoformat() + "Z"

        # También obtener eventos futuros (por si hay reservas para dentro de días)
        max_time = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"

        url = "https://api.calendly.com/scheduled_events"
        params = {
            'user': settings.CALENDLY_USER_URI,
            'min_start_time': min_time,
            'max_start_time': max_time,  # ✅ NUEVO: límite superior
            'status': 'active',
            'count': 100
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            logger.error(f"❌ Error API Calendly: {response.status_code} - {response.text}")
            return

        events = response.json().get('collection', [])
        logger.info(f"📅 Eventos encontrados (últimas 26h + próximos 30 días): {len(events)}")

        # ✅ Filtrar solo eventos cuyo booking (created_at) fue en las últimas 26h
        # Esto evita procesar reservas antiguas que solo tienen la reunión próxima
        eventos_recientes = []
        ahora = datetime.utcnow()
        limite_booking = ahora - timedelta(hours=26)

        for event in events:
            created_at = event.get("created_at")
            if created_at:
                try:
                    created_datetime = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    # Solo procesar si el booking fue en las últimas 26h
                    if created_datetime.replace(tzinfo=None) >= limite_booking:
                        eventos_recientes.append(event)
                except:
                    # Si no se puede parsear, incluirlo por seguridad
                    eventos_recientes.append(event)
            else:
                eventos_recientes.append(event)

        logger.info(f"📌 Eventos con booking reciente (últimas 26h): {len(eventos_recientes)}")

        nuevas_reservas = 0

        for event in eventos_recientes:
            event_uri = event["uri"]
            event_start = event["start_time"]

            # ✅ AQUÍ ESTÁ LA CLAVE: created_at es cuando rellenaron el formulario
            created_at = event.get("created_at")  # Hora real del booking

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

            # ✅ Convertir created_at a datetime (hora real del booking)
            try:
                if created_at:
                    booking_datetime = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                else:
                    booking_datetime = None
            except:
                booking_datetime = None

            # ✅ Comprobar si ya existe esta reserva EXACTA
            existe = db.query(CalendlyBooking).filter(
                CalendlyBooking.calendly_event_id == event_uri
            ).first()

            if existe:
                logger.info(f"⏭️ Ya existe: {email} - {event_uri[:30]}...")
                continue

            # ✅ BUSCAR CLICK MÁS CERCANO a la hora del BOOKING (no del evento)
            search_time = booking_datetime if booking_datetime else event_datetime

            clicks = db.query(CalendlyClick).filter(
                CalendlyClick.timestamp <= search_time  # Solo clicks ANTES del booking
            ).order_by(
                CalendlyClick.timestamp.desc()  # Más reciente primero
            ).limit(50).all()

            session_id = None
            traffic_source = "direct"

            if clicks:
                # Encontrar el click MÁS CERCANO al momento del booking
                closest_click = min(
                    clicks,
                    key=lambda c: abs((search_time - c.timestamp).total_seconds())
                )

                # Solo vincular si el click fue en los últimos 7 días
                diferencia_segundos = (search_time - closest_click.timestamp).total_seconds()
                if diferencia_segundos <= 7 * 24 * 3600:  # 7 días
                    session_id = closest_click.session_id
                    traffic_source = closest_click.traffic_source
                    logger.info(
                        f"🔗 Click vinculado: {traffic_source} ({diferencia_segundos / 3600:.1f}h antes del booking)")
                else:
                    logger.info(f"⏰ Click muy antiguo ({diferencia_segundos / 86400:.1f} días), marcando como 'direct'")
            else:
                # Si no hay clicks, buscar visitas
                logger.info(f"🔍 Sin clicks, buscando visitas alternativas...")
                visitas = db.query(PageVisit).filter(
                    PageVisit.timestamp >= search_time - timedelta(days=30),
                    PageVisit.timestamp <= search_time
                ).order_by(PageVisit.timestamp.desc()).limit(20).all()

                if visitas:
                    sources = [v.traffic_source for v in visitas]
                    traffic_source = max(set(sources), key=sources.count)
                    logger.info(f"📊 Usando source más común: {traffic_source}")

            # ✅ Guardar reserva CON LA HORA REAL DEL BOOKING
            tracking_crud.create_calendly_booking(
                db=db,
                calendly_event_id=event_uri,
                invitee_email=email,
                invitee_name=name,
                event_start_time=event_datetime,
                booking_timestamp=booking_datetime,  # ← NUEVO: hora real del booking
                session_id=session_id,
                traffic_source=traffic_source
            )

            nuevas_reservas += 1

            booking_time_str = booking_datetime.strftime("%Y-%m-%d %H:%M") if booking_datetime else "N/A"
            logger.info(f"✅ Reserva guardada: {email}")
            logger.info(f"   📅 Booking: {booking_time_str} | Reunión: {event_datetime.strftime('%Y-%m-%d %H:%M')}")
            logger.info(f"   🎯 Source: {traffic_source} | Session: {session_id[:10] if session_id else 'N/A'}")

        logger.info(f"🎉 Finalizado. Nuevas reservas: {nuevas_reservas}/{len(eventos_recientes)}")

        # ✅ Log final con estadísticas
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