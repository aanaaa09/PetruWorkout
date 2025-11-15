from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..schemas.tablero import (
    IniciarPartidaRequest,
    ColocarCancionRequest,
    KaraokeRequest
)
from ..services.tablero_service import tablero_service

router = APIRouter(prefix="/api/tablero", tags=["tablero"])


@router.post("/iniciar")
def iniciar_partida(data: IniciarPartidaRequest, db: Session = Depends(get_db)):
    """Inicia una nueva partida de tablero"""
    try:
        partida = tablero_service.crear_partida(
            db,
            data.playlist_key,
            data.configuracion.dict()
        )

        return {
            'success': True,
            'partida_id': partida.id,
            'mensaje': 'Partida iniciada correctamente'
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar partida: {str(e)}")


@router.get("/{partida_id}/cancion")
def obtener_cancion(partida_id: int, db: Session = Depends(get_db)):
    """Obtiene la canción para el turno actual"""
    resultado = tablero_service.obtener_cancion_turno(db, partida_id)

    if 'error' in resultado:
        raise HTTPException(status_code=404, detail=resultado['error'])

    return resultado


@router.post("/colocar-cancion")
def colocar_cancion(data: ColocarCancionRequest, db: Session = Depends(get_db)):
    """Coloca una canción en el TreeMap y valida"""
    # Necesitamos pasar los datos de la canción actual
    # En una implementación real, estos datos deberían estar almacenados temporalmente
    # Por ahora, los pasamos en el request
    resultado = tablero_service.colocar_cancion_treemap(
        db,
        data.partida_id,
        data.jugador_index,
        data.posicion,
        data.titulo or '',
        data.artista or '',
        {
            'titulo_real': data.titulo_real,
            'artista_real': data.artista_real,
            'anio_real': data.anio_real,
            'spotify_id': data.spotify_id,
            'spotify_url': data.spotify_url
        }
    )

    if 'error' in resultado:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return resultado


@router.post("/{partida_id}/avanzar-turno")
def avanzar_turno(partida_id: int, db: Session = Depends(get_db)):
    """Avanza al siguiente turno"""
    resultado = tablero_service.avanzar_turno(db, partida_id)

    if 'error' in resultado:
        raise HTTPException(status_code=404, detail=resultado['error'])

    return resultado


@router.post("/karaoke")
def procesar_karaoke(data: KaraokeRequest, db: Session = Depends(get_db)):
    """Procesa el resultado del karaoke"""
    resultado = tablero_service.procesar_karaoke(
        db,
        data.partida_id,
        data.jugador_index,
        data.puntos_karaoke
    )

    if 'error' in resultado:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return resultado


@router.get("/{partida_id}/estado")
def obtener_estado(partida_id: int, db: Session = Depends(get_db)):
    """Obtiene el estado actual de la partida"""
    resultado = tablero_service.obtener_estado_partida(db, partida_id)

    if 'error' in resultado:
        raise HTTPException(status_code=404, detail=resultado['error'])

    return resultado


@router.get("/{partida_id}/ganador")
def obtener_ganador(partida_id: int, db: Session = Depends(get_db)):
    """Obtiene el ganador de la partida"""
    resultado = tablero_service.obtener_ganador(db, partida_id)

    if 'error' in resultado:
        raise HTTPException(status_code=404, detail=resultado['error'])

    return resultado


@router.post("/{partida_id}/finalizar")
def finalizar_partida(partida_id: int, db: Session = Depends(get_db)):
    """Finaliza la partida"""
    resultado = tablero_service.finalizar_partida(db, partida_id)

    if 'error' in resultado:
        raise HTTPException(status_code=404, detail=resultado['error'])

    return resultado