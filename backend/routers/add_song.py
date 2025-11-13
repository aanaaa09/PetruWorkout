from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..config.database import get_db
from ..services.spotify_service import SpotifyService
from ..crud.cancion import cancion_crud
from ..config.settings import settings, Settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["add_song"])


class BuscarCancionRequest(BaseModel):
    spotify_id: str
    playlist_key: str


class AñadirCancionRequest(BaseModel):
    playlist_key: str
    spotify_id: str
    anio: int = None


@router.post("/buscar-cancion")
async def buscar_cancion(data: BuscarCancionRequest, db: Session = Depends(get_db)):
    """Busca información de una canción por su ID de Spotify"""

    # Validar que la playlist existe
    if data.playlist_key not in settings.PLAYLISTS:
        raise HTTPException(status_code=400, detail="Playlist no válida")

    # Verificar si la canción ya existe en la playlist
    canciones_existentes = cancion_crud.get_all_by_playlist(db, data.playlist_key)
    spotify_ids_existentes = {c.spotify_id for c in canciones_existentes}

    if data.spotify_id in spotify_ids_existentes:
        return {
            'error': 'Esta canción ya existe en la playlist seleccionada'
        }

    # Obtener token de Spotify
    if not Settings.SPOTIFY_TOKEN:
        if not SpotifyService.obtener_token():
            raise HTTPException(status_code=500, detail="Error obteniendo token de Spotify")

    # Buscar la canción en Spotify
    try:
        import requests

        headers = {'Authorization': f'Bearer {Settings.SPOTIFY_TOKEN}'}
        url = f'https://api.spotify.com/v1/tracks/{data.spotify_id}'

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 401:
            # Token expirado, renovar
            if SpotifyService.obtener_token():
                headers['Authorization'] = f'Bearer {Settings.SPOTIFY_TOKEN}'
                response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 404:
            return {'error': 'Canción no encontrada en Spotify'}

        if response.status_code != 200:
            return {'error': f'Error al buscar en Spotify: {response.status_code}'}

        track_data = response.json()

        # Extraer información
        titulo = track_data.get('name', 'Sin título')
        artista = track_data['artists'][0]['name'] if track_data.get('artists') else 'Artista desconocido'
        preview_url = track_data.get('preview_url')
        spotify_url = track_data.get('external_urls', {}).get('spotify', '')

        # Extraer año
        anio_spotify = None
        if 'album' in track_data and 'release_date' in track_data['album']:
            try:
                anio_spotify = int(track_data['album']['release_date'][:4])
            except (ValueError, IndexError):
                anio_spotify = None

        logger.info(f"Canción encontrada: {titulo} - {artista}")

        return {
            'titulo': titulo,
            'artista': artista,
            'anio_spotify': anio_spotify,
            'preview_url': preview_url,
            'spotify_url': spotify_url,
            'spotify_id': data.spotify_id
        }

    except Exception as e:
        logger.error(f"Error buscando canción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al buscar la canción: {str(e)}")


@router.post("/añadir-cancion")
async def añadir_cancion(data: AñadirCancionRequest, db: Session = Depends(get_db)):
    """Añade una canción a una playlist"""

    # Validar playlist
    if data.playlist_key not in settings.PLAYLISTS:
        raise HTTPException(status_code=400, detail="Playlist no válida")

    # Verificar que no exista ya
    canciones_existentes = cancion_crud.get_all_by_playlist(db, data.playlist_key)
    spotify_ids_existentes = {c.spotify_id for c in canciones_existentes}

    if data.spotify_id in spotify_ids_existentes:
        raise HTTPException(status_code=400, detail="Esta canción ya existe en la playlist")

    # Obtener información completa de Spotify
    try:
        import requests

        if not Settings.SPOTIFY_TOKEN:
            SpotifyService.obtener_token()

        headers = {'Authorization': f'Bearer {Settings.SPOTIFY_TOKEN}'}
        url = f'https://api.spotify.com/v1/tracks/{data.spotify_id}'

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="No se pudo obtener información de Spotify")

        track_data = response.json()

        titulo = track_data.get('name', 'Sin título')
        artista = track_data['artists'][0]['name'] if track_data.get('artists') else 'Artista desconocido'
        spotify_url = track_data.get('external_urls', {}).get('spotify', '')

        # Usar año manual si se proporcionó, si no el de Spotify
        anio_final = data.anio
        if anio_final is None and 'album' in track_data and 'release_date' in track_data['album']:
            try:
                anio_final = int(track_data['album']['release_date'][:4])
            except (ValueError, IndexError):
                pass

        # Guardar en la base de datos
        cancion_crud.create(
            db,
            titulo=titulo,
            artista=artista,
            anio=anio_final,
            spotify_id=data.spotify_id,
            spotify_url=spotify_url,
            playlist_key=data.playlist_key
        )

        logger.info(f"Canción añadida: {titulo} - {artista} a {data.playlist_key}")

        return {
            'success': True,
            'mensaje': 'Canción añadida correctamente',
            'cancion': {
                'titulo': titulo,
                'artista': artista,
                'anio': anio_final
            }
        }

    except Exception as e:
        logger.error(f"Error añadiendo canción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al añadir la canción: {str(e)}")