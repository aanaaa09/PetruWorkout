# backend/services/content_service.py
"""
Lógica de negocio para la gestión del content.json de la landing.
Extraída de content_editor.py para mantener el router limpio.
"""

import json
import time
import logging

from . import github_service

logger = logging.getLogger(__name__)

CONTENT_JSON_PATH = "frontend/public/content.json"
IMAGES_BASE_PATH  = "frontend/public/images/results"
VIDEOS_BASE_PATH  = "frontend/public/videos"

ALLOWED_VIDEO_SLOTS = {"video1", "video2", "video3"}


# ──────────────────────────────────────────────────────────────────
# HELPERS INTERNOS
# ──────────────────────────────────────────────────────────────────

def _deep_merge(current: dict, incoming: dict) -> dict:
    """
    Merge profundo:
    - Dicts: merge recursivo por clave.
    - Listas (ej: results.users): reemplazar completo.
    - Escalares: reemplazar.
    """
    result = dict(current)
    for key, value in incoming.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _read_content_file() -> tuple[dict, str | None]:
    """
    Lee content.json del repo GitHub.
    Devuelve (contenido_dict, sha) o ({}, None) si no existe.
    """
    file = github_service.get_file(CONTENT_JSON_PATH)
    if not file:
        return {}, None
    return json.loads(file["content"]), file["sha"]


def _write_content_file(content: dict, sha: str | None, commit_msg: str) -> bool:
    """Serializa y hace commit de content.json."""
    content_bytes = json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")
    return github_service.commit_file(CONTENT_JSON_PATH, content_bytes, commit_msg, sha)


# ──────────────────────────────────────────────────────────────────
# API PÚBLICA
# ──────────────────────────────────────────────────────────────────

def get_content() -> dict:
    """Devuelve el contenido actual de content.json."""
    content, _ = _read_content_file()
    return content


def update_content(incoming: dict) -> bool:
    """
    Actualiza secciones del content.json con merge profundo.
    Devuelve True si el commit fue exitoso.
    """
    current, sha = _read_content_file()
    merged = _deep_merge(current, incoming) if current else incoming
    return _write_content_file(merged, sha, "admin: actualizar contenido landing")


def update_youtube_id(youtube_id: str) -> bool:
    """Actualiza solo el ID del vídeo de YouTube en content.json."""
    current, sha = _read_content_file()
    if "video" not in current:
        current["video"] = {}
    current["video"]["youtube_id"] = youtube_id
    return _write_content_file(current, sha, f"admin: actualizar YouTube ID → {youtube_id}")


def upload_result_image(name: str, image_bytes: bytes) -> dict:
    """
    Valida la imagen, genera 3 tamaños WebP y hace commit atómico.
    Actualiza _img_version en content.json para romper caché.

    Returns:
        dict con name y sizes (rutas públicas).
    Raises:
        ValueError si la imagen no es válida.
    """
    from .image_service import validate_image, generate_sizes

    validation = validate_image(image_bytes)
    if not validation["valid"]:
        raise ValueError(validation["error"])

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
        raise RuntimeError("Error al subir imagen a GitHub")

    # Bump _img_version para romper caché del browser
    try:
        current, sha = _read_content_file()
        if "results" not in current:
            current["results"] = {}
        current["results"]["_img_version"] = int(time.time())
        _write_content_file(current, sha, f"admin: bump _img_version tras subir imagen {name}")
    except Exception as e:
        logger.warning(f"No se pudo actualizar _img_version: {e}")

    return {
        "name":  name,
        "sizes": {s: f"/images/results/{name}-{s}.webp" for s in ("small", "medium", "large")},
    }


def upload_testimonial_video(slot: str, video_bytes: bytes) -> dict:
    """
    Sube un vídeo .mp4 de testimonio y hace commit.
    Actualiza _video_version en content.json para romper caché.

    Returns:
        dict con slot y path público.
    Raises:
        ValueError si el slot no es válido.
        RuntimeError si el commit falla.
    """
    if slot not in ALLOWED_VIDEO_SLOTS:
        raise ValueError(f"Slot inválido. Usa: {ALLOWED_VIDEO_SLOTS}")

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
        raise RuntimeError("Error al subir vídeo a GitHub")

    # Bump _video_version para romper caché
    try:
        current, sha_content = _read_content_file()
        if "results" not in current:
            current["results"] = {}
        current["results"]["_video_version"] = int(time.time())
        _write_content_file(current, sha_content, f"admin: bump _video_version tras subir vídeo {slot}")
    except Exception as e:
        logger.warning(f"No se pudo actualizar _video_version: {e}")

    return {"slot": slot, "path": f"/videos/{slot}.mp4"}