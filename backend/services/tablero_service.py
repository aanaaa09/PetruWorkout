from sqlalchemy.orm import Session
from ..models.juego_tablero import PartidaTablero, TreeMapJugador
from ..crud.cancion import cancion_crud
from ..crud.usuario import usuario_crud
from ..crud.sesion import sesion_crud
from ..utils.fuzzy_match import verificar_respuesta_solo_titulo, verificar_respuesta_solo_artista
from ..utils.qr_generator import generar_qr_base64
from datetime import datetime
from sortedcontainers import SortedList
import random
import logging

logger = logging.getLogger(__name__)


class TableroService:
    """Servicio para gestionar la lógica del modo tablero"""

    @staticmethod
    def crear_partida(db: Session, playlist_key: str, configuracion: dict) -> PartidaTablero:
        """Crea una nueva partida de tablero"""
        tipo_juego = configuracion['tipo_juego']

        # Validar y procesar jugadores según el tipo
        if tipo_juego == 'individual':
            jugadores = configuracion.get('jugadores_individuales', [])
            if len(jugadores) > 4 or len(jugadores) < 1:
                raise ValueError("Debe haber entre 1 y 4 jugadores")

            # Validar y cargar datos de jugadores registrados
            for jugador in jugadores:
                if jugador['tipo'] == 'registrado':
                    if not jugador.get('token'):
                        raise ValueError(f"Token requerido para jugador registrado: {jugador['nombre']}")

                    # Validar sesión y cargar datos del usuario
                    sesion = sesion_crud.validate_token(db, jugador['token'])
                    if not sesion:
                        raise ValueError(f"Sesión inválida para jugador: {jugador['nombre']}")

                    usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
                    if not usuario:
                        raise ValueError(f"Usuario no encontrado: {jugador['nombre']}")

                    # Actualizar datos del jugador con info de BD
                    jugador['usuario_id'] = usuario.id
                    jugador['nombre'] = usuario.nombre
                    jugador['email'] = usuario.email
                    jugador['puntos'] = usuario.puntos

        else:  # parejas
            parejas = configuracion.get('parejas', [])
            if len(parejas) > 3 or len(parejas) < 1:
                raise ValueError("Debe haber entre 1 y 3 parejas")

            # Validar y cargar datos de cada miembro de pareja
            for pareja in parejas:
                # Procesar miembro 1
                miembro1 = pareja['miembro1']
                if miembro1['tipo'] == 'registrado':
                    if not miembro1.get('token'):
                        raise ValueError(f"Token requerido para {miembro1['nombre']}")

                    sesion = sesion_crud.validate_token(db, miembro1['token'])
                    if not sesion:
                        raise ValueError(f"Sesión inválida para {miembro1['nombre']}")

                    usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
                    if not usuario:
                        raise ValueError(f"Usuario no encontrado: {miembro1['nombre']}")

                    miembro1['usuario_id'] = usuario.id
                    miembro1['nombre'] = usuario.nombre
                    miembro1['email'] = usuario.email

                # Procesar miembro 2
                miembro2 = pareja['miembro2']
                if miembro2['tipo'] == 'registrado':
                    if not miembro2.get('token'):
                        raise ValueError(f"Token requerido para {miembro2['nombre']}")

                    sesion = sesion_crud.validate_token(db, miembro2['token'])
                    if not sesion:
                        raise ValueError(f"Sesión inválida para {miembro2['nombre']}")

                    usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
                    if not usuario:
                        raise ValueError(f"Usuario no encontrado: {miembro2['nombre']}")

                    miembro2['usuario_id'] = usuario.id
                    miembro2['nombre'] = usuario.nombre
                    miembro2['email'] = usuario.email

        # Crear partida
        partida = PartidaTablero(
            playlist_key=playlist_key,
            tipo_juego=tipo_juego,
            jugadores=configuracion,
            turno_actual=0,
            estado='activa',
            canciones_servidas=[]
        )

        db.add(partida)
        db.commit()
        db.refresh(partida)

        # Crear TreeMaps para cada jugador/pareja
        if tipo_juego == 'individual':
            num_jugadores = len(jugadores)
        else:
            num_jugadores = len(parejas)

        for i in range(num_jugadores):
            treemap = TreeMapJugador(
                partida_id=partida.id,
                jugador_index=i,
                canciones=[],  # Lista vacía que será ordenada
                puntos_actuales=0,
                completado_10=False,
                karaoke_realizado=False
            )
            db.add(treemap)

        db.commit()

        logger.info(f"Partida tablero creada: ID={partida.id}, Tipo={tipo_juego}, Jugadores={num_jugadores}")
        return partida

    @staticmethod
    def obtener_cancion_turno(db: Session, partida_id: int):
        """Obtiene una canción para el turno actual y la guarda en la partida"""

        partida = db.query(PartidaTablero).filter(PartidaTablero.id == partida_id).first()
        if not partida:
            return {'error': 'Partida no encontrada'}

        # Obtener canciones de la playlist
        canciones = cancion_crud.get_all_by_playlist(db, partida.playlist_key)
        if not canciones:
            return {'error': 'No hay canciones disponibles'}

        # Inicializar canciones servidas si no existe
        if not partida.canciones_servidas:
            partida.canciones_servidas = []

        # Filtrar canciones no servidas y que tengan año
        canciones_disponibles = [
            c for c in canciones
            if c.id not in partida.canciones_servidas and c.anio is not None
        ]

        # Si no quedan, resetear
        if not canciones_disponibles:
            logger.info(f"Reseteando canciones servidas de partida {partida_id}")
            partida.canciones_servidas = []
            canciones_disponibles = [c for c in canciones if c.anio is not None]

        if not canciones_disponibles:
            return {'error': 'No hay canciones con año disponibles'}

        # Seleccionar canción aleatoria
        cancion = random.choice(canciones_disponibles)

        # Obtener preview
        from ..services.itunes_service import ITunesService
        preview_url = ITunesService.buscar_preview(cancion.titulo, cancion.artista)

        if not preview_url:
            return {'error': 'No se encontró preview para esta canción'}

        # Guardar la canción actual en la partida
        partida.cancion_actual = {
            'id': cancion.id,
            'titulo': cancion.titulo,
            'artista': cancion.artista,
            'anio': cancion.anio,
            'spotify_id': cancion.spotify_id,
            'spotify_url': cancion.spotify_url or f"https://open.spotify.com/track/{cancion.spotify_id}"
        }

        # Marcar como servida
        partida.canciones_servidas.append(cancion.id)

        db.commit()

        return {
            'preview_url': preview_url,
            'turno_actual': partida.turno_actual,
            'jugador_info': TableroService._obtener_info_jugador_actual(partida)
        }

    @staticmethod
    def _obtener_info_jugador_actual(partida: PartidaTablero):
        """Obtiene la info del jugador/pareja actual"""

        configuracion = partida.jugadores
        turno = partida.turno_actual

        if partida.tipo_juego == 'individual':
            jugadores = configuracion.get('jugadores_individuales', [])
            if turno < len(jugadores):
                jugador = jugadores[turno]
                return {
                    'tipo': 'individual',
                    'nombre': jugador['nombre'],
                    'puntos': jugador.get('puntos', 0)
                }
        else:  # parejas
            parejas = configuracion.get('parejas', [])
            if turno < len(parejas):
                pareja = parejas[turno]
                return {
                    'tipo': 'pareja',
                    'nombre_pareja': pareja['nombre_pareja'],
                    'miembro1': pareja['miembro1']['nombre'],
                    'miembro2': pareja['miembro2']['nombre']
                }

        return {'error': 'Jugador no encontrado'}



tablero_service = TableroService()