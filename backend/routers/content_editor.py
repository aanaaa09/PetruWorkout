"""
Endpoints para editar el contenido de la landing desde el panel de admin.
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header
from sqlalchemy.orm import Session
from typing import Optional

from ..config.database import get_db
from ..crud.sesion import sesion_crud
from ..crud.usuario import usuario_crud
from ..models.usuario import Usuario, TipoUsuario
from ..services import github_service
from ..services.image_service import validate_image, generate_sizes

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/content", tags=["content-editor"])

CONTENT_JSON_PATH = "frontend/public/content.json"
IMAGES_BASE_PATH  = "frontend/public/images/results"
VIDEOS_BASE_PATH  = "frontend/public/videos"


# ── Auth ──────────────────────────────────────────────────────────────────────

def verify_admin(token: str = Header(None, alias="token"), db: Session = Depends(get_db)) -> Usuario:
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    sesion = sesion_crud.validate_token(db, token)
    if not sesion:
        raise HTTPException(status_code=401, detail="Sesión expirada o inválida")
    usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
    if not usuario or usuario.tipo_usuario != TipoUsuario.ADMIN:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return usuario


def _get_content() -> dict:
    """Lee content.json del repo. Si no existe, devuelve estructura vacía."""
    file = github_service.get_file(CONTENT_JSON_PATH)
    if not file:
        return {}
    return json.loads(file["content"])


def _get_content_with_sha() -> tuple[dict, str | None]:
    file = github_service.get_file(CONTENT_JSON_PATH)
    if not file:
        return {}, None
    return json.loads(file["content"]), file["sha"]


def _deep_merge(current: dict, incoming: dict) -> dict:
    """
    Merge profundo:
    - Para dicts: merge recursivo por clave
    - Para listas (como results.users): reemplazar completo
    - Para escalares: reemplazar
    """
    result = dict(current)
    for key, value in incoming.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            # Listas, strings, números → reemplazar directamente
            result[key] = value
    return result


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("")
def get_content(admin: Usuario = Depends(verify_admin)):
    """Devuelve el JSON de contenido actual."""
    try:
        content = _get_content()
        return {"success": True, "content": content}
    except Exception as e:
        logger.error(f"Error leyendo content.json: {e}")
        raise HTTPException(status_code=500, detail="Error al leer el contenido")


@router.put("")
def update_content(
    body: dict,
    admin: Usuario = Depends(verify_admin),
):
    """
    Actualiza secciones del content.json.
    Usa merge profundo: dicts se mergean, listas se reemplazan.
    """
    try:
        current, sha = _get_content_with_sha()

        if not current and sha is None:
            # El archivo no existe aún en GitHub → será creado
            merged = body
        else:
            merged = _deep_merge(current, body)

        content_bytes = json.dumps(merged, ensure_ascii=False, indent=2).encode("utf-8")
        ok = github_service.commit_file(
            CONTENT_JSON_PATH,
            content_bytes,
            "admin: actualizar contenido landing",
            sha,
        )
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
    admin: Usuario = Depends(verify_admin),
):
    """Actualiza el ID del vídeo de YouTube."""
    try:
        current, sha = _get_content_with_sha()
        if "video" not in current:
            current["video"] = {}
        current["video"]["youtube_id"] = youtube_id

        content_bytes = json.dumps(current, ensure_ascii=False, indent=2).encode("utf-8")
        ok = github_service.commit_file(
            CONTENT_JSON_PATH,
            content_bytes,
            f"admin: actualizar YouTube ID → {youtube_id}",
            sha,
        )
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
    admin: Usuario = Depends(verify_admin),
):
    """
    Sube imagen .webp, genera 3 tamaños y hace commit atómico.
    name = image_slug del usuario (ej: "user1")
    """
    if not file.filename.lower().endswith(".webp"):
        raise HTTPException(status_code=400, detail="Solo se aceptan imágenes .webp")

    image_bytes = await file.read()

    validation = validate_image(image_bytes)
    if not validation["valid"]:
        raise HTTPException(status_code=422, detail=validation["error"])

    sizes = generate_sizes(image_bytes)

    files_to_commit = [
        {"path": f"{IMAGES_BASE_PATH}/{name}-small.webp",  "content_bytes": sizes["small"]},
        {"path": f"{IMAGES_BASE_PATH}/{name}-medium.webp", "content_bytes": sizes["medium"]},
        {"path": f"{IMAGES_BASE_PATH}/{name}-large.webp",  "content_bytes": sizes["large"]},
    ]

    ok = github_service.commit_multiple_files(
        files_to_commit,
        f"admin: subir imagen results → {name} (3 tamaños)",
    )
    if not ok:
        raise HTTPException(status_code=500, detail="Error al subir imagen a GitHub")

    return {
        "success": True,
        "name": name,
        "sizes": {s: f"/images/results/{name}-{s}.webp" for s in ("small", "medium", "large")},
    }


@router.post("/video")
async def upload_video(
    slot: str = Form(...),
    file: UploadFile = File(...),
    admin: Usuario = Depends(verify_admin),
):
    """Sube un vídeo .mp4 de testimonio y hace commit."""
    if not file.filename.lower().endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Solo se aceptan vídeos .mp4")

    allowed_slots = {"video1", "video2", "video3"}
    if slot not in allowed_slots:
        raise HTTPException(status_code=400, detail=f"Slot inválido. Usa: {allowed_slots}")

    video_bytes = await file.read()
    path = f"{VIDEOS_BASE_PATH}/{slot}.mp4"

    existing = github_service.get_file(path)
    sha = existing["sha"] if existing else None

    ok = github_service.commit_file(
        path,
        video_bytes,
        f"admin: actualizar vídeo testimonio → {slot}",
        sha,
    )
    if not ok:
        raise HTTPException(status_code=500, detail="Error al subir vídeo a GitHub")

    return {"success": True, "slot": slot, "path": f"/videos/{slot}.mp4"}