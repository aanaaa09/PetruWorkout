from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..models.juego_tablero import LineaTiempoJugador, PartidaTablero
from ..schemas.tablero import (
    IniciarPartidaRequest,
    ColocarCancionRequest,
    CrearCasillaRequest,
    KaraokeRequest,
    ReiniciarPartidaRequest
)
from ..services.tablero_service import tablero_service, logger

router = APIRouter(prefix="/api/tablero", tags=["tablero"])


def get_token_from_header(authorization: str = Header(None)):
    """Extrae el token del header Authorization"""
    if not authorization:
        return None
    return authorization.replace("Bearer ", "")


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


@router.post("/crear-casilla")
def crear_casilla(data: CrearCasillaRequest, db: Session = Depends(get_db)):
    """Prepara para crear una nueva casilla (informativo)"""
    resultado = tablero_service.crear_casilla(
        db,
        data.partida_id,
        data.jugador_index,
        data.posicion
    )

    if 'error' in resultado:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return resultado


@router.post("/colocar-cancion")
def colocar_cancion(data: ColocarCancionRequest, db: Session = Depends(get_db)):
    """Coloca una canción en la línea de tiempo y valida"""
    resultado = tablero_service.colocar_cancion(
        db,
        data.partida_id,
        data.jugador_index,
        data.posicion,
        data.titulo or '',
        data.artista or ''
    )

    if 'error' in resultado:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return resultado


@router.post("/karaoke")
def procesar_karaoke(data: KaraokeRequest, db: Session = Depends(get_db)):
    """
    Procesa el resultado del karaoke
    Por ahora recibe los puntos directamente (0-20)
    TODO: Implementar evaluación con IA
    """
    # Extraer puntos del request (temporalmente manual)
    # En producción, esto vendría de un servicio de IA que evalúa el audio
    puntos_karaoke = 15  # Placeholder

    resultado = tablero_service.procesar_karaoke(
        db,
        data.partida_id,
        data.jugador_index,
        puntos_karaoke
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
    """Finaliza la partida y suma puntos"""
    resultado = tablero_service.finalizar_partida(db, partida_id)

    if 'error' in resultado:
        raise HTTPException(status_code=404, detail=resultado['error'])

    return resultado


@router.post("/reiniciar")
def reiniciar_partida(
        data: ReiniciarPartidaRequest,
        db: Session = Depends(get_db),
        authorization: str = Header(None)
):
    """Reinicia la partida con o sin los mismos jugadores"""
    token_principal = get_token_from_header(authorization)

    resultado = tablero_service.reiniciar_partida(
        db,
        data.partida_id,
        data.mismos_jugadores,
        token_principal or ''
    )

    if 'error' in resultado:
        raise HTTPException(status_code=404, detail=resultado['error'])

    return resultado


@router.get("/{partida_id}/linea-tiempo/{jugador_index}")
def obtener_linea_tiempo(
        partida_id: int,
        jugador_index: int,
        db: Session = Depends(get_db)
):
    """Obtiene la línea de tiempo de un jugador específico"""
    linea_tiempo = db.query(LineaTiempoJugador).filter(
        LineaTiempoJugador.partida_id == partida_id,
        LineaTiempoJugador.jugador_index == jugador_index
    ).first()

    if not linea_tiempo:
        raise HTTPException(status_code=404, detail="Línea de tiempo no encontrada")

    from sortedcontainers import SortedDict
    canciones_dict = SortedDict(linea_tiempo.canciones_por_anio or {})

    canciones_ordenadas = [
        {
            'anio': int(anio),
            'titulo': info['titulo'],
            'artista': info['artista'],
            'spotify_id': info['spotify_id'],
            'spotify_url': info['spotify_url']
        }
        for anio, info in canciones_dict.items()
    ]

    # ✅ INVERTIR para enviar más recientes primero
    canciones_ordenadas.reverse()

    return {
        'canciones_ordenadas': canciones_ordenadas,
        'puntos': linea_tiempo.puntos_actuales,
        'completado_10': linea_tiempo.completado_10,
        'karaoke_realizado': linea_tiempo.karaoke_realizado,
        'puntos_karaoke': linea_tiempo.puntos_karaoke,
        'necesita_karaoke': linea_tiempo.completado_10 and not linea_tiempo.karaoke_realizado
    }


@router.post("/karaoke")
def procesar_karaoke(data: KaraokeRequest, db: Session = Depends(get_db)):
    """
    Procesa el resultado del karaoke evaluando con IA
    """
    from ..services.karaoke_ia_service import KaraokeIAService

    # Obtener información de la canción actual
    partida = db.query(PartidaTablero).filter(
        PartidaTablero.id == data.partida_id
    ).first()

    if not partida or not partida.cancion_actual:
        return {'error': 'No hay canción activa'}

    cancion = partida.cancion_actual

    # Evaluar karaoke con IA
    logger.info(f"Evaluando karaoke para: {cancion['titulo']} - {cancion['artista']}")

    resultado_ia = KaraokeIAService.evaluar_karaoke(
        audio_base64=data.audio_base64,
        titulo_cancion=cancion['titulo'],
        artista=cancion['artista']
    )

    puntos_karaoke = resultado_ia['puntos']

    # Procesar resultado en el servicio
    resultado = tablero_service.procesar_karaoke(
        db,
        data.partida_id,
        data.jugador_index,
        puntos_karaoke
    )

    if 'error' in resultado:
        raise HTTPException(status_code=400, detail=resultado['error'])

    # Añadir información de la IA
    resultado['evaluacion_ia'] = {
        'transcripcion': resultado_ia.get('transcripcion', ''),
        'desglose': resultado_ia.get('desglose', {}),
        'feedback': resultado_ia.get('feedback', '¡Buen trabajo!')
    }

    return resultado