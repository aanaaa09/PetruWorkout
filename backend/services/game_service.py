from ..crud import cancion_crud
from ..services.spotify_service import SpotifyService
from ..services.itunes_service import ITunesService
from ..utils.fuzzy_match import verificar_respuesta
from ..utils.qr_generator import generar_qr_base64
from ..config.settings import settings
import random
import logging

logger = logging.getLogger(__name__)


class GameService:
    """Servicio de lógica del juego"""

    @staticmethod
    def sincronizar_playlist(db, playlist_key: str):
        """Sincroniza una playlist con la base de datos"""
        if playlist_key not in settings.PLAYLISTS:
            logger.error(f"Playlist {playlist_key} no encontrada")
            return False

        playlist_id = settings.PLAYLISTS[playlist_key]
        logger.info(f"Sincronizando playlist {playlist_key}...")

        # Obtener canciones de Spotify
        canciones_spotify = SpotifyService.obtener_canciones_playlist(playlist_id)
        if not canciones_spotify:
            logger.warning(f"No se obtuvieron canciones de Spotify para {playlist_key}")
            return False

        # IDs de Spotify
        spotify_ids_spotify = {c['spotify_id'] for c in canciones_spotify if c.get('spotify_id')}

        # IDs en BD
        ids_db = cancion_crud.get_spotify_ids(db, playlist_key)

        # Nuevas y eliminadas
        nuevas = spotify_ids_spotify - ids_db
        eliminadas = ids_db - spotify_ids_spotify

        # Guardar nuevas
        for cancion_data in canciones_spotify:
            if cancion_data['spotify_id'] in nuevas:
                cancion_crud.create(
                    db,
                    titulo=cancion_data['name'],
                    artista=cancion_data['artist'],
                    anio=cancion_data.get('year'),
                    spotify_id=cancion_data['spotify_id'],
                    spotify_url=cancion_data['spotify_url'],
                    playlist_key=playlist_key
                )

        # Eliminar obsoletas
        if eliminadas:
            cancion_crud.delete_by_spotify_ids(db, playlist_key, list(eliminadas))

        logger.info(f"Playlist {playlist_key} sincronizada: {len(nuevas)} nuevas, {len(eliminadas)} eliminadas")
        return True

    @staticmethod
    def obtener_cancion_para_adivinar(db, playlist_key: str):
        """Obtiene una canción aleatoria con preview"""
        if playlist_key not in settings.PLAYLISTS:
            logger.error(f"Playlist {playlist_key} no encontrada")
            return {}

        # Obtener canciones
        canciones = cancion_crud.get_all_by_playlist(db, playlist_key)

        # Si no hay, sincronizar
        if not canciones:
            logger.info(f"No hay canciones para {playlist_key}, sincronizando...")
            if GameService.sincronizar_playlist(db, playlist_key):
                canciones = cancion_crud.get_all_by_playlist(db, playlist_key)

            if not canciones:
                logger.error(f"No se pudieron obtener canciones para {playlist_key}")
                return {}

        # Inicializar servidas
        if playlist_key not in settings.SERVIDAS:
            settings.SERVIDAS[playlist_key] = set()

        # Filtrar disponibles
        disponibles = [
            c for c in canciones
            if f"{c.titulo}|{c.artista}" not in settings.SERVIDAS[playlist_key]
        ]

        # Resetear si no quedan
        if not disponibles:
            logger.info(f"Reseteando canciones servidas de {playlist_key}")
            settings.SERVIDAS[playlist_key].clear()
            disponibles = canciones[:]

        random.shuffle(disponibles)

        # Buscar preview
        for cancion in disponibles:
            preview = ITunesService.buscar_preview(cancion.titulo, cancion.artista)

            if preview:
                clave = f"{cancion.titulo}|{cancion.artista}"
                settings.SERVIDAS[playlist_key].add(clave)
                settings.CANCION_ACTUAL[playlist_key] = cancion

                logger.info(f"Canción servida: {cancion.titulo} - {cancion.artista}")

                return {
                    'preview_url': preview,
                    'playlist': playlist_key
                }

        logger.warning(f"No se encontró preview para {playlist_key}")
        return {}

    @staticmethod
    def verificar_respuesta(playlist_key: str, titulo_usuario: str, artista_usuario: str):
        """Verifica la respuesta del usuario"""
        if playlist_key not in settings.CANCION_ACTUAL:
            return {'error': 'No hay canción activa', 'correcto': False}

        cancion = settings.CANCION_ACTUAL[playlist_key]

        resultado = verificar_respuesta(
            cancion.titulo,
            cancion.artista,
            titulo_usuario,
            artista_usuario
        )

        if resultado['correcto']:
            qr_base64 = generar_qr_base64(cancion.spotify_url)

            return {
                'correcto': True,
                'titulo_real': cancion.titulo,
                'artista_real': cancion.artista,
                'spotify_url': cancion.spotify_url,
                'qr_code': qr_base64
            }
        else:
            mensaje = "❌ "
            if resultado['titulo_correcto'] and not resultado['artista_correcto']:
                mensaje += "¡Título correcto! Pero el artista no."
            elif resultado['artista_correcto'] and not resultado['titulo_correcto']:
                mensaje += "¡Artista correcto! Pero el título no."
            else:
                mensaje += "Título y artista incorrectos."

            return {
                'correcto': False,
                'mensaje': mensaje,
                'titulo_correcto': resultado['titulo_correcto'],
                'artista_correcto': resultado['artista_correcto']
            }

    @staticmethod
    def rendirse(playlist_key: str):
        """El usuario se rinde"""
        if playlist_key not in settings.CANCION_ACTUAL:
            return {'error': 'No hay canción activa'}

        cancion = settings.CANCION_ACTUAL[playlist_key]
        qr_base64 = generar_qr_base64(cancion.spotify_url)

        return {
            'titulo_real': cancion.titulo,
            'artista_real': cancion.artista,
            'spotify_url': cancion.spotify_url,
            'qr_code': qr_base64
        }