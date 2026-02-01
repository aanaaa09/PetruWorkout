import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from backend.config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def crear_base_datos():
    """Crea la base de datos PetruWorkout si no existe"""
    try:
        # Conectar a la base de datos postgres por defecto
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Verificar si la base de datos existe
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (settings.DB_NAME,)
        )
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f'CREATE DATABASE "{settings.DB_NAME}"')
            logger.info(f"Base de datos '{settings.DB_NAME}' creada correctamente")
        else:
            logger.info(f"Base de datos '{settings.DB_NAME}' ya existe")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Error al crear la base de datos: {e}")
        logger.info("Asegúrate de que PostgreSQL esté corriendo y las credenciales sean correctas")
        return False


if __name__ == "__main__":
    crear_base_datos()