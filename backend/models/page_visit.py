from sqlalchemy import Column, Integer, String, Text, DateTime, func
from backend.config.database import Base


class PageVisit(Base):
    """Visitas a la página web con detección de origen de tráfico"""
    __tablename__ = "page_visits"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    traffic_source = Column(String(50), nullable=False,
                            index=True)  # instagram, tiktok, youtube, linkedin, direct, organic_search, unknown
    referrer_url = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    landing_page = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)