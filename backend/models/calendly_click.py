from sqlalchemy import Column, Integer, String, DateTime, Date, Time, func, Index
from backend.config.database import Base


class CalendlyClick(Base):
    """Clicks en botones que llevan a Calendly"""
    __tablename__ = "calendly_clicks"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    traffic_source = Column(String(50), nullable=False, index=True)
    button_id = Column(String(100), nullable=True)
    button_location = Column(String(100), nullable=True, index=True)  # AÑADIR INDEX
    page_url = Column(String(255), nullable=True)

    # Timestamp completo
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Campos separados para análisis
    fecha = Column(Date, nullable=False, index=True)
    dia = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    año = Column(Integer, nullable=False)
    hora = Column(Time, nullable=False)

    # ÍNDICES COMPUESTOS
    __table_args__ = (
        # Para análisis de conversión por fuente
        Index('ix_calendly_clicks_source_fecha', 'traffic_source', 'fecha'),

        # Para análisis temporal
        Index('ix_calendly_clicks_año_mes', 'año', 'mes'),

        # Para seguir el embudo del usuario
        Index('ix_calendly_clicks_session_timestamp', 'session_id', 'timestamp'),

        # Para análisis de ubicación de botones
        Index('ix_calendly_clicks_location_source', 'button_location', 'traffic_source'),
    )