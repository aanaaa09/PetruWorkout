import base64
import requests
import logging
from ..config.settings import settings

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


def _headers():
    return {
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }


def get_file(path: str) -> dict | None:
    """Obtiene contenido + SHA de un fichero del repo."""
    url = f"{GITHUB_API}/repos/{settings.GITHUB_REPO}/contents/{path}?ref={settings.GITHUB_BRANCH}"
    r = requests.get(url, headers=_headers(), timeout=15)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    data = r.json()
    return {
        "content": base64.b64decode(data["content"]).decode("utf-8"),
        "sha": data["sha"],
    }


def commit_file(path: str, content_bytes: bytes, message: str, sha: str | None = None) -> bool:
    """Sube/actualiza un fichero. content_bytes puede ser texto o binario."""
    url = f"{GITHUB_API}/repos/{settings.GITHUB_REPO}/contents/{path}"
    payload = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode("utf-8"),
        "branch": settings.GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(url, json=payload, headers=_headers(), timeout=30)
    if r.status_code in (200, 201):
        logger.info(f"✅ Commit OK: {path}")
        return True
    logger.error(f"❌ Commit error {r.status_code}: {r.text[:300]}")
    return False


def commit_multiple_files(files: list[dict], message: str) -> bool:
    """
    Commit atómico de varios ficheros usando Git Trees API.
    files = [{"path": "...", "content_bytes": b"..."}]
    """
    base = f"{GITHUB_API}/repos/{settings.GITHUB_REPO}"
    hdrs = _headers()

    # 1. Obtener el SHA del último commit en la branch
    ref_r = requests.get(f"{base}/git/ref/heads/{settings.GITHUB_BRANCH}", headers=hdrs, timeout=15)
    ref_r.raise_for_status()
    latest_commit_sha = ref_r.json()["object"]["sha"]

    # 2. Obtener el tree SHA del commit
    commit_r = requests.get(f"{base}/git/commits/{latest_commit_sha}", headers=hdrs, timeout=15)
    commit_r.raise_for_status()
    base_tree_sha = commit_r.json()["tree"]["sha"]

    # 3. Crear blobs para cada fichero
    tree_items = []
    for f in files:
        blob_r = requests.post(f"{base}/git/blobs", headers=hdrs, timeout=30, json={
            "content": base64.b64encode(f["content_bytes"]).decode("utf-8"),
            "encoding": "base64",
        })
        blob_r.raise_for_status()
        tree_items.append({
            "path": f["path"],
            "mode": "100644",
            "type": "blob",
            "sha": blob_r.json()["sha"],
        })

    # 4. Crear el tree
    tree_r = requests.post(f"{base}/git/trees", headers=hdrs, timeout=15, json={
        "base_tree": base_tree_sha,
        "tree": tree_items,
    })
    tree_r.raise_for_status()
    new_tree_sha = tree_r.json()["sha"]

    # 5. Crear el commit
    new_commit_r = requests.post(f"{base}/git/commits", headers=hdrs, timeout=15, json={
        "message": message,
        "tree": new_tree_sha,
        "parents": [latest_commit_sha],
    })
    new_commit_r.raise_for_status()
    new_commit_sha = new_commit_r.json()["sha"]

    # 6. Avanzar la ref de la branch
    update_r = requests.patch(
        f"{base}/git/refs/heads/{settings.GITHUB_BRANCH}",
        headers=hdrs, timeout=15,
        json={"sha": new_commit_sha},
    )
    if update_r.status_code in (200, 201):
        logger.info(f"✅ Multi-commit OK: {[f['path'] for f in files]}")
        return True
    logger.error(f"❌ Multi-commit error: {update_r.text[:300]}")
    return False