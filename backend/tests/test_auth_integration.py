import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.config.database import Base, get_db
from backend.models.usuario import Usuario
from backend.models.sesion import Sesion
import time

# Base de datos de test en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dependencia de DB para tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Setup y teardown de la base de datos para cada test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestAuthIntegracion:
    """Tests de integración para endpoints de autenticación"""

    def test_registro_completo_flujo(self, setup_database):
        """Test: flujo completo de registro"""
        # Datos de registro
        datos_registro = {
            "nombre": "Usuario Test",
            "email": "test@example.com",
            "password": "password123"
        }

        # Hacer registro
        response = client.post("/api/auth/registro", json=datos_registro)

        # Verificaciones
        assert response.status_code == 200, f"Error: {response.json()}"
        data = response.json()

        assert data['success'] is True
        assert 'token' in data
        assert 'usuario' in data
        assert data['usuario']['email'] == "test@example.com"
        assert data['usuario']['nombre'] == "Usuario Test"
        assert data['usuario']['puntos'] == 0
        assert len(data['token']) > 20  # El token debe ser largo

    def test_registro_duplicado_debe_fallar(self, setup_database):
        """Test: registro con email duplicado debe fallar"""
        datos = {
            "nombre": "Usuario Test",
            "email": "duplicate@example.com",
            "password": "password123"
        }

        # Primer registro (debe funcionar)
        response1 = client.post("/api/auth/registro", json=datos)
        assert response1.status_code == 200

        # Segundo registro (debe fallar)
        response2 = client.post("/api/auth/registro", json=datos)
        assert response2.status_code == 400
        assert 'ya está registrado' in response2.json()['detail'].lower()

    def test_registro_validaciones_campos(self, setup_database):
        """Test: validaciones de campos en registro"""
        # Nombre muy corto
        response1 = client.post("/api/auth/registro", json={
            "nombre": "A",
            "email": "test@test.com",
            "password": "123456"
        })
        assert response1.status_code == 400

        # Email inválido
        response2 = client.post("/api/auth/registro", json={
            "nombre": "Test User",
            "email": "emailinvalido",
            "password": "123456"
        })
        assert response2.status_code == 400

        # Password muy corta
        response3 = client.post("/api/auth/registro", json={
            "nombre": "Test User",
            "email": "test@test.com",
            "password": "123"
        })
        assert response3.status_code == 400

    def test_login_despues_de_registro(self, setup_database):
        """Test: login después de registrarse debe funcionar"""
        # Registro
        datos_registro = {
            "nombre": "Login Test",
            "email": "login@test.com",
            "password": "mypassword"
        }
        response_registro = client.post("/api/auth/registro", json=datos_registro)
        assert response_registro.status_code == 200

        # Login con las mismas credenciales
        datos_login = {
            "email": "login@test.com",
            "password": "mypassword"
        }
        response_login = client.post("/api/auth/login", json=datos_login)

        assert response_login.status_code == 200
        data = response_login.json()
        assert data['success'] is True
        assert 'token' in data
        assert data['usuario']['email'] == "login@test.com"

    def test_login_credenciales_incorrectas(self, setup_database):
        """Test: login con credenciales incorrectas debe fallar"""
        # Primero registrar usuario
        client.post("/api/auth/registro", json={
            "nombre": "Test User",
            "email": "user@test.com",
            "password": "correctpass"
        })

        # Intentar login con password incorrecta
        response = client.post("/api/auth/login", json={
            "email": "user@test.com",
            "password": "wrongpass"
        })

        assert response.status_code == 401
        assert 'incorrectos' in response.json()['detail'].lower()

    def test_verificar_sesion_con_token_valido(self, setup_database):
        """Test: verificar sesión con token válido"""
        # Registro
        response_registro = client.post("/api/auth/registro", json={
            "nombre": "Verify Test",
            "email": "verify@test.com",
            "password": "password123"
        })
        token = response_registro.json()['token']

        # Verificar sesión
        response_verificar = client.post("/api/auth/verificar", json={"token": token})

        assert response_verificar.status_code == 200
        data = response_verificar.json()
        assert data['valida'] is True
        assert data['usuario']['email'] == "verify@test.com"

    def test_verificar_sesion_con_token_invalido(self, setup_database):
        """Test: verificar sesión con token inválido debe fallar"""
        response = client.post("/api/auth/verificar", json={"token": "token_fake_123"})

        assert response.status_code == 401

    def test_logout_con_token_valido(self, setup_database):
        """Test: logout debe eliminar la sesión"""
        # Registro
        response_registro = client.post("/api/auth/registro", json={
            "nombre": "Logout Test",
            "email": "logout@test.com",
            "password": "password123"
        })
        token = response_registro.json()['token']

        # Logout
        response_logout = client.post("/api/auth/logout", json={"token": token})
        assert response_logout.status_code == 200

        # Verificar que el token ya no es válido
        response_verificar = client.post("/api/auth/verificar", json={"token": token})
        assert response_verificar.status_code == 401

    def test_actualizar_puntos(self, setup_database):
        """Test: actualizar puntos de usuario"""
        # Registro
        response_registro = client.post("/api/auth/registro", json={
            "nombre": "Points Test",
            "email": "points@test.com",
            "password": "password123"
        })
        token = response_registro.json()['token']

        # Actualizar puntos
        response_puntos = client.post("/api/auth/actualizar-puntos", json={
            "token": token,
            "puntos": 50
        })

        assert response_puntos.status_code == 200
        assert response_puntos.json()['puntos'] == 50

        # Verificar que los puntos se actualizaron
        response_verificar = client.post("/api/auth/verificar", json={"token": token})
        assert response_verificar.json()['usuario']['puntos'] == 50

    def test_ranking_usuarios(self, setup_database):
        """Test: obtener ranking de usuarios"""
        # Registrar varios usuarios con diferentes puntos
        usuarios = [
            {"nombre": "User1", "email": "user1@test.com", "password": "pass1", "puntos": 100},
            {"nombre": "User2", "email": "user2@test.com", "password": "pass2", "puntos": 200},
            {"nombre": "User3", "email": "user3@test.com", "password": "pass3", "puntos": 50},
        ]

        for user in usuarios:
            response_registro = client.post("/api/auth/registro", json={
                "nombre": user["nombre"],
                "email": user["email"],
                "password": user["password"]
            })
            token = response_registro.json()['token']

            # Actualizar puntos
            client.post("/api/auth/actualizar-puntos", json={
                "token": token,
                "puntos": user["puntos"]
            })

        # Obtener ranking
        response_ranking = client.get("/api/auth/ranking")

        assert response_ranking.status_code == 200
        data = response_ranking.json()
        assert data['success'] is True
        assert len(data['ranking']) == 3

        # Verificar que están ordenados por puntos (mayor a menor)
        assert data['ranking'][0]['puntos'] == 200
        assert data['ranking'][1]['puntos'] == 100
        assert data['ranking'][2]['puntos'] == 50

    def test_registro_concurrente_mismo_email(self, setup_database):
        """Test: registros concurrentes con el mismo email (diagnóstico del bug)"""
        import concurrent.futures

        datos = {
            "nombre": "Concurrent Test",
            "email": "concurrent@test.com",
            "password": "password123"
        }

        def hacer_registro():
            try:
                response = client.post("/api/auth/registro", json=datos)
                return response.status_code, response.json()
            except Exception as e:
                return None, str(e)

        # Hacer 3 registros simultáneos
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(hacer_registro) for _ in range(3)]
            resultados = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Contar exitosos y fallidos
        exitosos = sum(1 for status, _ in resultados if status == 200)
        fallidos = sum(1 for status, _ in resultados if status == 400)

        # DEBE haber exactamente 1 exitoso y 2 fallidos
        print(f"Exitosos: {exitosos}, Fallidos: {fallidos}")
        print(f"Resultados: {resultados}")

        assert exitosos == 1, f"Debe haber 1 registro exitoso, pero hubo {exitosos}"
        assert fallidos == 2, f"Debe haber 2 registros fallidos, pero hubo {fallidos}"

    def test_timing_registro_respuesta(self, setup_database):
        """Test: medir tiempo de respuesta del registro (diagnóstico de doble request)"""
        datos = {
            "nombre": "Timing Test",
            "email": "timing@test.com",
            "password": "password123"
        }

        start = time.time()
        response = client.post("/api/auth/registro", json=datos)
        end = time.time()

        tiempo_respuesta = (end - start) * 1000  # en ms

        print(f"Tiempo de respuesta: {tiempo_respuesta:.2f}ms")

        assert response.status_code == 200
        assert tiempo_respuesta < 5000, f"Registro muy lento: {tiempo_respuesta:.2f}ms"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])