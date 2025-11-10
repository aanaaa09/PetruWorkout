import qrcode
import io
import base64
import logging

logger = logging.getLogger(__name__)


def generar_qr_base64(url):
    """
    Genera un código QR en formato base64 para una URL

    Args:
        url (str): URL para generar el código QR

    Returns:
        str: Código QR en formato base64 (data:image/png;base64,...)
        None: Si hay un error
    """
    try:
        # Crear código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Generar imagen
        img = qr.make_image(fill_color="black", back_color="white")

        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    except Exception as e:
        logger.error(f"Error generando código QR: {e}")
        return None