from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time, func
from backend.config.database import Base


class PageVisit(Base):
    """Visitas a la página web con detección de origen de tráfico"""
    __tablename__ = "page_visits"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    traffic_source = Column(String(50), nullable=False, index=True)
    referrer_url = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    landing_page = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Timestamp completo
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Campos separados para análisis
    fecha = Column(Date, nullable=False, index=True)  # Fecha completa (YYYY-MM-DD)
    dia = Column(Integer, nullable=False, index=True)  # 1-31
    mes = Column(Integer, nullable=False, index=True)  # 1-12
    año = Column(Integer, nullable=False, index=True)  # 2024, 2025, etc.
    hora = Column(Time, nullable=False, index=True)  # HH:MM:SS