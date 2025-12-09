from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from .settings import settings
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

# ✅ Pool pequeño optimizado para Railway con poco tráfico
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=2,              # Solo 2 conexiones persistentes (antes 5)
    max_overflow=1,           # Máximo 1 conexión extra si hay pico (antes 10)
    pool_recycle=300,         # Reciclar conexiones cada 5 min (evita conexiones muertas)
    pool_pre_ping=True,       # Verifica conexión antes de usarla
    pool_timeout=10,          # Timeout reducido
    echo=False,
)

# ✅ SessionLocal optimizado
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Evita queries adicionales post-commit
)

Base = declarative_base()


def get_db():
    """Dependencia para obtener sesión de BD en FastAPI"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en sesión BD: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Sesión BD cerrada")


def init_db():
    """Crea todas las tablas en la base de datos"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas/verificadas")
        return True
    except SQLAlchemyError as e:
        logger.error("Error al inicializar la base de datos")
        logger.exception(e)
        return False


def close_db_connections():
    """Cierra todas las conexiones del pool (útil para shutdown)"""
    try:
        engine.dispose()
        logger.info("✅ Pool de conexiones cerrado")
    except Exception as e:
        logger.error(f"Error cerrando pool: {e}")