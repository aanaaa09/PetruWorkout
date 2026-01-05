# backend/sync_calendly.py
"""
Sincronización de reservas de Calendly con matching inteligente basado en UTM
"""
import requests
import os
from datetime import datetime, timedelta
from collections import Counter

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

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
    Obtiene eventos de Calendly y los vincula con clicks
    Matching basado en UTM parameters para detectar origen WhatsApp
    """
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        logger.info("🚂 Conectando a Railway via DATABASE_URL (GitHub Actions)")
        try:
            engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False
            )
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            logger.info("✅ Conexión a Railway exitosa")
        except Exception as e:
            logger.error(f"❌ Error conectando a Railway: {e}")
            return
    else:
        logger.info("💻 Conectando a BD local via settings")
        from backend.config.database import SessionLocal
        db = SessionLocal()

    try:
        if settings.CALENDLY_API_KEY == "test_key":
            logger.error("❌ CALENDLY_API_KEY es de test, no puede funcionar")
            return

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

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            logger.error(f"❌ Error API Calendly: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return

        events = response.json().get('collection', [])
        logger.info(f"📅 Total eventos encontrados: {len(events)}")

        if len(events) == 0:
            logger.info("ℹ️  No hay eventos en el rango de fechas")
            return

        # Filtrar eventos recientes (booking en últimas 26h)
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

        logger.info(f"📌 Eventos con booking reciente: {len(eventos_recientes)}")

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
            logger.info(f"📋 Procesando: {event_uri[-20:]}")

            # Comprobar si ya existe
            existe = db.query(CalendlyBooking).filter(
                CalendlyBooking.calendly_event_id == event_uri
            ).first()

            if existe:
                logger.info(f"   ⏭️  Ya existe en BD")
                reservas_existentes += 1
                continue

            logger.info(f"   ✨ NUEVO - obteniendo detalles...")

            # Obtener invitees
            invitees_url = f"{event_uri}/invitees"
            inv_response = requests.get(invitees_url, headers=headers, timeout=30)

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

            # ========================================
            # VERIFICAR SI EL EMAIL YA EXISTE
            # ========================================
            booking_existente = db.query(CalendlyBooking).filter(
                CalendlyBooking.invitee_email == email
            ).first()

            if booking_existente:
                logger.info(f"   ⚠️  EMAIL YA REGISTRADO en booking ID {booking_existente.id}")
                logger.info(f"   ℹ️  Evento anterior: {booking_existente.calendly_event_id[-20:]}")
                logger.info(f"   ⏭️  Saltando duplicado...")
                continue

            # Parsear fechas
            try:
                event_datetime = datetime.fromisoformat(event_start.replace("Z", "+00:00"))
            except:
                event_datetime = datetime.utcnow()

            try:
                if created_at:
                    booking_datetime = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    booking_datetime_naive = booking_datetime.replace(tzinfo=None)
                else:
                    booking_datetime_naive = datetime.utcnow()
            except:
                booking_datetime_naive = datetime.utcnow()

            logger.info(f"   🕐 Booking: {booking_datetime_naive.strftime('%Y-%m-%d %H:%M:%S')}")

            # ========================================
            # DETECTAR ORIGEN POR UTM PARAMETERS
            # ========================================
            tracking_data = invitee.get("tracking", {})
            utm_source = tracking_data.get("utm_source", "")
            utm_medium = tracking_data.get("utm_medium", "")

            viene_de_whatsapp = (utm_source == "whatsapp" or utm_medium == "whatsapp")

            if viene_de_whatsapp:
                logger.info(f"   📱 DETECTADO: Viene de WhatsApp (UTM)")
            else:
                logger.info(f"   🖥️  DETECTADO: Acceso directo a Calendly")

            # ========================================
            # MATCHING INTELIGENTE
            # ========================================
            ventana_dias = 7
            ventana_inicio = booking_datetime_naive - timedelta(days=ventana_dias)

            session_id = None
            traffic_source = "direct"
            via_whatsapp = False
            match_final = None

            if viene_de_whatsapp:
                # ========================================
                # CASO A: Viene de WhatsApp → Buscar clicks con via_whatsapp=True
                # ========================================
                logger.info(f"   🔍 Buscando clicks de WhatsApp (via_whatsapp=True) ANTERIORES al booking...")

                clicks_whatsapp = db.query(CalendlyClick).filter(
                    CalendlyClick.timestamp >= ventana_inicio,
                    CalendlyClick.timestamp < booking_datetime_naive,  # ANTES del booking
                    CalendlyClick.via_whatsapp == True
                ).order_by(
                    CalendlyClick.timestamp.desc()
                ).all()

                logger.info(f"   📊 Clicks WhatsApp encontrados (anteriores): {len(clicks_whatsapp)}")

                if clicks_whatsapp:
                    # Buscar el más cercano ANTERIOR
                    mejor_match = None
                    menor_diferencia = float('inf')

                    for click in clicks_whatsapp:
                        click_timestamp = click.timestamp.replace(tzinfo=None)

                        # Verificar que el click es ANTES del booking
                        if click_timestamp < booking_datetime_naive:
                            diferencia_segundos = (booking_datetime_naive - click_timestamp).total_seconds()

                            if diferencia_segundos < menor_diferencia:
                                menor_diferencia = diferencia_segundos
                                mejor_match = click

                    if mejor_match:
                        diferencia_minutos = menor_diferencia / 60
                        match_final = mejor_match
                        session_id = mejor_match.session_id
                        traffic_source = mejor_match.traffic_source
                        via_whatsapp = True

                        logger.info(f"   ✅ MATCH WhatsApp: {traffic_source} ({diferencia_minutos:.1f}min antes)")
                        logger.info(f"   📱 Button: {mejor_match.button_id}")
                        logger.info(f"   🕐 Click: {mejor_match.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    logger.info(f"   ℹ️  Sin clicks WhatsApp anteriores - usando traffic_source='whatsapp'")
                    traffic_source = "whatsapp"
                    via_whatsapp = True

            else:
                # ========================================
                # CASO B: Acceso directo → Buscar clicks con via_whatsapp=False
                # ========================================
                logger.info(f"   🔍 Buscando clicks directos a Calendly (via_whatsapp=False) ANTERIORES al booking...")

                clicks_calendly = db.query(CalendlyClick).filter(
                    CalendlyClick.timestamp >= ventana_inicio,
                    CalendlyClick.timestamp < booking_datetime_naive,  # ANTES del booking
                    CalendlyClick.via_whatsapp == False
                ).order_by(
                    CalendlyClick.timestamp.desc()
                ).all()

                logger.info(f"   📊 Clicks Calendly encontrados (anteriores): {len(clicks_calendly)}")

                if clicks_calendly:
                    # Buscar el más cercano ANTERIOR
                    mejor_match = None
                    menor_diferencia = float('inf')

                    for click in clicks_calendly:
                        click_timestamp = click.timestamp.replace(tzinfo=None)

                        # Verificar que el click es ANTES del booking
                        if click_timestamp < booking_datetime_naive:
                            diferencia_segundos = (booking_datetime_naive - click_timestamp).total_seconds()

                            if diferencia_segundos < menor_diferencia:
                                menor_diferencia = diferencia_segundos
                                mejor_match = click

                    if mejor_match:
                        diferencia_minutos = menor_diferencia / 60
                        match_final = mejor_match
                        session_id = mejor_match.session_id
                        traffic_source = mejor_match.traffic_source
                        via_whatsapp = False

                        logger.info(f"   ✅ MATCH Calendly: {traffic_source} ({diferencia_minutos:.1f}min antes)")
                        logger.info(f"   📱 Button: {mejor_match.button_id}")
                        logger.info(f"   🕐 Click: {mejor_match.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

            # ========================================
            # FALLBACK: Si no hay match, analizar visitas
            # ========================================
            if not match_final and not viene_de_whatsapp:
                logger.info(f"   🔍 Fallback: Analizando visitas...")

                visitas = db.query(PageVisit).filter(
                    PageVisit.timestamp >= ventana_inicio,
                    PageVisit.timestamp <= booking_datetime_naive
                ).order_by(PageVisit.timestamp.desc()).all()

                if visitas:
                    sources = [v.traffic_source for v in visitas]
                    source_counts = Counter(sources)
                    traffic_source = source_counts.most_common(1)[0][0]
                    logger.info(f"   📊 Source por visitas: {traffic_source}")
                else:
                    logger.info(f"   ℹ️  Sin visitas - usando 'direct'")

            # ========================================
            # GUARDAR EN BD
            # ========================================
            try:
                booking = tracking_crud.create_calendly_booking(
                    db=db,
                    calendly_event_id=event_uri,
                    invitee_email=email,
                    invitee_name=name,
                    event_start_time=event_datetime,
                    booking_timestamp=booking_datetime_naive,
                    session_id=session_id,
                    traffic_source=traffic_source,
                    via_whatsapp=via_whatsapp
                )

                db.flush()

                # Verificar que se guardó
                verificar = db.query(CalendlyBooking).filter(
                    CalendlyBooking.calendly_event_id == event_uri
                ).first()

                if verificar:
                    nuevas_reservas += 1
                    logger.info(f"   ✅ GUARDADO EN BD (ID: {verificar.id})")
                    logger.info(f"   🎯 Traffic Source: {traffic_source}")
                    logger.info(f"   {'📱 Via WhatsApp: SÍ' if via_whatsapp else '🖥️  Via Calendly: DIRECTO'}")
                else:
                    logger.error(f"   ❌ NO SE GUARDÓ EN BD")

            except Exception as e:
                logger.error(f"   ❌ Error guardando: {e}")
                db.rollback()
                import traceback
                traceback.print_exc()

        # Commit final
        try:
            db.commit()
            logger.info(f"\n💾 Commit final exitoso")
        except Exception as e:
            logger.error(f"❌ Error en commit final: {e}")
            db.rollback()

        # Resumen
        logger.info(f"\n{'=' * 60}")
        logger.info(f"🎉 SINCRONIZACIÓN COMPLETADA")
        logger.info(f"📊 Eventos totales: {len(eventos_recientes)}")
        logger.info(f"✨ Nuevas reservas: {nuevas_reservas}")
        logger.info(f"⏭️  Ya existentes: {reservas_existentes}")
        logger.info(f"{'=' * 60}\n")

    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()
        logger.info("🔌 Conexión cerrada")


if __name__ == "__main__":
    logger.info("🔄 Iniciando sync con Calendly...")
    sync_calendly_bookings()

