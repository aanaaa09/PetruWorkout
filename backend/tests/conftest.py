# ==========================================
# backend/tests/conftest.py
# ==========================================
"""Configuración global de pytest"""
import os
import sys
from pathlib import Path

# ✅ PASO 1: Configurar variables de entorno ANTES de cualquier import
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("EMAIL_API", "test_key")
os.environ.setdefault("CALENDLY_API_KEY", "test_key")
os.environ.setdefault("CALENDLY_USER_URI", "test_uri")
os.environ.setdefault("CALENDLY_EVENT_URL", "test_url")
os.environ.setdefault("SPOTIFY_CLIENT_ID", "test_id")
os.environ.setdefault("SPOTIFY_CLIENT_SECRET", "test_secret")
os.environ.setdefault("SPOTIFY_REFRESH_TOKEN", "test_token")
os.environ.setdefault("OPENAI_API_KEY", "test_key")

# ✅ PASO 2: Añadir backend al path si es necesario
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# ✅ PASO 3: AHORA SÍ importar
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.config.database import Base, get_db

# BD temporal (solo para tests en GitHub)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """BD limpia para cada test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Cliente de test de FastAPI"""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()