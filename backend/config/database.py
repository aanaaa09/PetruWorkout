import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from .settings import settings
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


def get_database_url():
    """
    Construye la URL de la base de datos.
    Prioridad: Variables de Railway (PG*) > Variables custom (DB_*) > settings
    """
    # Railway CLI inyecta estas variables automáticamente
    pg_host = os.getenv('PGHOST')
    pg_port = os.getenv('PGPORT')
    pg_database = os.getenv('PGDATABASE')
    pg_user = os.getenv('PGUSER')
    pg_password = os.getenv('PGPASSWORD')


    if pg_host and pg_password:
        url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
        logger.info(f"Usando variables de Railway CLI: {pg_host}:{pg_port}")
        return url


    logger.info("Usando configuración de settings")
    return settings.DATABASE_URL


DATABASE_URL = get_database_url()

# Pool pequeño optimizado para Railway con poco tráfico
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=2,
    max_overflow=1,
    pool_recycle=300,
    pool_pre_ping=True,
    pool_timeout=10,
    echo=False,
)


# SessionLocal optimizado
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
        logger.info("Tablas creadas/verificadas")
        return True
    except SQLAlchemyError as e:
        logger.error("Error al inicializar la base de datos")
        logger.exception(e)
        return False


def close_db_connections():
    """Cierra todas las conexiones del pool (útil para shutdown)"""
    try:
        engine.dispose()
        logger.info("Pool de conexiones cerrado")
    except Exception as e:
        logger.error(f"Error cerrando pool: {e}")