from sqlalchemy import Column, String, DateTime, func
from backend.config.database import Base


class SessionTracking(Base):
    __tablename__ = "sessions_tracking"

    session_id = Column(String(255), primary_key=True)
    traffic_source = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())