import requests
import urllib.parse
import logging
from ..config.settings import settings

logger = logging.getLogger(__name__)


class ITunesService:
    """Servicio para buscar previews de canciones en iTunes"""

    @staticmethod
    def buscar_preview(nombre_cancion, artista):
        """
        Busca el preview de una canción en iTunes

        Args:
            nombre_cancion (str): Nombre de la canción
            artista (str): Nombre del artista

        Returns:
            str: URL del preview (30 segundos)
            None: Si no se encuentra
        """
        # Verificar caché primero
        key = f"{nombre_cancion}|{artista}"
        if key in settings.CACHE_ITUNES:
            logger.debug(f"Preview encontrado en caché: {key}")
            return settings.CACHE_ITUNES[key]

        # Función auxiliar para hacer la búsqueda
        def _buscar(query):
            try:
                query_encoded = urllib.parse.quote(query)
                url = f"https://itunes.apple.com/search?term={query_encoded}&media=music&entity=song&limit=1"

                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])

                    if results:
                        preview_url = results[0].get('previewUrl')
                        if preview_url:
                            logger.info(f"Preview encontrado para: {query}")
                            return preview_url

            except Exception as e:
                logger.error(f"Error buscando en iTunes: {e}")

            return None

        # Intentar búsqueda normal
        preview = _buscar(f"{nombre_cancion} {artista}")

        # Si no funciona, invertir el orden
        if not preview:
            logger.debug(f"Reintentando búsqueda invertida para: {nombre_cancion} - {artista}")
            preview = _buscar(f"{artista} {nombre_cancion}")

        # Guardar en caché (incluso si es None para evitar búsquedas repetidas)
        settings.CACHE_ITUNES[key] = preview

        if preview:
            logger.info(f"Preview guardado en caché: {nombre_cancion} - {artista}")
        else:
            logger.warning(f"No se encontró preview para: {nombre_cancion} - {artista}")

        return preview

    @staticmethod
    def limpiar_cache():
        """Limpia el caché de iTunes"""
        settings.CACHE_ITUNES.clear()
        logger.info("Caché de iTunes limpiado")