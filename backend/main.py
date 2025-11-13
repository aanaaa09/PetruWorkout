import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routers import auth, game, game_rondas, add_song
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
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Routers API (PRIMERO)
# --------------------------
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(game.router, tags=["game"])  # Sin prefix
app.include_router(game_rondas.router, tags=["rondas"])
app.include_router(add_song.router, tags=["add_song"])


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
# Montar frontend SPA (AL FINAL)
# --------------------------
frontend_dist = os.path.join(os.path.dirname(__file__), "../frontend/dist")

if os.path.isdir(frontend_dist):
    # Montar assets primero
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        logger.info(f"✅ Frontend assets montados desde {assets_dir}")


    # Servir favicon
    @app.get("/favicon.svg")
    async def favicon():
        favicon_path = os.path.join(frontend_dist, "favicon.svg")
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path)
        return {"error": "Favicon no encontrado"}


    # Servir index.html para la raíz
    @app.get("/")
    async def serve_root():
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend no encontrado"}


    # SPA fallback para client-side routing (DEBE SER EL ÚLTIMO)
    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # NO capturar rutas de API
        if full_path.startswith("api/"):
            return {"error": "Ruta API no encontrada"}, 404

        # Para cualquier otra ruta, servir index.html
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Página no encontrada"}, 404
else:
    logger.warning(f"⚠️ Frontend no encontrado en {frontend_dist}")


# --------------------------
# Arrancar servidor
# --------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=5000, reload=True)
