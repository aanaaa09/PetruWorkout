from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Boolean, func, Index
from backend.config.database import Base


class CalendlyBooking(Base):
    """Reservas completadas en Calendly (vía webhook)"""
    __tablename__ = "calendly_bookings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    traffic_source = Column(String(50), nullable=True, index=True)
    calendly_event_id = Column(String(255), unique=True, nullable=False, index=True)
    invitee_email = Column(String(255), nullable=True, index=True)
    invitee_name = Column(String(255), nullable=True)
    event_start_time = Column(DateTime(timezone=True), nullable=True, index=True)

    # NUEVO - Tracking de WhatsApp
    via_whatsapp = Column(Boolean, default=False, nullable=False, index=True)

    # Timestamp completo
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Campos separados para análisis
    fecha = Column(Date, nullable=False, index=True)
    dia = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    año = Column(Integer, nullable=False)
    hora = Column(Time, nullable=False)

    # ÍNDICES COMPUESTOS OPTIMIZADOS
    __table_args__ = (
        # Para calcular conversiones por fuente
        Index('ix_calendly_bookings_source_fecha', 'traffic_source', 'fecha'),

        # Para análisis temporal de conversiones
        Index('ix_calendly_bookings_año_mes', 'año', 'mes'),

        # Para vincular con el embudo completo
        Index('ix_calendly_bookings_session_timestamp', 'session_id', 'timestamp'),

        # Para detectar usuarios recurrentes
        Index('ix_calendly_bookings_email_fecha', 'invitee_email', 'fecha'),

        # Para consultas de conversión vía WhatsApp
        Index('ix_calendly_bookings_whatsapp_source', 'via_whatsapp', 'traffic_source'),

        # Para análisis temporal de WhatsApp
        Index('ix_calendly_bookings_whatsapp_fecha', 'via_whatsapp', 'fecha'),
    )