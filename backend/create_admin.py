"""
Script para crear usuarios administradores en la base de datos.
Ejecutar UNA SOLA VEZ para crear los admins.

Uso:
    python -m backend.create_admin
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import bcrypt
from datetime import datetime
import sys


def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_admin_users():
    """
    Crea los usuarios administradores en la base de datos de Railway
    """
    # URL de conexión directa a Railway
    DATABASE_URL = "postgresql://postgres:zmBLqeCqmmSgCCJkXQmKdZviqkOVWuVP@switchyard.proxy.rlwy.net:47023/railway"

    # Lista de admins a crear
    admins = [
        {
            'nombre': 'Petru Admin',
            'email': 'petruworkout@gmail.com',
            'password': input('Introduce contraseña para petruworkout@gmail.com: ')
        },
        {
            'nombre': 'Admin Petru',
            'email': 'admn.petruworkout@gmail.com',
            'password': input('Introduce contraseña para admn.petruworkout@gmail.com: ')
        }
    ]

    try:
        # Conectar a la base de datos
        print("\n🔌 Conectando a Railway...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print("✅ Conectado correctamente\n")

        for admin in admins:
            email = admin['email']

            # Verificar si ya existe
            cursor.execute(
                "SELECT id, email, tipo_usuario FROM usuarios WHERE email = %s",
                (email,)
            )
            existing = cursor.fetchone()

            if existing:
                print(f"⚠️  El usuario {email} ya existe")
                print(f"   ID: {existing[0]}, Tipo: {existing[2]}")

                # Preguntar si quiere actualizar
                respuesta = input(f"   ¿Actualizar contraseña? (s/n): ").lower()
                if respuesta == 's':
                    password_hash = hash_password(admin['password'])
                    cursor.execute(
                        """
                        UPDATE usuarios 
                        SET password_hash = %s,
                            tipo_usuario = 'ADMIN',
                            suscrito_newsletter = true
                        WHERE email = %s
                        """,
                        (password_hash, email)
                    )
                    print(f"   ✅ Contraseña actualizada para {email}\n")
                else:
                    print(f"   ⏭️  Saltando {email}\n")
                continue

            # Crear nuevo admin
            print(f"👤 Creando admin: {email}")
            password_hash = hash_password(admin['password'])

            cursor.execute(
                """
                INSERT INTO usuarios (
                    nombre, 
                    email, 
                    password_hash, 
                    tipo_usuario, 
                    suscrito_newsletter,
                    fecha_registro
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    admin['nombre'],
                    email,
                    password_hash,
                    'ADMIN',  # tipo_usuario como string (enum)
                    True,
                    datetime.now()
                )
            )

            user_id = cursor.fetchone()[0]
            print(f"   ✅ Admin creado correctamente (ID: {user_id})\n")

        # Mostrar resumen
        cursor.execute(
            "SELECT id, nombre, email, tipo_usuario, fecha_registro FROM usuarios WHERE tipo_usuario = 'ADMIN'"
        )
        admins_db = cursor.fetchall()

        print("=" * 60)
        print("📋 RESUMEN DE ADMINISTRADORES EN LA BASE DE DATOS")
        print("=" * 60)
        for admin in admins_db:
            print(f"ID: {admin[0]}")
            print(f"Nombre: {admin[1]}")
            print(f"Email: {admin[2]}")
            print(f"Tipo: {admin[3]}")
            print(f"Fecha registro: {admin[4]}")
            print("-" * 60)

        cursor.close()
        conn.close()
        print("\n✅ Proceso completado exitosamente")

    except psycopg2.Error as e:
        print(f"\n❌ Error de base de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 CREACIÓN DE USUARIOS ADMINISTRADORES")
    print("=" * 60)
    print("\n⚠️  IMPORTANTE:")
    print("   - Este script crea usuarios con tipo_usuario = 'ADMIN'")
    print("   - Solo ejecutar UNA VEZ o para actualizar contraseñas")
    print("   - Las contraseñas se hashean con bcrypt")
    print("\n" + "=" * 60 + "\n")

    respuesta = input("¿Continuar? (s/n): ").lower()
    if respuesta != 's':
        print("❌ Cancelado por el usuario")
        sys.exit(0)

    print()
    create_admin_users()