# backend/send_fuerza_sequence.py
"""
Script diario ejecutado por GitHub Actions.

Para cada lead registrado, calcula cuántos días han pasado desde fecha_registro
y envía el email de la secuencia que corresponda (días 1, 3, 4, 5).

El día 0 ya se envió en el momento del registro desde el router de fuerza.

"""

import sys
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config.settings import settings
from backend.models.usuario import Usuario, TipoUsuario
from backend.services.email_sequence_service import SEQUENCE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# Días en los que se envía email de la secuencia de fuerza
SEQUENCE_DAYS = set(SEQUENCE.keys())   # {1, 3, 4, 5}


def get_db_session():
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()


def days_since_registration(fecha_registro: datetime) -> int:
    """Devuelve días completos transcurridos desde el registro (hora España)."""
    spain_tz = timezone(timedelta(hours=1))
    now = datetime.now(spain_tz)

    # Normalizar fecha_registro a timezone-aware si viene naive
    if fecha_registro.tzinfo is None:
        fecha_registro = fecha_registro.replace(tzinfo=spain_tz)
    else:
        fecha_registro = fecha_registro.astimezone(spain_tz)

    return (now.date() - fecha_registro.date()).days


def run():
    db = get_db_session()
    try:
        # Solo usuarios tipo NEWSLETTER (los leads del test de fuerza se guardan así)
        leads = db.query(Usuario).filter(
            Usuario.tipo_usuario == TipoUsuario.NEWSLETTER,
            Usuario.fecha_registro.isnot(None),
        ).all()

        logger.info(f"Leads encontrados: {len(leads)}")

        enviados = 0
        errores  = 0

        for lead in leads:
            dias = days_since_registration(lead.fecha_registro)

            if dias not in SEQUENCE_DAYS:
                continue

            send_fn = SEQUENCE[dias]
            logger.info(f"Enviando día {dias} a {lead.email} (registrado hace {dias} días)")

            try:
                ok = send_fn(to_email=lead.email, nombre=lead.nombre)
                if ok:
                    enviados += 1
                    logger.info(f"  ✓ Día {dias} enviado a {lead.email}")
                else:
                    errores += 1
                    logger.warning(f"  ✗ Fallo al enviar día {dias} a {lead.email}")
            except Exception as e:
                errores += 1
                logger.error(f"  ✗ Error enviando día {dias} a {lead.email}: {e}")

        logger.info(f"Resumen: {enviados} enviados, {errores} errores")
        return errores == 0

    finally:
        db.close()


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)