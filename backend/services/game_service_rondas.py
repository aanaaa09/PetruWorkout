from sqlalchemy.orm import Session
from ..crud import cancion_crud
from ..services.spotify_service import SpotifyService
from ..services.itunes_service import ITunesService
from ..utils.fuzzy_match import (
    verificar_respuesta_solo_titulo,
    verificar_respuesta_solo_artista,
    verificar_respuesta_solo_anio
)
from ..utils.qr_generator import generar_qr_base64
from ..config.settings import settings
import random
import logging

logger = logging.getLogger(__name__)


class GameServiceRondas:
    """Servicio de lógica del juego por rondas"""

    @staticmethod
    def obtener_cancion_ronda(db: Session, playlist_key: str):
        """Obtiene una canción para la ronda actual"""
        if playlist_key not in settings.PLAYLISTS:
            logger.error(f"Playlist {playlist_key} no encontrada")
            return {}

        # Verificar ronda activa
        if playlist_key not in settings.RONDAS_ACTIVAS:
            return {'error': 'No hay ronda activa. Inicia una ronda primero.'}

        ronda = settings.RONDAS_ACTIVAS[playlist_key]

        # Verificar si terminó
        if ronda['preguntas_respondidas'] >= settings.PREGUNTAS_POR_RONDA:
            return {
                'error': 'Ronda completada',
                'finalizar': True,
                'puntos_totales': ronda['puntos_acumulados']
            }

        # Obtener canciones
        canciones = cancion_crud.get_all_by_playlist(db, playlist_key)

        if not canciones:
            logger.info(f"No hay canciones para {playlist_key}, sincronizando...")
            from ..services.game_service import GameService
            if GameService.sincronizar_playlist(db, playlist_key):
                canciones = cancion_crud.get_all_by_playlist(db, playlist_key)
            if not canciones:
                logger.error(f"No se pudieron obtener canciones para {playlist_key}")
                return {}

        # Inicializar servidas
        if playlist_key not in settings.SERVIDAS:
            settings.SERVIDAS[playlist_key] = set()

        # Inicializar servidas en ronda
        if 'canciones_ronda' not in ronda:
            ronda['canciones_ronda'] = set()

        # Filtrar disponibles
        disponibles = [
            c for c in canciones
            if f"{c.titulo}|{c.artista}" not in ronda['canciones_ronda']
        ]

        # Resetear si no quedan
        if not disponibles:
            logger.warning(f"No quedan canciones en {playlist_key}")
            ronda['canciones_ronda'].clear()
            disponibles = canciones[:]

        random.shuffle(disponibles)

        # Tipos de pregunta
        tipos_pregunta = ['solo_titulo', 'solo_artista', 'solo_anio']
        ultimo_tipo = ronda.get('tipo_pregunta_actual')

        # Evitar repetir tipo
        tipos_disponibles = [t for t in tipos_pregunta if t != ultimo_tipo]
        tipo_pregunta = random.choice(tipos_disponibles if tipos_disponibles else tipos_pregunta)
        ronda['tipo_pregunta_actual'] = tipo_pregunta

        # Buscar canción con preview
        for cancion in disponibles:
            # Si es año, verificar que tenga
            if tipo_pregunta == 'solo_anio' and not cancion.anio:
                continue

            preview = ITunesService.buscar_preview(cancion.titulo, cancion.artista)

            if preview:
                clave = f"{cancion.titulo}|{cancion.artista}"

                # Marcar como servida
                ronda['canciones_ronda'].add(clave)
                settings.SERVIDAS[playlist_key].add(clave)

                # Guardar actual
                settings.CANCION_ACTUAL[playlist_key] = cancion

                logger.info(f"Canción servida: {cancion.titulo} - {cancion.artista}, Tipo: {tipo_pregunta}")

                return {
                    'preview_url': preview,
                    'playlist': playlist_key,
                    'tipo_pregunta': tipo_pregunta,
                    'pregunta_numero': ronda['preguntas_respondidas'] + 1,
                    'total_preguntas': settings.PREGUNTAS_POR_RONDA,
                    'puntos_actuales': ronda['puntos_acumulados'],
                    'racha_actual': ronda['racha_actual']
                }

        logger.warning(f"No se encontró preview para {playlist_key}")
        return {}

    @staticmethod
    def iniciar_ronda(playlist_key: str, usuario_id: int):
        """Inicia una nueva ronda"""
        settings.RONDAS_ACTIVAS[playlist_key] = {
            'usuario_id': usuario_id,
            'preguntas_respondidas': 0,
            'puntos_acumulados': 0,
            'racha_actual': 0,
            'tipo_pregunta_actual': None,
            'canciones_ronda': set()
        }
        logger.info(f"Ronda iniciada para usuario {usuario_id} en {playlist_key}")
        return True

    @staticmethod
    def verificar_respuesta_ronda(db: Session, playlist_key: str, titulo_usuario: str,
                                   artista_usuario: str, anio_usuario: str):
        """Verifica la respuesta del usuario en la ronda"""
        if playlist_key not in settings.RONDAS_ACTIVAS:
            return {'error': 'No hay ronda activa'}

        if playlist_key not in settings.CANCION_ACTUAL:
            return {'error': 'No hay canción actual'}

        ronda = settings.RONDAS_ACTIVAS[playlist_key]
        cancion = settings.CANCION_ACTUAL[playlist_key]
        tipo_pregunta = ronda.get('tipo_pregunta_actual', 'solo_titulo')

        # Datos reales
        titulo_real = cancion.titulo
        artista_real = cancion.artista
        anio_real = cancion.anio

        # Variables de evaluación
        correcto_final = False
        puntos_ganados = 0
        similitud = 0
        diferencia_anio = None
        mensaje = ""

        # Evaluar según tipo
        if tipo_pregunta == 'solo_titulo':
            resultado_fuzzy = verificar_respuesta_solo_titulo(titulo_real, titulo_usuario)
            correcto_final = resultado_fuzzy['correcto']
            similitud = resultado_fuzzy['similitud']

            if correcto_final:
                puntos_ganados = settings.PUNTOS_TITULO
                mensaje = f"✅ ¡Correcto! ({int(similitud)}% similitud)<br><strong>{titulo_real}</strong> - {artista_real}"
            else:
                mensaje = f"❌ Incorrecto ({int(similitud)}% similitud)<br>Era: <strong>{titulo_real}</strong> - {artista_real}"

        elif tipo_pregunta == 'solo_artista':
            resultado_fuzzy = verificar_respuesta_solo_artista(artista_real, artista_usuario)
            correcto_final = resultado_fuzzy['correcto']
            similitud = resultado_fuzzy['similitud']

            # DESPUÉS:
            if correcto_final:
                puntos_ganados = settings.PUNTOS_ARTISTA
                mensaje = f"✅ ¡Correcto! ({int(similitud)}% similitud)<br><strong>{titulo_real}</strong> - {artista_real}"
            else:
                mensaje = f"❌ Incorrecto ({int(similitud)}% similitud)<br>Era: {artista_real}<br>Canción: <strong>{titulo_real}</strong>"

        elif tipo_pregunta == 'solo_anio':
            resultado_fuzzy = verificar_respuesta_solo_anio(anio_real, anio_usuario)
            correcto_final = resultado_fuzzy['correcto']
            diferencia_anio = resultado_fuzzy['diferencia']

            if not anio_real:
                mensaje = f"❌ Esta canción no tiene año registrado<br><strong>{titulo_real}</strong> - {artista_real}"
                correcto_final = False
            elif correcto_final:
                puntos_ganados = settings.PUNTOS_ANIO
                mensaje = f"✅ ¡Correcto!<br><strong>{titulo_real}</strong> - {artista_real} ({anio_real})"
            else:
                if diferencia_anio is not None:
                    mensaje = f"❌ Incorrecto (te alejaste {diferencia_anio} años)<br>Era: {anio_real}<br><strong>{titulo_real}</strong> - {artista_real}"
                else:
                    mensaje = f"❌ Incorrecto<br>Era: {anio_real}<br><strong>{titulo_real}</strong> - {artista_real}"

        # Calcular bonus por racha
        bonus_racha = 0
        if correcto_final:
            ronda['racha_actual'] += 1
            # Bonus cada 3 correctas
            if ronda['racha_actual'] % 3 == 0:
                bonus_racha = settings.BONUS_RACHA
                puntos_ganados += bonus_racha
        else:
            ronda['racha_actual'] = 0

        # Actualizar puntos y preguntas
        ronda['puntos_acumulados'] += puntos_ganados
        ronda['preguntas_respondidas'] += 1

        # Verificar si terminó
        ronda_terminada = ronda['preguntas_respondidas'] >= settings.PREGUNTAS_POR_RONDA

        # Generar QR si correcto
        qr_code = None
        spotify_url = None
        if correcto_final:
            spotify_url = f"https://open.spotify.com/track/{cancion.spotify_id}"
            qr_code = generar_qr_base64(spotify_url)

        # Si terminó, sumar puntos al usuario
        puntos_finales_usuario = ronda['puntos_acumulados']
        if ronda_terminada:
            from ..crud.usuario import usuario_crud
            usuario = usuario_crud.get_by_id(db, ronda['usuario_id'])
            if usuario:
                usuario_crud.add_points(db, usuario.id, int(ronda['puntos_acumulados']))
                puntos_finales_usuario = usuario.puntos

        resultado = {
            'correcto': correcto_final,
            'similitud': similitud,
            'diferencia_anio': diferencia_anio,
            'puntos_ganados': puntos_ganados,
            'bonus_racha': bonus_racha,
            'racha_actual': ronda['racha_actual'],
            'puntos_totales': ronda['puntos_acumulados'],
            'pregunta_numero': ronda['preguntas_respondidas'],
            'total_preguntas': settings.PREGUNTAS_POR_RONDA,
            'ronda_terminada': ronda_terminada,
            'puntos_finales_usuario': puntos_finales_usuario,
            'titulo_real': titulo_real,
            'artista_real': artista_real,
            'anio_real': anio_real if anio_real else None,
            'tipo_pregunta': tipo_pregunta,
            'qr_code': qr_code,
            'spotify_url': spotify_url,
            'mensaje': mensaje
        }

        return resultado

    @staticmethod
    def rendirse_ronda(db: Session, playlist_key: str):
        """El usuario se rinde"""
        if playlist_key not in settings.RONDAS_ACTIVAS:
            return {'error': 'No hay ronda activa'}

        if playlist_key not in settings.CANCION_ACTUAL:
            return {'error': 'No hay canción actual'}

        ronda = settings.RONDAS_ACTIVAS[playlist_key]
        cancion = settings.CANCION_ACTUAL[playlist_key]

        # Resetear racha
        ronda['racha_actual'] = 0
        ronda['preguntas_respondidas'] += 1

        # Verificar si terminó
        ronda_terminada = ronda['preguntas_respondidas'] >= settings.PREGUNTAS_POR_RONDA

        # Generar QR
        spotify_url = f"https://open.spotify.com/track/{cancion.spotify_id}"
        qr_code = generar_qr_base64(spotify_url)

        # Si terminó, sumar puntos
        puntos_finales_usuario = ronda['puntos_acumulados']
        if ronda_terminada:
            from ..crud.usuario import usuario_crud
            usuario = usuario_crud.get_by_id(db, ronda['usuario_id'])
            if usuario:
                usuario_crud.add_points(db, usuario.id, int(ronda['puntos_acumulados']))
                puntos_finales_usuario = usuario.puntos

        return {
            'correcto': False,
            'titulo_real': cancion.titulo,
            'artista_real': cancion.artista,
            'anio_real': cancion.anio,
            'qr_code': qr_code,
            'spotify_url': spotify_url,
            'pregunta_numero': ronda['preguntas_respondidas'],
            'total_preguntas': settings.PREGUNTAS_POR_RONDA,
            'puntos_totales': ronda['puntos_acumulados'],
            'racha_actual': ronda['racha_actual'],
            'ronda_terminada': ronda_terminada,
            'puntos_finales_usuario': puntos_finales_usuario
        }

    @staticmethod
    def finalizar_ronda(db: Session, playlist_key: str):
        """Finaliza una ronda manualmente"""
        if playlist_key not in settings.RONDAS_ACTIVAS:
            return {'error': 'No hay ronda activa'}

        ronda = settings.RONDAS_ACTIVAS[playlist_key]

        from ..crud.usuario import usuario_crud
        usuario = usuario_crud.get_by_id(db, ronda['usuario_id'])
        if usuario:
            usuario_crud.add_points(db, usuario.id, int(ronda['puntos_acumulados']))
            puntos_finales = usuario.puntos
        else:
            puntos_finales = 0

        puntos_ronda = ronda['puntos_acumulados']
        preguntas_respondidas = ronda['preguntas_respondidas']

        # Limpiar ronda
        del settings.RONDAS_ACTIVAS[playlist_key]

        return {
            'puntos_ronda': puntos_ronda,
            'preguntas_respondidas': preguntas_respondidas,
            'puntos_totales_usuario': puntos_finales
        }

    @staticmethod
    def obtener_estado_ronda(playlist_key: str):
        """Obtiene el estado actual de la ronda"""
        if playlist_key not in settings.RONDAS_ACTIVAS:
            return {'error': 'No hay ronda activa'}

        ronda = settings.RONDAS_ACTIVAS[playlist_key]

        return {
            'preguntas_respondidas': ronda['preguntas_respondidas'],
            'total_preguntas': settings.PREGUNTAS_POR_RONDA,
            'puntos_acumulados': ronda['puntos_acumulados'],
            'racha_actual': ronda['racha_actual']
        }