from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from ..config.database import get_db
from ..schemas.game import VerificarRespuestaRequest
from ..services.game_service import GameService
from ..config.settings import settings

router = APIRouter(tags=["game"])


@router.get("/playlists")
def get_playlists():
    """Devuelve las playlists disponibles"""
    playlists = [{'key': k, 'name': k} for k in settings.PLAYLISTS.keys()]
    return {'playlists': playlists}


@router.get("/cancion/{playlist_key}")
def get_cancion(playlist_key: str, db: Session = Depends(get_db)):
    """Obtiene una canción aleatoria"""
    resultado = GameService.obtener_cancion_para_adivinar(db, playlist_key)

    if not resultado:
        raise HTTPException(status_code=404, detail='No se pudo obtener canción')

    return resultado


@router.post("/verificar/{playlist_key}")
def verificar_respuesta(playlist_key: str, data: VerificarRespuestaRequest):
    """Verifica la respuesta del usuario"""
    resultado = GameService.verificar_respuesta(
        playlist_key,
        data.titulo,
        data.artista
    )

    if 'error' in resultado:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return resultado


@router.get("/rendirse/{playlist_key}")
def rendirse(playlist_key: str):
    """El usuario se rinde"""
    resultado = GameService.rendirse(playlist_key)

    if 'error' in resultado:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return resultado


@router.get("/sync/{playlist_key}")
def sync_playlist(playlist_key: str, db: Session = Depends(get_db)):
    """Sincroniza una playlist"""
    resultado = GameService.sincronizar_playlist(db, playlist_key)

    if resultado:
        return {
            'message': f'Playlist {playlist_key} sincronizada correctamente',
            'status': 'success'
        }
    else:
        raise HTTPException(status_code=500, detail=f'Error sincronizando playlist {playlist_key}')


@router.get("/sync-all")
def sync_all_playlists(db: Session = Depends(get_db)):
    """Sincroniza todas las playlists"""
    results = {}
    for key in settings.PLAYLISTS.keys():
        ok = GameService.sincronizar_playlist(db, key)
        results[key] = ok

    success_count = sum(1 for success in results.values() if success)
    total = len(results)

    return {
        'message': f'Sincronización completada. {success_count}/{total} playlists sincronizadas',
        'results': results,
        'status': 'success' if success_count == total else 'partial'
    }