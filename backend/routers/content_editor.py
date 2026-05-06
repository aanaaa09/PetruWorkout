# backend/routers/content_editor.py


import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.usuario import Usuario
from ..services.auth_service import verify_admin_token
from ..services import content_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/content", tags=["content-editor"])


@router.get("")
def get_content(admin: Usuario = Depends(verify_admin_token)):
    """Devuelve el JSON de contenido actual."""
    try:
        content = content_service.get_content()
        return {"success": True, "content": content}
    except Exception as e:
        logger.error(f"Error leyendo content.json: {e}")
        raise HTTPException(status_code=500, detail="Error al leer el contenido")


@router.put("")
def update_content(
    body: dict,
    admin: Usuario = Depends(verify_admin_token),
):
    """Actualiza secciones del content.json con merge profundo."""
    try:
        ok = content_service.update_content(body)
        if not ok:
            raise HTTPException(status_code=500, detail="Error al guardar en GitHub")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando content.json: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/youtube")
def update_youtube(
    youtube_id: str = Form(...),
    admin: Usuario = Depends(verify_admin_token),
):
    """Actualiza el ID del vídeo de YouTube."""
    try:
        ok = content_service.update_youtube_id(youtube_id)
        if not ok:
            raise HTTPException(status_code=500, detail="Error al guardar en GitHub")
        return {"success": True, "youtube_id": youtube_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando YouTube: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image")
async def upload_image(
    name: str = Form(...),
    file: UploadFile = File(...),
    admin: Usuario = Depends(verify_admin_token),
):
    """Sube imagen .webp, genera 3 tamaños y hace commit atómico."""
    if not file.filename.lower().endswith(".webp"):
        raise HTTPException(status_code=400, detail="Solo se aceptan imágenes .webp")

    try:
        image_bytes = await file.read()
        result = content_service.upload_result_image(name, image_bytes)
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error subiendo imagen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


