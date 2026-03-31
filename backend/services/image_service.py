import io
from PIL import Image

SIZES = {
    "small":  (330, 336),
    "medium": (660, 673),
    "large":  (661, 674),
}


def validate_image(image_bytes: bytes) -> dict:
    """
    Valida que los bytes sean una imagen válida que Pillow pueda abrir.
    No restringe dimensiones: se acepta cualquier tamaño y se redimensiona automáticamente.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        w, h = img.size
        return {"valid": True, "width": w, "height": h, "error": None}
    except Exception as e:
        return {
            "valid": False,
            "width": 0,
            "height": 0,
            "error": f"No se pudo leer la imagen: {str(e)}",
        }


def generate_sizes(image_bytes: bytes) -> dict[str, bytes]:
    """
    Genera los 3 tamaños en WebP a partir de la imagen original.
    Usa LANCZOS para redimensionar con máxima calidad.
    Devuelve {"small": bytes, "medium": bytes, "large": bytes}
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    result = {}
    for name, (w, h) in SIZES.items():
        resized = img.resize((w, h), Image.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, format="WEBP", quality=85, method=6)
        result[name] = buf.getvalue()
    return result