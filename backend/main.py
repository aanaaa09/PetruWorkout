import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routers import auth, consultas, tracking
from .config.database import Base, engine, close_db_connections
from .init_db import crear_base_datos

# --------------------------
# Logging
# --------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# --------------------------
# ✅ Lifespan: startup/shutdown events
# --------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja inicio y cierre de la aplicación"""
    # STARTUP
    logger.info("🚀 Iniciando aplicación...")
    crear_base_datos()
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Base de datos inicializada")

    yield  # Aplicación corriendo

    # SHUTDOWN
    logger.info("🛑 Cerrando aplicación...")
    close_db_connections()
    logger.info("✅ Conexiones cerradas")


# --------------------------
# Crear app FastAPI
# --------------------------
app = FastAPI(
    title="PetruWorkout API",
    description="API de PetruWorkout",
    version="2.0",
    lifespan=lifespan  # ✅ Usar lifespan context manager
)

# --------------------------
# CORS
# --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5000",
        "https://petrucalistenia.com",
        "https://www.petrucalistenia.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Routers API
# --------------------------
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(consultas.router)
app.include_router(tracking.router, prefix="/api/tracking", tags=["tracking"])


# --------------------------
# Health y info API
# --------------------------
@app.get("/api")
async def api_info():
    return {"message": "PetruWorkout API", "version": "2.0"}


@app.get("/health")
async def health():
    """Health check optimizado"""
    try:
        # ✅ No verificar BD en cada health check para evitar conexiones innecesarias
        return {
            "status": "healthy",
            "service": "petruworkout",
            "version": "2.0"
        }
    except Exception as e:
        logger.error(f"Health check falló: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/api/sync-calendly")
async def sync_calendly_endpoint():
    """
    Endpoint para sincronizar reservas de Calendly
    ⚠️ Este endpoint debería protegerse con autenticación en producción
    """
    from .sync_calendly import sync_calendly_bookings

    try:
        sync_calendly_bookings()
        return {"success": True, "message": "Sincronización completada"}
    except Exception as e:
        logger.error(f"Error en sync: {e}")
        return {"success": False, "error": str(e)}


# --------------------------
# Arrancar servidor
# --------------------------
if __name__ == "__main__":
    import uvicorn

    # ✅ Configuración optimizada de uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=5000,
        reload=False,  # ✅ Desactivar en producción
        workers=1,  # ✅ 1 worker para tráfico bajo
        limit_concurrency=50,  # ✅ Limitar requests concurrentes
        timeout_keep_alive=30  # ✅ Cerrar conexiones idle
    )