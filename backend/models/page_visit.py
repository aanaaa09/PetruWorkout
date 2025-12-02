from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time, func, Index
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
    fecha = Column(Date, nullable=False, index=True)
    dia = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    año = Column(Integer, nullable=False)
    hora = Column(Time, nullable=False)

    # ÍNDICES COMPUESTOS para optimizar consultas analíticas
    __table_args__ = (
        # Para filtrar por fuente de tráfico y fecha (análisis por canal)
        Index('ix_page_visits_source_fecha', 'traffic_source', 'fecha'),

        # Para análisis temporal (conversiones por mes/año)
        Index('ix_page_visits_año_mes', 'año', 'mes'),

        # Para análisis de embudo (session_id + timestamp)
        Index('ix_page_visits_session_timestamp', 'session_id', 'timestamp'),

        # Para análisis diario por fuente
        Index('ix_page_visits_source_año_mes_dia', 'traffic_source', 'año', 'mes', 'dia'),
    )