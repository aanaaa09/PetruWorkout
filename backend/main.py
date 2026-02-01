import os
import gc
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from .routers import auth, consultas, tracking, leads, calculator
from .config.database import Base, engine, close_db_connections
from .init_db import crear_base_datos

# --------------------------
# Logging
# --------------------------
logging.basicConfig(
    level=logging.ERROR,  # Solo errores críticos
    format='%(levelname)s - %(message)s'  # Formato minimalista
)
logger = logging.getLogger(__name__)

# DESACTIVAR logs de librerías ruidosas
logging.getLogger("uvicorn.access").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)


# --------------------------
# Task para forzar GC periódicamente
# --------------------------
async def periodic_gc():
    """Fuerza garbage collection cada 5 minutos"""
    while True:
        await asyncio.sleep(300)  # 5 minutos
        gc.collect()  # Liberar memoria no usada
        logger.debug("GC ejecutado")


# --------------------------
# Lifespan: startup/shutdown events
# --------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja inicio y cierre de la aplicación"""
    # STARTUP
    logger.info("Iniciando...")
    crear_base_datos()
    Base.metadata.create_all(bind=engine)

    # Iniciar tarea de limpieza de memoria
    gc_task = asyncio.create_task(periodic_gc())

    yield  # Aplicación corriendo

    # SHUTDOWN
    gc_task.cancel()
    close_db_connections()
    gc.collect()  # Limpieza final
    logger.info("Cerrado")


# --------------------------
# Crear app FastAPI
# --------------------------
app = FastAPI(
    title="PetruWorkout API",
    version="2.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)


# --------------------------
# Middleware para liberar memoria después de cada request
# --------------------------
@app.middleware("http")
async def cleanup_middleware(request: Request, call_next):
    """Libera memoria después de cada request"""
    response = await call_next(request)

    # Forzar GC cada 50 requests
    if not hasattr(app.state, 'request_count'):
        app.state.request_count = 0

    app.state.request_count += 1
    if app.state.request_count % 50 == 0:
        gc.collect()

    return response


# --------------------------
# CORS OPTIMIZADO
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
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)

# --------------------------
# Routers API
# --------------------------
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(consultas.router)
app.include_router(tracking.router, prefix="/api/tracking", tags=["tracking"])
app.include_router(leads.router)
app.include_router(calculator.router, tags=["calculator"])

# --------------------------
# Health y info API (ULTRA LIGEROS)
# --------------------------
@app.get("/api")
async def api_info():
    return {"v": "2.0"}


@app.get("/health")
async def health():
    """Health check ultra ligero"""
    return {"ok": 1}


@app.get("/api/sync-calendly")
async def sync_calendly_endpoint():
    """Endpoint para sincronizar reservas de Calendly"""
    from .sync_calendly import sync_calendly_bookings

    try:
        sync_calendly_bookings()
        return {"success": True}
    except Exception as e:
        logger.error(f"Error sync: {e}")
        return {"success": False, "error": str(e)}


# --------------------------
# Arrancar servidor
# --------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        reload=False,
        workers=1,
        limit_concurrency=10,
        timeout_keep_alive=5,
        timeout_graceful_shutdown=2,
        backlog=10,
        log_level="error",
        access_log=False,
        server_header=False,
        date_header=False,
    )