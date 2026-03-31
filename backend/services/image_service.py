import io
from PIL import Image

# Tamaños objetivo
SIZES = {
    "small":  (330, 336),
    "medium": (660, 673),
    "large":  (661, 674),
}
TOLERANCE = 50  # ±px


def validate_image(image_bytes: bytes) -> dict:
    """
    Valida que la imagen tenga dimensiones compatibles con 'large' ±TOLERANCE.
    Devuelve {"valid": bool, "width": int, "height": int, "error": str|None}
    """
    img = Image.open(io.BytesIO(image_bytes))
    w, h = img.size
    tw, th = SIZES["large"]

    w_ok = (tw - TOLERANCE) <= w <= (tw + TOLERANCE)
    h_ok = (th - TOLERANCE) <= h <= (th + TOLERANCE)

    if not (w_ok and h_ok):
        return {
            "valid": False,
            "width": w,
            "height": h,
            "error": (
                f"Dimensiones recibidas: {w}×{h}px. "
                f"Se esperaba aproximadamente {tw}×{th}px "
                f"(tolerancia ±{TOLERANCE}px)."
            ),
        }
    return {"valid": True, "width": w, "height": h, "error": None}


def generate_sizes(image_bytes: bytes) -> dict[str, bytes]:
    """
    Genera los 3 tamaños en WebP a partir de la imagen original.
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