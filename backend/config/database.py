from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import settings
from sqlalchemy.exc import SQLAlchemyError
# Engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=10,
    max_overflow=20
)

# SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependencia para obtener sesión de BD en FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Crea todas las tablas en la base de datos
    """
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except SQLAlchemyError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Error al inicializar la base de datos")
        logger.exception(e)
        return False
