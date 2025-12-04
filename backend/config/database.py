from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from .settings import settings
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

# ✅ OPCIÓN 1: Pool minimalista (para tráfico bajo/medio)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=2,              # ✅ Reducido de 20 a 2
    max_overflow=3,           # ✅ Reducido de 40 a 3
    pool_recycle=1800,        # ✅ Reducido de 3600 a 1800 (30 min)
    pool_timeout=10,          # ✅ Timeout de 10 segundos
    echo=False,               # ✅ Desactivar logs SQL en producción
)



# SessionLocal con configuración optimizada
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # ✅ Evita queries adicionales post-commit
)

Base = declarative_base()


# ✅ Event listener para cerrar conexiones automáticamente
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Configura timeout en cada conexión nueva"""
    connection_record.info['pid'] = dbapi_conn.get_backend_pid()
    logger.debug(f"Nueva conexión BD: PID {connection_record.info['pid']}")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log cuando se obtiene conexión del pool"""
    logger.debug(f"Checkout conexión: PID {connection_record.info.get('pid')}")


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
        db.close()  # ✅ Cierra explícitamente
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