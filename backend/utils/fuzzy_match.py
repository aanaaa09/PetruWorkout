from rapidfuzz import fuzz
import unicodedata
import re
from ..config.settings import settings



def normalizar_texto(texto):
    """Normaliza texto para comparación fuzzy"""
    texto = unicodedata.normalize('NFD', texto.lower())
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto.strip()


def verificar_coincidencia_titulo(titulo_real, titulo_usuario):
    """
    Verifica coincidencia de título con reglas especiales
    Retorna el porcentaje de similitud (0-100)
    """
    if not titulo_usuario.strip():
        return 0

    titulo_real_norm = normalizar_texto(titulo_real)
    titulo_usuario_norm = normalizar_texto(titulo_usuario)

    # Eliminar "remix" del título real para la comparación
    titulo_real_sin_remix = re.sub(r'\b(remix|rmx)\b', '', titulo_real_norm).strip()

    # Calcular similitud con ambas versiones y tomar la mayor
    similitud1 = fuzz.ratio(titulo_real_norm, titulo_usuario_norm)
    similitud2 = fuzz.ratio(titulo_real_sin_remix, titulo_usuario_norm)

    return max(similitud1, similitud2)


def verificar_coincidencia_artista(artista_real, artista_usuario):
    """
    Verifica coincidencia de artista permitiendo múltiples artistas del usuario
    Retorna el porcentaje de similitud (0-100)
    """
    if not artista_usuario.strip():
        return 0

    artista_real_norm = normalizar_texto(artista_real)
    artista_usuario_norm = normalizar_texto(artista_usuario)

    # Separar artistas del usuario por comas, "y", "and", "ft", "feat"
    separadores = [',', ' y ', ' and ', ' ft ', ' feat ', ' featuring ']
    artistas_usuario = [artista_usuario_norm]

    for sep in separadores:
        nuevos_artistas = []
        for artista in artistas_usuario:
            nuevos_artistas.extend(artista.split(sep))
        artistas_usuario = [a.strip() for a in nuevos_artistas if a.strip()]

    # Calcular similitud con cada artista del usuario
    similitudes = []
    for artista_usr in artistas_usuario:
        similitud = fuzz.ratio(artista_real_norm, artista_usr)
        similitudes.append(similitud)

    # Retornar la mayor similitud encontrada
    return max(similitudes) if similitudes else 0


def verificar_respuesta(titulo_real, artista_real, titulo_usuario, artista_usuario):
    """
    Verifica si la respuesta del usuario es correcta

    Returns:
        dict: {
            'correcto': bool,
            'titulo_correcto': bool,
            'artista_correcto': bool,
            'similitud_titulo': int,
            'similitud_artista': int
        }
    """
    similitud_titulo = verificar_coincidencia_titulo(titulo_real, titulo_usuario)
    similitud_artista = verificar_coincidencia_artista(artista_real, artista_usuario)

    titulo_correcto = similitud_titulo >= settings.FUZZY_MATCH_THRESHOLD
    artista_correcto = similitud_artista >= settings.FUZZY_MATCH_THRESHOLD

    return {
        'correcto': titulo_correcto and artista_correcto,
        'titulo_correcto': titulo_correcto,
        'artista_correcto': artista_correcto,
        'similitud_titulo': similitud_titulo,
        'similitud_artista': similitud_artista
    }


def verificar_respuesta_solo_titulo(titulo_real, titulo_usuario):
    """
    Verifica SOLO el título con fuzzy match

    Args:
        titulo_real: título correcto de la canción
        titulo_usuario: título ingresado por el usuario

    Returns:
        dict: {
            'correcto': bool,
            'similitud': int (0-100)
        }
    """
    if not titulo_usuario or not titulo_usuario.strip():
        return {
            'correcto': False,
            'similitud': 0
        }

    similitud = verificar_coincidencia_titulo(titulo_real, titulo_usuario)

    return {
        'correcto': similitud >= settings.FUZZY_MATCH_THRESHOLD,
        'similitud': similitud
    }


def verificar_respuesta_solo_artista(artista_real, artista_usuario):
    """
    Verifica SOLO el artista con fuzzy match

    Args:
        artista_real: artista correcto de la canción
        artista_usuario: artista ingresado por el usuario

    Returns:
        dict: {
            'correcto': bool,
            'similitud': int (0-100)
        }
    """
    if not artista_usuario or not artista_usuario.strip():
        return {
            'correcto': False,
            'similitud': 0
        }

    similitud = verificar_coincidencia_artista(artista_real, artista_usuario)

    return {
        'correcto': similitud >= settings.FUZZY_MATCH_THRESHOLD,
        'similitud': similitud
    }


def verificar_respuesta_solo_anio(anio_real, anio_usuario):
    """
    Verifica SOLO el año (comparación exacta)

    Args:
        anio_real: año correcto de la canción
        anio_usuario: año ingresado por el usuario

    Returns:
        dict: {
            'correcto': bool,
            'diferencia': int (diferencia de años)
        }
    """
    if not anio_usuario or not str(anio_usuario).strip():
        return {
            'correcto': False,
            'diferencia': None
        }

    if not anio_real:
        return {
            'correcto': False,
            'diferencia': None
        }

    # Normalizar a strings y limpiar
    anio_real_str = str(anio_real).strip()
    anio_usuario_str = str(anio_usuario).strip()

    # Comparación exacta
    correcto = anio_real_str == anio_usuario_str

    # Calcular diferencia si ambos son números válidos
    diferencia = None
    try:
        diferencia = abs(int(anio_real_str) - int(anio_usuario_str))
    except (ValueError, TypeError):
        pass

    return {
        'correcto': correcto,
        'diferencia': diferencia
    }