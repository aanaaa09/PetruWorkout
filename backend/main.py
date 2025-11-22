import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routers import auth, resenas, consultas
from .config.database import Base, engine
from .init_db import crear_base_datos

# --------------------------
# Logging
# --------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------
# Crear base de datos si no existe
# --------------------------
crear_base_datos()

# --------------------------
# Crear todas las tablas
# --------------------------
Base.metadata.create_all(bind=engine)
logger.info("✅ Tablas de la base de datos creadas/verificadas")

# --------------------------
# Crear app FastAPI
# --------------------------
app = FastAPI(
    title="PetruWorkout API",
    description="API de PetruWorkout",
    version="2.0"
)

# --------------------------
# CORS
# --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Routers API
# --------------------------
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(resenas.router)
app.include_router(consultas.router)

# --------------------------
# Health y info API
# --------------------------
@app.get("/api")
async def api_info():
    return {"message": "PetruWorkout API", "version": "2.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "petruworkout"}


# --------------------------
# Montar frontend SPA
# --------------------------
frontend_dist = os.path.join(os.path.dirname(__file__), "../frontend/dist")

if os.path.isdir(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        logger.info(f"✅ Frontend assets montados desde {assets_dir}")

    @app.get("/favicon.svg")
    async def favicon():
        favicon_path = os.path.join(frontend_dist, "favicon.svg")
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path)
        return {"error": "Favicon no encontrado"}

    @app.get("/")
    async def serve_root():
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend no encontrado"}

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path.startswith("api/"):
            return {"error": "Ruta API no encontrada"}, 404

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