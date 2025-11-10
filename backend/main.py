import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config.database import init_db
from .routers import auth, game, game_rondas

# --------------------------
# Logging
# --------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------
# Crear app FastAPI
# --------------------------
app = FastAPI(
    title="SongByte API",
    description="API del juego SongByte",
    version="2.0"
)

# --------------------------
# CORS
# --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Routers API
# --------------------------
app.include_router(auth.router, prefix="/api/auth")
app.include_router(game.router, prefix="/api/game")
app.include_router(game_rondas.router, prefix="/api/rondas")

# --------------------------
# Montar frontend SPA
# --------------------------
frontend_dist = os.path.join(os.path.dirname(__file__), "../frontend/dist")
assets_dir = os.path.join(frontend_dist, "assets")

if os.path.isdir(frontend_dist):
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        logger.info(f"✅ Frontend assets montados desde {assets_dir}")
    else:
        logger.warning(f"Frontend assets no encontrados en {assets_dir}")
else:
    logger.warning(f"Frontend no encontrado en {frontend_dist}")

@app.get("/")
async def serve_root():
    index_file = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend no encontrado"}

# --------------------------
# SPA fallback (para rutas del cliente)
# --------------------------
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    # Evitar capturar rutas de la API
    if full_path.startswith("api/"):
        return {"message": "Ruta API no encontrada"}
    index_file = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend no encontrado"}

# --------------------------
# Health y info API
# --------------------------
@app.get("/api")
async def api_info():
    return {"message": "SongByte Game API", "version": "2.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "songbyte"}

# --------------------------
# Inicializar base de datos
# --------------------------
@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        logger.info("✅ Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"❌ Error inicializando la base de datos: {e}")

# --------------------------
# Arrancar servidor
# --------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=5000, reload=True)
