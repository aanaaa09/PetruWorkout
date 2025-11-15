from sqlalchemy.orm import Session
from ..models.juego_tablero import PartidaTablero, TreeMapJugador
from ..crud.cancion import cancion_crud
from ..utils.fuzzy_match import verificar_respuesta_solo_titulo, verificar_respuesta_solo_artista
import random
import logging

logger = logging.getLogger(__name__)


class TableroService:
    """Servicio para gestionar la lógica del modo tablero"""

    @staticmethod
    def crear_partida(db: Session, playlist_key: str, configuracion: dict) -> PartidaTablero:
        """Crea una nueva partida de tablero"""

        # Validar configuración
        tipo_juego = configuracion['tipo_juego']

        if tipo_juego == 'individual':
            jugadores = configuracion.get('jugadores_individuales', [])
            if len(jugadores) > 4 or len(jugadores) < 1:
                raise ValueError("Debe haber entre 1 y 4 jugadores")
        else:  # parejas
            parejas = configuracion.get('parejas', [])
            if len(parejas) > 3 or len(parejas) < 1:
                raise ValueError("Debe haber entre 1 y 3 parejas")
            jugadores = parejas

        # Crear partida
        partida = PartidaTablero(
            playlist_key=playlist_key,
            tipo_juego=tipo_juego,
            jugadores=configuracion,
            turno_actual=0,
            estado='activa'
        )

        db.add(partida)
        db.commit()
        db.refresh(partida)

        # Crear TreeMaps para cada jugador/pareja
        num_jugadores = len(jugadores)
        for i in range(num_jugadores):
            treemap = TreeMapJugador(
                partida_id=partida.id,
                jugador_index=i,
                canciones=[],
                puntos_actuales=0
            )
            db.add(treemap)

        db.commit()

        logger.info(f"Partida tablero creada: ID={partida.id}, Jugadores={num_jugadores}")
        return partida

    @staticmethod
    def obtener_cancion_turno(db: Session, partida_id: int):
        """Obtiene una canción para el turno actual"""

        partida = db.query(PartidaTablero).filter(PartidaTablero.id == partida_id).first()
        if not partida:
            return {'error': 'Partida no encontrada'}

        # Obtener canción aleatoria de la playlist
        canciones = cancion_crud.get_all_by_playlist(db, partida.playlist_key)

        if not canciones:
            return {'error': 'No hay canciones disponibles'}

        # Seleccionar canción aleatoria
        cancion = random.choice(canciones)

        # Obtener preview de iTunes (del servicio existente)
        from ..services.itunes_service import ITunesService
        preview_url = ITunesService.buscar_preview(cancion.titulo, cancion.artista)

        if not preview_url:
            return {'error': 'No se encontró preview para esta canción'}

        return {
            'cancion_id': cancion.id,
            'preview_url': preview_url,
            'spotify_id': cancion.spotify_id,
            'titulo_real': cancion.titulo,
            'artista_real': cancion.artista,
            'anio_real': cancion.anio,
            'spotify_url': cancion.spotify_url if cancion.spotify_url else f"https://open.spotify.com/track/{cancion.spotify_id}"
        }

    @staticmethod
    def colocar_cancion_treemap(
            db: Session,
            partida_id: int,
            jugador_index: int,
            posicion: int,
            titulo_usuario: str,
            artista_usuario: str
    ):
        """Coloca una canción en el TreeMap del jugador y valida"""

        partida = db.query(PartidaTablero).filter(PartidaTablero.id == partida_id).first()
        if not partida:
            return {'error': 'Partida no encontrada'}

        treemap = db.query(TreeMapJugador).filter(
            TreeMapJugador.partida_id == partida_id,
            TreeMapJugador.jugador_index == jugador_index
        ).first()

        if not treemap:
            return {'error': 'TreeMap no encontrado'}

        # Obtener la canción actual del turno (debería estar almacenada temporalmente)
        # Por ahora, asumimos que se pasa la info de la canción
        # En producción, deberías almacenar la canción actual en la partida

        # Validar título y artista
        resultado_titulo = verificar_respuesta_solo_titulo(
            cancion['titulo_real'],
            titulo_usuario
        )
        resultado_artista = verificar_respuesta_solo_artista(
            cancion['artista_real'],
            artista_usuario
        )

        titulo_correcto = resultado_titulo['correcto']
        artista_correcto = resultado_artista['correcto']

        # Calcular puntos
        puntos_ganados = 0

        # Verificar si el año está en la posición correcta
        canciones_actuales = treemap.canciones or []
        anio_correcto = TableroService._verificar_posicion_anio(
            canciones_actuales,
            posicion,
            cancion['anio_real']
        )

        if anio_correcto:
            puntos_ganados += 1

        if titulo_correcto and artista_correcto:
            puntos_ganados += 5

        # Actualizar TreeMap
        if anio_correcto:
            # Insertar canción en la posición
            nueva_cancion = {
                'titulo': cancion['titulo_real'],
                'artista': cancion['artista_real'],
                'anio': cancion['anio_real'],
                'spotify_id': cancion['spotify_id'],
                'spotify_url': cancion['spotify_url']
            }
            canciones_actuales.insert(posicion, nueva_cancion)
            treemap.canciones = canciones_actuales

        treemap.puntos_actuales += puntos_ganados

        # Verificar si completó 10 canciones
        if len(treemap.canciones) >= 10 and not treemap.completado_10:
            treemap.completado_10 = True

        db.commit()

        return {
            'correcto_anio': anio_correcto,
            'correcto_titulo': titulo_correcto,
            'correcto_artista': artista_correcto,
            'puntos_ganados': puntos_ganados,
            'puntos_totales': treemap.puntos_actuales,
            'treemap_actualizado': treemap.canciones,
            'completado_10': treemap.completado_10,
            'anio_real': cancion['anio_real']
        }

    @staticmethod
    def _verificar_posicion_anio(canciones: list, posicion: int, anio: int) -> bool:
        """Verifica si el año está en la posición correcta del TreeMap"""

        if not canciones:
            # Primera canción, siempre es correcta
            return True

        # Verificar que mantiene el orden ascendente
        if posicion > 0:
            # Debe ser mayor o igual al anterior
            if canciones[posicion - 1]['anio'] > anio:
                return False

        if posicion < len(canciones):
            # Debe ser menor o igual al siguiente
            if canciones[posicion]['anio'] < anio:
                return False

        return True

    @staticmethod
    def avanzar_turno(db: Session, partida_id: int):
        """Avanza al siguiente turno"""

        partida = db.query(PartidaTablero).filter(PartidaTablero.id == partida_id).first()
        if not partida:
            return {'error': 'Partida no encontrada'}

        configuracion = partida.jugadores
        num_jugadores = len(
            configuracion.get('jugadores_individuales', [])
            if partida.tipo_juego == 'individual'
            else configuracion.get('parejas', [])
        )

        partida.turno_actual = (partida.turno_actual + 1) % num_jugadores
        db.commit()

        return {'turno_actual': partida.turno_actual}

    @staticmethod
    def obtener_ganador(db: Session, partida_id: int):
        """Determina el ganador de la partida"""

        treemaps = db.query(TreeMapJugador).filter(
            TreeMapJugador.partida_id == partida_id
        ).all()

        if not treemaps:
            return {'error': 'No hay datos de la partida'}

        # Encontrar el jugador con más puntos
        ganador = max(treemaps, key=lambda t: t.puntos_actuales)

        return {
            'jugador_index': ganador.jugador_index,
            'puntos': ganador.puntos_actuales,
            'todos_los_puntos': [
                {'jugador_index': t.jugador_index, 'puntos': t.puntos_actuales}
                for t in treemaps
            ]
        }

    @staticmethod
    def finalizar_partida(db: Session, partida_id: int):
        """Finaliza la partida y actualiza puntos de usuarios registrados"""

        partida = db.query(PartidaTablero).filter(PartidaTablero.id == partida_id).first()
        if not partida:
            return {'error': 'Partida no encontrada'}

        partida.estado = 'finalizada'
        from datetime import datetime
        partida.fecha_fin = datetime.now()

        # Actualizar puntos de usuarios registrados
        treemaps = db.query(TreeMapJugador).filter(
            TreeMapJugador.partida_id == partida_id
        ).all()

        configuracion = partida.jugadores

        from ..crud.usuario import usuario_crud

        for treemap in treemaps:
            idx = treemap.jugador_index

            if partida.tipo_juego == 'individual':
                jugador = configuracion['jugadores_individuales'][idx]
                if jugador.get('usuario_id'):
                    usuario_crud.add_points(db, jugador['usuario_id'], treemap.puntos_actuales)
            else:
                pareja = configuracion['parejas'][idx]
                # Sumar puntos a ambos miembros si están registrados
                if pareja['miembro1'].get('usuario_id'):
                    usuario_crud.add_points(db, pareja['miembro1']['usuario_id'], treemap.puntos_actuales)
                if pareja['miembro2'].get('usuario_id'):
                    usuario_crud.add_points(db, pareja['miembro2']['usuario_id'], treemap.puntos_actuales)

        db.commit()

        return {'mensaje': 'Partida finalizada y puntos actualizados'}


tablero_service = TableroService()