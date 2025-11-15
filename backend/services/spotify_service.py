import requests
import base64
import logging
from ..config.settings import settings, Settings

logger = logging.getLogger(__name__)


class SpotifyService:
    """Servicio para interactuar con la API de Spotify"""

    @staticmethod
    def obtener_token():
        """Obtiene un token de acceso de Spotify (Client Credentials)"""
        from backend.config import settings

        auth_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        headers = {"Authorization": f"Basic {b64_auth_str}"}
        data = {"grant_type": "client_credentials"}

        try:
            response = requests.post(
                "https://accounts.spotify.com/api/token",
                headers=headers,
                data=data,
                timeout=10
            )

            if response.status_code == 200:
                Settings.SPOTIFY_TOKEN = response.json()['access_token']
                logger.info("Token de Spotify obtenido correctamente")
                return True
            else:
                logger.error(f"Error obteniendo token de Spotify: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Excepción obteniendo token de Spotify: {e}")
            return False

    @staticmethod
    def refrescar_token_usuario():
        """
        Refresca el access token usando el refresh token
        Este token permite modificar playlists del usuario
        """
        from backend.config import settings

        if not settings.SPOTIFY_REFRESH_TOKEN:
            logger.error("No hay SPOTIFY_REFRESH_TOKEN configurado")
            return False

        auth_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        headers = {"Authorization": f"Basic {b64_auth_str}"}
        data = {
            "grant_type": "refresh_token",
            "refresh_token": settings.SPOTIFY_REFRESH_TOKEN
        }

        try:
            response = requests.post(
                "https://accounts.spotify.com/api/token",
                headers=headers,
                data=data,
                timeout=10
            )

            if response.status_code == 200:
                token_data = response.json()
                Settings.SPOTIFY_USER_TOKEN = token_data['access_token']

                # Algunos refresh pueden devolver un nuevo refresh_token
                if 'refresh_token' in token_data:
                    Settings.SPOTIFY_REFRESH_TOKEN = token_data['refresh_token']

                logger.info("Token de usuario de Spotify refrescado correctamente")
                return True
            else:
                logger.error(f"Error refrescando token de usuario: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Excepción refrescando token de usuario: {e}")
            return False

    @staticmethod
    def agregar_cancion_a_playlist(playlist_id, spotify_track_id):
        """
        Agrega una canción a una playlist de Spotify

        Args:
            playlist_id (str): ID de la playlist en Spotify
            spotify_track_id (str): ID de la canción en Spotify

        Returns:
            bool: True si se agregó correctamente, False en caso contrario
        """
        from backend.config import settings

        # Asegurar que tenemos un token de usuario válido
        if not hasattr(Settings, 'SPOTIFY_USER_TOKEN') or not Settings.SPOTIFY_USER_TOKEN:
            if not SpotifyService.refrescar_token_usuario():
                logger.error("No se pudo obtener token de usuario")
                return False

        headers = {
            'Authorization': f'Bearer {Settings.SPOTIFY_USER_TOKEN}',
            'Content-Type': 'application/json'
        }

        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        data = {
            'uris': [f'spotify:track:{spotify_track_id}']
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)

            # Si el token expiró, renovar y reintentar
            if response.status_code == 401:
                if SpotifyService.refrescar_token_usuario():
                    headers['Authorization'] = f'Bearer {Settings.SPOTIFY_USER_TOKEN}'
                    response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code in [200, 201]:
                logger.info(f"Canción {spotify_track_id} agregada a playlist {playlist_id}")
                return True
            else:
                logger.error(f"Error agregando canción a playlist: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Excepción agregando canción a playlist: {e}")
            return False

    @staticmethod
    def buscar_cancion(nombre, artista):
        """
        Busca una canción en Spotify por nombre y artista

        Args:
            nombre (str): Nombre de la canción
            artista (str): Nombre del artista

        Returns:
            dict: Información de la canción encontrada o None
        """
        from backend.config import settings

        if not Settings.SPOTIFY_TOKEN:
            if not SpotifyService.obtener_token():
                return None

        headers = {'Authorization': f'Bearer {Settings.SPOTIFY_TOKEN}'}

        # Crear query de búsqueda
        query = f'track:{nombre} artist:{artista}'
        url = f'https://api.spotify.com/v1/search?q={query}&type=track&limit=1'

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 401:
                if SpotifyService.obtener_token():
                    headers['Authorization'] = f'Bearer {Settings.SPOTIFY_TOKEN}'
                    response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                tracks = data.get('tracks', {}).get('items', [])

                if tracks:
                    track = tracks[0]
                    anio = None
                    if 'album' in track and 'release_date' in track['album']:
                        try:
                            anio = int(track['album']['release_date'][:4])
                        except (ValueError, IndexError):
                            anio = None

                    return {
                        'name': track['name'],
                        'artist': track['artists'][0]['name'] if track.get('artists') else 'Artista desconocido',
                        'spotify_url': track.get('external_urls', {}).get('spotify', ''),
                        'spotify_id': track.get('id', ''),
                        'year': anio
                    }
                else:
                    logger.warning(f"No se encontró la canción: {nombre} - {artista}")
                    return None
            else:
                logger.error(f"Error buscando canción: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Excepción buscando canción: {e}")
            return None

    @staticmethod
    def obtener_canciones_playlist(playlist_id):
        """
        Obtiene todas las canciones de una playlist de Spotify

        Args:
            playlist_id (str): ID de la playlist en Spotify

        Returns:
            list: Lista de diccionarios con info de canciones
        """
        from backend.config import settings

        if not Settings.SPOTIFY_TOKEN:
            if not SpotifyService.obtener_token():
                return []

        headers = {'Authorization': f'Bearer {Settings.SPOTIFY_TOKEN}'}
        canciones = []
        offset = 0
        limit = 100

        while True:
            url = (
                f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
                f'?limit={limit}&offset={offset}'
                f'&fields=items(track(name,artists(name),external_urls(spotify),id,album(release_date)))'
            )

            try:
                response = requests.get(url, headers=headers, timeout=15)

                # Si el token expiró, renovar
                if response.status_code == 401:
                    if SpotifyService.obtener_token():
                        headers['Authorization'] = f'Bearer {Settings.SPOTIFY_TOKEN}'
                        response = requests.get(url, headers=headers, timeout=15)

                    if response.status_code != 200:
                        logger.error(f"Error renovando token: {response.status_code}")
                        return []

                elif response.status_code != 200:
                    logger.error(f"Error obteniendo playlist: {response.status_code}")
                    return []

                data = response.json()
                items = data.get('items', [])

                if not items:
                    break

                # Procesar canciones
                for item in items:
                    track = item.get('track')
                    if track and track.get('name'):
                        # Extraer año del álbum
                        anio = None
                        if 'album' in track and 'release_date' in track['album']:
                            try:
                                anio = int(track['album']['release_date'][:4])
                            except (ValueError, IndexError):
                                anio = None

                        canciones.append({
                            'name': track['name'],
                            'artist': track['artists'][0]['name'] if track.get('artists') else 'Artista desconocido',
                            'spotify_url': track.get('external_urls', {}).get('spotify', ''),
                            'spotify_id': track.get('id', ''),
                            'year': anio
                        })

                # Verificar si hay más páginas
                if len(items) < limit:
                    break

                offset += limit

                # Límite de seguridad
                if offset > 2000:
                    break

            except Exception as e:
                logger.error(f"Excepción obteniendo canciones de Spotify: {e}")
                break

        logger.info(f"Obtenidas {len(canciones)} canciones de Spotify")
        return canciones