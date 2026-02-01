"""
Backup incremental desde Railway a GitHub
Primera ejecución: backup completo histórico
Siguientes: solo registros del último mes

"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import psycopg2
import json
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RailwayBackup:
    """Descarga backups incrementales desde Railway"""

    TABLAS_A_RESPALDAR = [
        'usuarios',
        'sesiones',
        'consultas',
        'page_visits',
        'calendly_clicks',
        'calendly_bookings'
    ]

    def __init__(self):
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
        self.log_file = self.backup_dir / 'backup-log.json'

        # Obtener URL de Railway desde variable de entorno
        database_url = os.getenv('DATABASE_URL')

        if not database_url:
            logger.error("❌ DATABASE_URL no configurada")
            sys.exit(1)

        logger.info(f"🔌 Conectando a Railway...")

        # Conectar con reintentos (despertar BD si está dormida)
        self.conn = self._conectar_con_reintentos(database_url)

    def _conectar_con_reintentos(self, database_url, max_intentos=5, tiempo_espera=10):
        """
        Conecta a Railway con reintentos para despertar la BD si está dormida.
        Railway puede tardar hasta 30-60 segundos en despertar una BD inactiva.
        """
        for intento in range(1, max_intentos + 1):
            try:
                logger.info(f"🔄 Intento {intento}/{max_intentos}...")
                conn = psycopg2.connect(database_url, connect_timeout=30)

                # Verificar que la conexión funciona
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()

                logger.info("✅ Conectado a Railway")
                return conn

            except psycopg2.OperationalError as e:
                error_msg = str(e)

                if intento < max_intentos:
                    if "server closed the connection" in error_msg or "Connection refused" in error_msg:
                        logger.warning(
                            f"⏳ BD dormida o iniciando... Esperando {tiempo_espera}s antes del siguiente intento")
                    else:
                        logger.warning(f"⚠️ Error de conexión: {error_msg}")

                    time.sleep(tiempo_espera)
                else:
                    logger.error(f"❌ Error conectando tras {max_intentos} intentos: {e}")
                    logger.error("💡 Posibles causas:")
                    logger.error("   - Verifica que DATABASE_URL sea correcta")
                    logger.error("   - Verifica que el servicio esté activo en Railway")
                    logger.error("   - Revisa los límites de tu plan en Railway")
                    sys.exit(1)

            except Exception as e:
                logger.error(f"❌ Error inesperado conectando a Railway: {e}")
                sys.exit(1)

    def cargar_log(self):
        """Carga registro de últimos backups"""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return {}

    def guardar_log(self, log):
        """Guarda registro de backup"""
        with open(self.log_file, 'w') as f:
            json.dump(log, f, indent=2, default=str)

    def es_primer_backup(self):
        """Verifica si es el primer backup"""
        log = self.cargar_log()
        return len(log) == 0

    def obtener_fecha_ultimo_backup(self, tabla):
        """Obtiene la fecha del último backup de una tabla"""
        log = self.cargar_log()
        if tabla in log:
            return datetime.fromisoformat(log[tabla])
        # Si no hay backup previo, retornar None (backup completo)
        return None

    def exportar_tabla_completa(self, tabla, cursor, sql_file):
        """Exporta TODOS los registros de una tabla (primer backup)"""
        query = f"SELECT * FROM {tabla}"
        cursor.execute(query)
        registros = cursor.fetchall()

        if not registros:
            logger.info(f"ℹ️  {tabla}: Vacía")
            return 0

        # Obtener nombres de columnas
        columnas = [desc[0] for desc in cursor.description]

        # Escribir INSERT statements
        sql_file.write(f"\n-- ========================================\n")
        sql_file.write(f"-- Tabla: {tabla}\n")
        sql_file.write(f"-- BACKUP COMPLETO HISTÓRICO\n")
        sql_file.write(f"-- Total registros: {len(registros)}\n")
        sql_file.write(f"-- ========================================\n\n")

        for registro in registros:
            valores = []
            for valor in registro:
                if valor is None:
                    valores.append('NULL')
                elif isinstance(valor, str):
                    valor_escapado = valor.replace("'", "''")
                    valores.append(f"'{valor_escapado}'")
                elif isinstance(valor, (datetime)):
                    valores.append(f"'{valor.isoformat()}'")
                elif isinstance(valor, bool):
                    valores.append('TRUE' if valor else 'FALSE')
                else:
                    valores.append(str(valor))

            columnas_str = ', '.join(columnas)
            valores_str = ', '.join(valores)

            sql_file.write(
                f"INSERT INTO {tabla} ({columnas_str}) "
                f"VALUES ({valores_str}) "
                f"ON CONFLICT DO NOTHING;\n"
            )

        sql_file.write("\n")
        logger.info(f"✅ {tabla}: {len(registros)} registros (TODOS)")
        return len(registros)

    def exportar_tabla_incremental(self, tabla, cursor, sql_file):
        """Exporta solo registros nuevos desde el último backup"""
        fecha_ultimo = self.obtener_fecha_ultimo_backup(tabla)

        if fecha_ultimo is None:
            # No debería pasar, pero por seguridad
            return self.exportar_tabla_completa(tabla, cursor, sql_file)

        # Detectar columna de fecha en cada tabla
        columna_fecha_map = {
            'usuarios': 'fecha_registro',
            'sesiones': 'fecha_creacion',
            'consultas': 'fecha_envio',
            'page_visits': 'timestamp',
            'calendly_clicks': 'timestamp',
            'calendly_bookings': 'timestamp'
        }

        columna_fecha = columna_fecha_map.get(tabla)

        if not columna_fecha:
            logger.warning(f"⚠️ No se encontró columna de fecha para {tabla}")
            return 0

        # Obtener registros nuevos desde el último backup
        query = f"""
            SELECT * FROM {tabla}
            WHERE {columna_fecha} > %s
            ORDER BY {columna_fecha} ASC
        """

        cursor.execute(query, (fecha_ultimo,))
        registros = cursor.fetchall()

        if not registros:
            logger.info(f"ℹ️  {tabla}: Sin registros nuevos")
            return 0

        # Obtener nombres de columnas
        columnas = [desc[0] for desc in cursor.description]

        # Escribir INSERT statements
        sql_file.write(f"\n-- ========================================\n")
        sql_file.write(f"-- Tabla: {tabla}\n")
        sql_file.write(f"-- Registros nuevos: {len(registros)}\n")
        sql_file.write(f"-- Desde: {fecha_ultimo.strftime('%Y-%m-%d %H:%M:%S')}\n")
        sql_file.write(f"-- ========================================\n\n")

        for registro in registros:
            valores = []
            for valor in registro:
                if valor is None:
                    valores.append('NULL')
                elif isinstance(valor, str):
                    valor_escapado = valor.replace("'", "''")
                    valores.append(f"'{valor_escapado}'")
                elif isinstance(valor, (datetime)):
                    valores.append(f"'{valor.isoformat()}'")
                elif isinstance(valor, bool):
                    valores.append('TRUE' if valor else 'FALSE')
                else:
                    valores.append(str(valor))

            columnas_str = ', '.join(columnas)
            valores_str = ', '.join(valores)

            sql_file.write(
                f"INSERT INTO {tabla} ({columnas_str}) "
                f"VALUES ({valores_str}) "
                f"ON CONFLICT DO NOTHING;\n"
            )

        sql_file.write("\n")
        logger.info(f"✅ {tabla}: {len(registros)} registros nuevos")
        return len(registros)

    def ejecutar_backup(self):
        """Ejecuta el backup (completo o incremental según corresponda)"""
        fecha_actual = datetime.now()

        # Detectar si es primer backup
        primer_backup = self.es_primer_backup()

        if primer_backup:
            # Primer backup: nombre especial con "completo"
            archivo_backup = self.backup_dir / f"backup-completo-inicial.sql"
            tipo_backup = "COMPLETO HISTÓRICO"
            logger.info("🎯 PRIMER BACKUP: Se descargarán TODOS los datos históricos")
        else:
            # Backups siguientes: nombre con mes/año
            mes_año = fecha_actual.strftime('%Y-%m-%B')
            archivo_backup = self.backup_dir / f"backup-{mes_año}.sql"
            tipo_backup = "INCREMENTAL"
            logger.info("📅 Backup incremental: Solo datos nuevos desde el último backup")

        logger.info(f"📁 Archivo: {archivo_backup.name}")

        total_registros = 0

        try:
            with open(archivo_backup, 'w', encoding='utf-8') as sql_file:
                # Header
                sql_file.write(f"-- ========================================\n")
                sql_file.write(f"-- BACKUP {tipo_backup} - RAILWAY\n")
                sql_file.write(f"-- Fecha: {fecha_actual.strftime('%Y-%m-%d %H:%M:%S')}\n")
                sql_file.write(f"-- Base de datos: {os.getenv('DB_NAME', 'railway')}\n")
                sql_file.write(f"-- ========================================\n\n")

                sql_file.write("BEGIN;\n\n")

                cursor = self.conn.cursor()

                # Exportar cada tabla
                for tabla in self.TABLAS_A_RESPALDAR:
                    try:
                        if primer_backup:
                            # Primer backup: TODO
                            registros = self.exportar_tabla_completa(tabla, cursor, sql_file)
                        else:
                            # Backups siguientes: solo nuevos
                            registros = self.exportar_tabla_incremental(tabla, cursor, sql_file)

                        total_registros += registros
                    except Exception as e:
                        logger.error(f"❌ Error en tabla {tabla}: {e}")

                sql_file.write("COMMIT;\n")

                cursor.close()

            # Actualizar log con la fecha actual
            log = self.cargar_log()
            for tabla in self.TABLAS_A_RESPALDAR:
                log[tabla] = fecha_actual.isoformat()
            self.guardar_log(log)

            # Estadísticas
            tamaño_mb = archivo_backup.stat().st_size / (1024 * 1024)

            logger.info("=" * 50)
            logger.info(f"✅ BACKUP COMPLETADO")
            logger.info(f"📊 Tipo: {tipo_backup}")
            logger.info(f"📝 Total registros: {total_registros}")
            logger.info(f"📁 Archivo: {archivo_backup.name}")
            logger.info(f"💾 Tamaño: {tamaño_mb:.2f} MB")
            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"❌ Error en backup: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            self.conn.close()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 BACKUP RAILWAY → GITHUB")
    logger.info("=" * 60)

    backup = RailwayBackup()
    backup.ejecutar_backup()

    logger.info("=" * 60)
    logger.info("✅ PROCESO COMPLETADO")
    logger.info("=" * 60)