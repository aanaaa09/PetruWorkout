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

        # Obtener la canción actual de la partida
        if not partida.cancion_actual:
            return {'error': 'No hay canción actual'}

        cancion = partida.cancion_actual

        treemap = db.query(TreeMapJugador).filter(
            TreeMapJugador.partida_id == partida_id,
            TreeMapJugador.jugador_index == jugador_index
        ).first()

        if not treemap:
            return {'error': 'TreeMap no encontrado'}

        # Validar título y artista
        resultado_titulo = verificar_respuesta_solo_titulo(
            cancion['titulo'],
            titulo_usuario
        )
        resultado_artista = verificar_respuesta_solo_artista(
            cancion['artista'],
            artista_usuario
        )

        titulo_correcto = resultado_titulo['correcto']
        artista_correcto = resultado_artista['correcto']

        # Calcular puntos
        puntos_ganados = 0

        # Obtener la lista de canciones actual (TreeMap en Python = lista ordenada)
        canciones_actuales = treemap.canciones or []

        # Verificar si el año está en la posición correcta
        anio_correcto = TableroService._verificar_posicion_anio(
            canciones_actuales,
            posicion,
            cancion['anio']
        )

        if anio_correcto:
            puntos_ganados += 1  # 1 punto por año correcto

        if titulo_correcto and artista_correcto:
            puntos_ganados += 5  # 5 puntos por título y artista

        # Actualizar TreeMap solo si el año es correcto
        if anio_correcto:
            nueva_cancion = {
                'titulo': cancion['titulo'],
                'artista': cancion['artista'],
                'anio': cancion['anio'],
                'spotify_id': cancion['spotify_id'],
                'spotify_url': cancion['spotify_url'],
                'correcta': True
            }

            # Insertar en la posición indicada
            canciones_actuales.insert(posicion, nueva_cancion)
            treemap.canciones = canciones_actuales
        else:
            # Si no es correcto, no se añade al TreeMap
            pass

        treemap.puntos_actuales += puntos_ganados

        # Verificar si completó 10 canciones correctas
        if len(treemap.canciones) >= 10 and not treemap.completado_10:
            treemap.completado_10 = True

        db.commit()

        # Generar QR si acertó todo
        qr_code = None
        if titulo_correcto and artista_correcto:
            qr_code = generar_qr_base64(cancion['spotify_url'])

        return {
            'correcto_anio': anio_correcto,
            'correcto_titulo': titulo_correcto,
            'correcto_artista': artista_correcto,
            'puntos_ganados': puntos_ganados,
            'puntos_totales': treemap.puntos_actuales,
            'treemap_actualizado': treemap.canciones,
            'completado_10': treemap.completado_10,
            'necesita_karaoke': treemap.completado_10 and not treemap.karaoke_realizado,
            'titulo_real': cancion['titulo'],
            'artista_real': cancion['artista'],
            'anio_real': cancion['anio'],
            'qr_code': qr_code,
            'spotify_url': cancion['spotify_url'] if (titulo_correcto and artista_correcto) else None
        }

    @staticmethod
    def _verificar_posicion_anio(canciones: list, posicion: int, anio: int) -> bool:
        """
        Verifica si el año está en la posición correcta del TreeMap
        El TreeMap debe estar ordenado ascendentemente por año
        """
        if not canciones:
            # Si está vacío, cualquier posición es válida
            return True

        # Verificar límites de posición
        if posicion < 0 or posicion > len(canciones):
            return False

        # Si se inserta al principio
        if posicion == 0:
            # El año debe ser menor o igual al primer elemento
            return anio <= canciones[0]['anio']

        # Si se inserta al final
        if posicion == len(canciones):
            # El año debe ser mayor o igual al último elemento
            return anio >= canciones[-1]['anio']

        # Si se inserta en medio
        # Debe ser mayor o igual al anterior Y menor o igual al siguiente
        return canciones[posicion - 1]['anio'] <= anio <= canciones[posicion]['anio']

    @staticmethod
    def crear_casilla_treemap(db: Session, partida_id: int, jugador_index: int, posicion: int):
        """
        Crea una nueva casilla vacía en el TreeMap
        (En realidad solo devuelve info, ya que el TreeMap es dinámico)
        """
        treemap = db.query(TreeMapJugador).filter(
            TreeMapJugador.partida_id == partida_id,
            TreeMapJugador.jugador_index == jugador_index
        ).first()

        if not treemap:
            return {'error': 'TreeMap no encontrado'}

        canciones = treemap.canciones or []

        return {
            'success': True,
            'casillas_totales': len(canciones) + 1,
            'mensaje': 'Puedes colocar la canción en esta posición'
        }

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

        # Limpiar canción actual
        partida.cancion_actual = None

        db.commit()

        return {
            'turno_actual': partida.turno_actual,
            'jugador_turno': TableroService._obtener_info_jugador_turno(partida)
        }

    @staticmethod
    def _obtener_info_jugador_turno(partida: PartidaTablero):
        """Obtiene información del jugador en turno"""
        configuracion = partida.jugadores
        turno = partida.turno_actual

        if partida.tipo_juego == 'individual':
            jugador = configuracion['jugadores_individuales'][turno]
            return {
                'tipo': 'individual',
                'nombre': jugador['nombre'],
                'puntos': jugador.get('puntos', 0)
            }
        else:
            pareja = configuracion['parejas'][turno]
            return {
                'tipo': 'pareja',
                'nombre_pareja': pareja['nombre_pareja'],
                'miembro1': pareja['miembro1']['nombre'],
                'miembro2': pareja['miembro2']['nombre']
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