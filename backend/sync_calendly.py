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
    Obtiene eventos de Calendly y los vincula con clicks
    """
    # Obtener DATABASE_URL si existe (GitHub Actions), sino usar config normal
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(database_url)
        SessionLocal_temp = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal_temp()
        logger.info("📊 Conectado a Railway vía DATABASE_URL")
    else:
        db = SessionLocal()
        logger.info("📊 Conectado a BD local")

    try:
        headers = {
            'Authorization': f'Bearer {settings.CALENDLY_API_KEY}',
            'Content-Type': 'application/json'
        }

        # Buscar eventos de las últimas 26h + próximos 30 días
        min_time = (datetime.utcnow() - timedelta(hours=26)).isoformat() + "Z"
        max_time = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"

        logger.info(f"🔍 Buscando eventos desde: {min_time}")

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
            logger.error(f"❌ Error API Calendly: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return

        events = response.json().get('collection', [])
        logger.info(f"📅 Total eventos encontrados: {len(events)}")

        # Filtrar eventos recientes
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

        if len(eventos_recientes) == 0:
            logger.info("ℹ️  No hay eventos nuevos para procesar")
            return

        nuevas_reservas = 0
        reservas_existentes = 0

        for event in eventos_recientes:
            event_uri = event["uri"]
            event_start = event["start_time"]
            created_at = event.get("created_at")

            logger.info(f"\n{'=' * 60}")
            logger.info(f"📋 Procesando evento: {event_uri[-20:]}")

            # Comprobar si ya existe
            existe = db.query(CalendlyBooking).filter(
                CalendlyBooking.calendly_event_id == event_uri
            ).first()

            if existe:
                logger.info(f"   ⏭️  Ya existe en BD, saltando...")
                reservas_existentes += 1
                continue

            logger.info(f"   ✨ NUEVO - obteniendo detalles...")

            # Obtener datos del asistente
            invitees_url = f"{event_uri}/invitees"
            inv_response = requests.get(invitees_url, headers=headers)

            if inv_response.status_code != 200:
                logger.warning(f"   ⚠️  Error obteniendo invitees")
                continue

            invitees = inv_response.json().get("collection", [])
            if not invitees:
                logger.warning(f"   ⚠️  Sin invitees")
                continue

            invitee = invitees[0]
            email = invitee.get("email", "unknown@email.com")
            name = invitee.get("name", "Unknown")

            logger.info(f"   👤 {name} ({email})")

            # Parsear fechas
            try:
                event_datetime = datetime.fromisoformat(event_start.replace("Z", "+00:00"))
            except:
                event_datetime = datetime.utcnow()

            # ✅ FIX: Convertir booking_datetime a naive inmediatamente
            try:
                if created_at:
                    booking_datetime = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    booking_datetime_naive = booking_datetime.replace(tzinfo=None)  # ← QUITAR TIMEZONE
                else:
                    booking_datetime_naive = datetime.utcnow()
            except:
                booking_datetime_naive = datetime.utcnow()

            logger.info(f"   🕐 Booking: {booking_datetime_naive.strftime('%Y-%m-%d %H:%M:%S')}")

            # ========================================
            # 🎯 MATCHING MEJORADO DE TRÁFICO
            # ========================================

            ventana_dias = 7
            ventana_inicio = booking_datetime_naive - timedelta(days=ventana_dias)

            clicks_previos = db.query(CalendlyClick).filter(
                CalendlyClick.timestamp >= ventana_inicio,
                CalendlyClick.timestamp <= booking_datetime_naive
            ).order_by(
                CalendlyClick.timestamp.desc()
            ).all()

            logger.info(f"   🔎 Clicks en ventana de {ventana_dias} días: {len(clicks_previos)}")

            session_id = None
            traffic_source = "direct"
            mejor_match = None
            mejor_diferencia = float('inf')

            if clicks_previos:
                # Encontrar el click MÁS CERCANO
                for click in clicks_previos:
                    diferencia_segundos = abs((booking_datetime_naive - click.timestamp).total_seconds())

                    if diferencia_segundos < mejor_diferencia:
                        mejor_diferencia = diferencia_segundos
                        mejor_match = click

                if mejor_match:
                    diferencia_horas = mejor_diferencia / 3600
                    diferencia_minutos = (mejor_diferencia % 3600) / 60

                    session_id = mejor_match.session_id
                    traffic_source = mejor_match.traffic_source

                    # Clasificar por calidad del match
                    if diferencia_horas <= 2:
                        logger.info(f"   ✅ MATCH PERFECTO: {traffic_source}")
                        logger.info(f"      ⏱️  Click hace {int(diferencia_horas)}h {int(diferencia_minutos)}min")
                    elif diferencia_horas <= 24:
                        logger.info(f"   ✅ MATCH BUENO: {traffic_source}")
                        logger.info(f"      ⏱️  Click hace {int(diferencia_horas)}h")
                    elif diferencia_horas <= 72:
                        logger.info(f"   ⚠️  MATCH ACEPTABLE: {traffic_source}")
                        logger.info(f"      ⏱️  Click hace {diferencia_horas / 24:.1f} días")
                    else:
                        # Click muy antiguo, analizar patrón
                        logger.info(f"   ⚠️  Click antiguo ({diferencia_horas / 24:.1f} días)")
                        traffic_source = analizar_patron_trafico(db, booking_datetime_naive, clicks_previos)
                        logger.info(f"   📊 Source por patrón: {traffic_source}")

                    logger.info(f"      🆔 Session: {session_id[:10]}...")
                else:
                    logger.info(f"   ⚠️  Sin clicks válidos")
            else:
                logger.info(f"   ℹ️  Sin clicks en ventana")

            # Fallback a visitas si es "direct"
            if traffic_source == "direct":
                logger.info(f"   🔍 Buscando en visitas...")
                visitas = db.query(PageVisit).filter(
                    PageVisit.timestamp >= ventana_inicio,
                    PageVisit.timestamp <= booking_datetime_naive
                ).order_by(PageVisit.timestamp.desc()).all()

                if visitas:
                    from collections import Counter
                    sources = [v.traffic_source for v in visitas]
                    source_counts = Counter(sources)
                    traffic_source = source_counts.most_common(1)[0][0]
                    logger.info(f"   📊 Source por visitas: {traffic_source} ({source_counts[traffic_source]} visitas)")
                else:
                    logger.info(f"   ℹ️  Sin visitas, usando 'direct'")

            # ========================================
            # 💾 GUARDAR EN BD
            # ========================================
            try:
                tracking_crud.create_calendly_booking(
                    db=db,
                    calendly_event_id=event_uri,
                    invitee_email=email,
                    invitee_name=name,
                    event_start_time=event_datetime,
                    booking_timestamp=booking_datetime_naive,
                    session_id=session_id,
                    traffic_source=traffic_source
                )

                nuevas_reservas += 1
                logger.info(f"   ✅ GUARDADO en BD")
                logger.info(f"   🎯 Source final: {traffic_source}")

            except Exception as e:
                logger.error(f"   ❌ Error guardando: {e}")
                import traceback
                traceback.print_exc()

        # ========================================
        # 📊 RESUMEN FINAL
        # ========================================
        logger.info(f"\n{'=' * 60}")
        logger.info(f"🎉 SINCRONIZACIÓN COMPLETADA")
        logger.info(f"📊 Eventos totales: {len(eventos_recientes)}")
        logger.info(f"✨ Reservas NUEVAS: {nuevas_reservas}")
        logger.info(f"⏭️  Ya existentes: {reservas_existentes}")
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