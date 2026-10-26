from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func, false
from backend.config.database import Base


class DiagnosticoLead(Base):
    """
    Contactos que rellenan el formulario de diagnóstico de la home.
    Se guardan SIEMPRE antes de avisar por Telegram: si Telegram falla,
    el contacto no se pierde y se puede consultar aquí.
    """
    __tablename__ = "diagnostico_leads"

    id = Column(Integer, primary_key=True, index=True)

    # Datos de contacto
    nombre = Column(String(200), nullable=False)
    telefono = Column(String(40), nullable=False)

    # Respuestas del formulario (texto tal cual lo ve el visitante)
    edad = Column(String(100), nullable=False)
    nivel = Column(String(300), nullable=False)
    objetivo = Column(String(300), nullable=False)
    freno = Column(String(300), nullable=False)
    compromiso = Column(String(300), nullable=False)

    # Estado del aviso por Telegram
    telegram_enviado = Column(Boolean, nullable=False, default=False, server_default=false())
    telegram_error = Column(Text, nullable=True)

    fecha = Column(DateTime(timezone=True), server_default=func.now())
