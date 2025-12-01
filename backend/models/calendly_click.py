from sqlalchemy import Column, Integer, String, DateTime, func
from backend.config.database import Base


class CalendlyClick(Base):
    """Clicks en botones que llevan a Calendly"""
    __tablename__ = "calendly_clicks"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    traffic_source = Column(String(50), nullable=False, index=True)
    button_id = Column(String(100), nullable=True)
    button_location = Column(String(100), nullable=True)  # hero, navbar, footer, services, etc.
    page_url = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)