from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..schemas.game import VerificarRespuestaRondaRequest
from ..services.game_service_rondas import GameServiceRondas
from ..crud.sesion import sesion_crud

router = APIRouter(prefix="/ronda", tags=["rondas"])


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Dependency para obtener usuario actual"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    token = authorization.replace("Bearer ", "")
    sesion = sesion_crud.validate_token(db, token)

    if not sesion:
        raise HTTPException(status_code=401, detail="Sesión no válida")

    return sesion.usuario_id


@router.post("/{playlist_key}/iniciar")
def iniciar_ronda(playlist_key: str, usuario_id: int = Depends(get_current_user)):
    """Inicia una nueva ronda"""
    resultado = GameServiceRondas.iniciar_ronda(playlist_key, usuario_id)

    if resultado:
        return {
            'message': 'Ronda iniciada',
            'total_preguntas': 10,
            'tipos_pregunta': ['solo_titulo', 'solo_anio', 'solo_artista']
        }
    else:
        raise HTTPException(status_code=500, detail='No se pudo iniciar la ronda')


@router.get("/{playlist_key}/cancion")
def obtener_cancion_ronda(playlist_key: str, db: Session = Depends(get_db)):
    """Obtiene una canción para la ronda"""
    resultado = GameServiceRondas.obtener_cancion_ronda(db, playlist_key)

    if not resultado or 'error' in resultado:
        raise HTTPException(status_code=404, detail=resultado.get('error', 'No se pudo obtener canción'))

    return resultado


@router.post("/{playlist_key}/verificar")
def verificar_respuesta_ronda(
        playlist_key: str,
        data: VerificarRespuestaRondaRequest,
        db: Session = Depends(get_db)
):
    """Verifica la respuesta del usuario en la ronda"""
    resultado = GameServiceRondas.verificar_respuesta_ronda(
        db,
        playlist_key,
        data.titulo or '',
        data.artista or '',
        data.anio or ''
    )

    if 'error' in resultado:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return resultado


@router.post("/{playlist_key}/rendirse")
def rendirse_ronda(playlist_key: str, db: Session = Depends(get_db)):
    """El usuario se rinde en la pregunta actual"""
    resultado = GameServiceRondas.rendirse_ronda(db, playlist_key)

    if 'error' in resultado:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return resultado


@router.post("/{playlist_key}/finalizar")
def finalizar_ronda(playlist_key: str, db: Session = Depends(get_db)):
    """Finaliza la ronda actual manualmente"""
    resultado = GameServiceRondas.finalizar_ronda(db, playlist_key)

    if 'error' in resultado:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return resultado


@router.get("/{playlist_key}/estado")
def obtener_estado_ronda(playlist_key: str):
    """Obtiene el estado actual de la ronda"""
    resultado = GameServiceRondas.obtener_estado_ronda(playlist_key)

    if 'error' in resultado:
        raise HTTPException(status_code=404, detail=resultado['error'])

    return resultado
