from sqlalchemy import Column, Integer, String, DateTime, func
from backend.config.database import Base


class CalendlyBooking(Base):
    """Reservas completadas en Calendly (vía webhook)"""
    __tablename__ = "calendly_bookings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    traffic_source = Column(String(50), nullable=True, index=True)
    calendly_event_id = Column(String(255), unique=True, nullable=False)
    invitee_email = Column(String(255), nullable=True)
    invitee_name = Column(String(255), nullable=True)
    event_start_time = Column(DateTime(timezone=True), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())