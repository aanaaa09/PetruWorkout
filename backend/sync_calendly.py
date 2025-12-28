# backend/sync_calendly.py
import requests
import os
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


def analizar_patron_trafico(db, booking_datetime, clicks_previos):
    """
    Analiza el patrón de tráfico cuando el click más cercano es muy antiguo
    """
    from collections import Counter
    sources = [c.traffic_source for c in clicks_previos]

    if not sources:
        return "direct"

    source_counts = Counter(sources)

    # Si hay un source claramente dominante (>50%), usarlo
    total = len(sources)
    for source, count in source_counts.most_common():
        if count / total > 0.5:
            return source

    # Sino, usar el más reciente de los más comunes
    top_sources = [s for s, c in source_counts.most_common(3)]

    for click in clicks_previos:
        if click.traffic_source in top_sources:
            return click.traffic_source

    return "direct"


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
            created_at = event.get("created_at")  # ← Hora real del booking

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

            # ✅ CLAVE: Usar created_at (hora del booking) para matching
            try:
                if created_at:
                    booking_datetime = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                else:
                    booking_datetime = event_datetime
            except:
                booking_datetime = event_datetime

            # Quitar timezone para comparaciones
            booking_datetime_naive = booking_datetime.replace(tzinfo=None)

            logger.info(f"\n🔍 Procesando: {email}")
            logger.info(f"   📅 Booking realizado: {booking_datetime_naive.strftime('%Y-%m-%d %H:%M:%S')}")

            # Comprobar si ya existe
            existe = db.query(CalendlyBooking).filter(
                CalendlyBooking.calendly_event_id == event_uri
            ).first()

            if existe:
                logger.info(f"⏭️  Ya existe en BD, saltando...")
                continue

            # ========================================
            # 🎯 ALGORITMO MEJORADO DE MATCHING
            # ========================================

            # PASO 1: Buscar clicks ANTES del booking (ventana de 7 días)
            ventana_dias = 7
            ventana_inicio = booking_datetime_naive - timedelta(days=ventana_dias)

            clicks_previos = db.query(CalendlyClick).filter(
                CalendlyClick.timestamp >= ventana_inicio,
                CalendlyClick.timestamp <= booking_datetime_naive
            ).order_by(
                CalendlyClick.timestamp.desc()
            ).all()

            logger.info(f"   🔎 Clicks encontrados en ventana de {ventana_dias} días: {len(clicks_previos)}")

            session_id = None
            traffic_source = "direct"
            mejor_match = None
            mejor_diferencia = float('inf')

            if clicks_previos:
                # Encontrar el click MÁS CERCANO al booking
                for click in clicks_previos:
                    # Calcular diferencia en segundos
                    diferencia_segundos = (booking_datetime_naive - click.timestamp).total_seconds()

                    # Solo considerar clicks que fueron ANTES del booking
                    if diferencia_segundos >= 0:
                        if diferencia_segundos < mejor_diferencia:
                            mejor_diferencia = diferencia_segundos
                            mejor_match = click

                if mejor_match:
                    diferencia_horas = mejor_diferencia / 3600
                    diferencia_minutos = (mejor_diferencia % 3600) / 60


                    if diferencia_horas <= 2:
                        # Match PERFECTO: click en las últimas 2 horas
                        session_id = mejor_match.session_id
                        traffic_source = mejor_match.traffic_source
                        logger.info(f"   ✅ MATCH PERFECTO: {traffic_source}")
                        logger.info(f"      ⏱️  Click hace {int(diferencia_horas)}h {int(diferencia_minutos)}min")
                        logger.info(f"      🆔 Session: {session_id[:10]}...")

                    elif diferencia_horas <= 24:
                        # Match BUENO: click en las últimas 24 horas
                        session_id = mejor_match.session_id
                        traffic_source = mejor_match.traffic_source
                        logger.info(f"   ✅ MATCH BUENO: {traffic_source}")
                        logger.info(f"      ⏱️  Click hace {int(diferencia_horas)}h {int(diferencia_minutos)}min")
                        logger.info(f"      🆔 Session: {session_id[:10]}...")

                    elif diferencia_horas <= 72:
                        # Match ACEPTABLE: click en los últimos 3 días
                        session_id = mejor_match.session_id
                        traffic_source = mejor_match.traffic_source
                        logger.info(f"   ⚠️  MATCH ACEPTABLE: {traffic_source}")
                        logger.info(f"      ⏱️  Click hace {diferencia_horas:.1f}h ({diferencia_horas / 24:.1f} días)")
                        logger.info(f"      🆔 Session: {session_id[:10]}...")

                    else:
                        # Click muy antiguo, usar análisis de tráfico
                        logger.info(f"   ⚠️  Click más cercano es muy antiguo ({diferencia_horas / 24:.1f} días)")
                        logger.info(f"   📊 Analizando patrón de tráfico...")
                        traffic_source = analizar_patron_trafico(db, booking_datetime_naive, clicks_previos)
                        logger.info(f"   🎯 Source inferido por patrón: {traffic_source}")
                else:
                    logger.info(f"   ⚠️  No hay clicks válidos antes del booking")

            # PASO 2: Si no hay clicks, analizar visitas
            if traffic_source == "direct":
                logger.info(f"   🔍 Sin clicks válidos, buscando visitas...")
                visitas = db.query(PageVisit).filter(
                    PageVisit.timestamp >= ventana_inicio,
                    PageVisit.timestamp <= booking_datetime_naive
                ).order_by(PageVisit.timestamp.desc()).all()

                if visitas:
                    # Contar sources más frecuentes
                    sources = [v.traffic_source for v in visitas]
                    from collections import Counter
                    source_counts = Counter(sources)
                    traffic_source = source_counts.most_common(1)[0][0]
                    logger.info(
                        f"   📊 Source más común en visitas: {traffic_source} ({source_counts[traffic_source]} visitas)")
                else:
                    logger.info(f"   ℹ️  Sin visitas registradas, marcando como 'direct'")

            # ========================================
            # 💾 GUARDAR RESERVA
            # ========================================
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
            logger.info(f"   ✅ Reserva guardada en BD")
            logger.info(f"   📧 Email: {email}")
            logger.info(f"   🎯 Source final: {traffic_source}")

        logger.info(f"\n{'=' * 60}")
        logger.info(f"🎉 FINALIZADO")
        logger.info(f"📊 Nuevas reservas procesadas: {nuevas_reservas}/{len(eventos_recientes)}")
        logger.info(f"{'=' * 60}\n")

    except Exception as e:
        logger.error(f"❌ Error en sincronización: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    logger.info("🔄 Iniciando sync con Calendly...")
    sync_calendly_bookings()