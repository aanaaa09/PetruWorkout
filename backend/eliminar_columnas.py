"""
Script para eliminar columnas de las tablas
- via_whatsapp de calendly_clicks y calendly_bookings
- leida y respondida de consultas
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URL de conexión a Railway
DATABASE_URL = "postgresql://postgres:zmBLqeCqmmSgCCJkXQmKdZviqkOVWuVP@switchyard.proxy.rlwy.net:47023/railway"


def eliminar_columnas():
    """Elimina las columnas especificadas de las tablas"""
    try:
        # Conectar a Railway
        logger.info("🔌 Conectando a Railway PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        logger.info("✅ Conexión exitosa")
        logger.info("=" * 60)

        # Lista de columnas a eliminar
        columnas_a_eliminar = [
            ("calendly_clicks", "via_whatsapp"),
            ("calendly_bookings", "via_whatsapp"),
            ("consultas", "leida"),
            ("consultas", "respondida")
        ]

        # Eliminar cada columna
        for tabla, columna in columnas_a_eliminar:
            try:
                logger.info(f"🗑️  Eliminando {tabla}.{columna}...")

                # Verificar si la columna existe primero
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = %s
                """, (tabla, columna))

                existe = cursor.fetchone()

                if existe:
                    # Eliminar columna
                    cursor.execute(f"ALTER TABLE {tabla} DROP COLUMN IF EXISTS {columna}")
                    logger.info(f"   ✅ {tabla}.{columna} eliminada correctamente")
                else:
                    logger.info(f"   ℹ️  {tabla}.{columna} no existe (ya fue eliminada)")

            except Exception as e:
                logger.error(f"   ❌ Error eliminando {tabla}.{columna}: {e}")

        logger.info("=" * 60)
        logger.info("📊 VERIFICANDO ESTRUCTURAS...")
        logger.info("=" * 60)

        # Verificar estructura de cada tabla
        tablas_verificar = ["calendly_clicks", "calendly_bookings", "consultas"]

        for tabla in tablas_verificar:
            logger.info(f"\n📋 Estructura de {tabla}:")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (tabla,))

            columnas = cursor.fetchall()
            for col in columnas:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                logger.info(f"   • {col[0]:30s} {col[1]:20s} {nullable}")

        cursor.close()
        conn.close()

        logger.info("\n" + "=" * 60)
        logger.info("✅ PROCESO COMPLETADO EXITOSAMENTE")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 ELIMINANDO COLUMNAS INNECESARIAS")
    logger.info("=" * 60)

    eliminar_columnas()