import requests
import base64
import logging
from ..config.settings import settings, Settings

logger = logging.getLogger(__name__)


class SpotifyService:
    """Servicio para interactuar con la API de Spotify"""

    @staticmethod
    def obtener_token():
        """Obtiene un token de acceso de Spotify"""
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
                Settings.SPOTIFY_TOKEN = response.json()['access_token']  # ← Settings con mayúscula
                logger.info("Token de Spotify obtenido correctamente")
                return True
            else:
                logger.error(f"Error obteniendo token de Spotify: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Excepción obteniendo token de Spotify: {e}")
            return False

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