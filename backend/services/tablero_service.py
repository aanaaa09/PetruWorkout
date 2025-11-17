from sqlalchemy.orm import Session
from ..models.juego_tablero import PartidaTablero, LineaTiempoJugador
from ..crud.cancion import cancion_crud
from ..crud.usuario import usuario_crud
from ..crud.sesion import sesion_crud
from ..utils.fuzzy_match import (
    verificar_respuesta_solo_titulo,
    verificar_respuesta_solo_artista
)
from ..utils.qr_generator import generar_qr_base64
from datetime import datetime
from sortedcontainers import SortedDict
import random
import logging

logger = logging.getLogger(__name__)


class TableroService:
    """Servicio para gestionar la lógica del modo tablero"""

    @staticmethod
    def crear_partida(db: Session, playlist_key: str, configuracion: dict) -> PartidaTablero:
        """Crea una nueva partida de tablero"""
        tipo_juego = configuracion['tipo_juego']

        # Validar y procesar jugadores
        if tipo_juego == 'individual':
            jugadores = configuracion.get('jugadores_individuales', [])
            if len(jugadores) > 4 or len(jugadores) < 1:
                raise ValueError("Debe haber entre 1 y 4 jugadores")

            # Validar cada jugador
            for jugador in jugadores:
                # ✅ Validar que el tipo sea válido
                if jugador['tipo'] not in ['registrado', 'invitado']:
                    raise ValueError(f"Tipo de jugador inválido: {jugador['tipo']}. Debe ser 'registrado' o 'invitado'")

                if jugador['tipo'] == 'registrado':
                    if not jugador.get('token'):
                        raise ValueError(f"Token requerido para jugador registrado: {jugador['nombre']}")

                    sesion = sesion_crud.validate_token(db, jugador['token'])
                    if not sesion:
                        raise ValueError(f"Sesión inválida para: {jugador['nombre']}")

                    usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
                    if not usuario:
                        raise ValueError(f"Usuario no encontrado: {jugador['nombre']}")

                    jugador['usuario_id'] = usuario.id
                    jugador['nombre'] = usuario.nombre
                    jugador['email'] = usuario.email
                    jugador['puntos'] = usuario.puntos

                elif jugador['tipo'] == 'invitado':
                    # ✅ Para invitados, solo validar que tengan nombre
                    if not jugador.get('nombre') or len(jugador['nombre'].strip()) < 2:
                        raise ValueError("Los jugadores invitados deben tener un nombre válido (mínimo 2 caracteres)")

        else:  # parejas
            parejas = configuracion.get('parejas', [])
            if len(parejas) > 3 or len(parejas) < 1:
                raise ValueError("Debe haber entre 1 y 3 parejas")

            for pareja in parejas:
                if not pareja.get('nombre_pareja'):
                    raise ValueError("Cada pareja debe tener un nombre")

                # ✅ Validar miembro 1
                m1 = pareja['miembro1']
                if m1['tipo'] not in ['registrado', 'invitado']:
                    raise ValueError(f"Tipo inválido para {m1['nombre']}: debe ser 'registrado' o 'invitado'")

                if m1['tipo'] == 'registrado':
                    if not m1.get('token'):
                        raise ValueError(f"Token requerido para: {m1['nombre']}")

                    sesion = sesion_crud.validate_token(db, m1['token'])
                    if not sesion:
                        raise ValueError(f"Sesión inválida para: {m1['nombre']}")

                    usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
                    if not usuario:
                        raise ValueError(f"Usuario no encontrado: {m1['nombre']}")

                    m1['usuario_id'] = usuario.id
                    m1['nombre'] = usuario.nombre
                    m1['email'] = usuario.email

                elif m1['tipo'] == 'invitado':
                    if not m1.get('nombre') or len(m1['nombre'].strip()) < 2:
                        raise ValueError("Los miembros invitados deben tener un nombre válido")

                # ✅ Validar miembro 2
                m2 = pareja['miembro2']
                if m2['tipo'] not in ['registrado', 'invitado']:
                    raise ValueError(f"Tipo inválido para {m2['nombre']}: debe ser 'registrado' o 'invitado'")

                if m2['tipo'] == 'registrado':
                    if not m2.get('token'):
                        raise ValueError(f"Token requerido para: {m2['nombre']}")

                    sesion = sesion_crud.validate_token(db, m2['token'])
                    if not sesion:
                        raise ValueError(f"Sesión inválida para: {m2['nombre']}")

                    usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
                    if not usuario:
                        raise ValueError(f"Usuario no encontrado: {m2['nombre']}")

                    m2['usuario_id'] = usuario.id
                    m2['nombre'] = usuario.nombre
                    m2['email'] = usuario.email

                elif m2['tipo'] == 'invitado':
                    if not m2.get('nombre') or len(m2['nombre'].strip()) < 2:
                        raise ValueError("Los miembros invitados deben tener un nombre válido")

        # Crear partida
        partida = PartidaTablero(
            playlist_key=playlist_key,
            tipo_juego=tipo_juego,
            jugadores=configuracion,
            turno_actual=0,
            estado='activa',
            canciones_servidas=[]  # ✅ Inicializar vacío
        )

        db.add(partida)
        db.commit()
        db.refresh(partida)

        # Crear líneas de tiempo vacías
        num_jugadores = (
            len(jugadores) if tipo_juego == 'individual'
            else len(parejas)
        )

        for i in range(num_jugadores):
            linea_tiempo = LineaTiempoJugador(
                partida_id=partida.id,
                jugador_index=i,
                canciones_por_anio={},
                puntos_actuales=0,
                completado_10=False,
                karaoke_realizado=False,
                puntos_karaoke=0
            )
            db.add(linea_tiempo)

        db.commit()

        logger.info(f"Partida creada: ID={partida.id}, Tipo={tipo_juego}, Jugadores: {num_jugadores}")
        return partida

    @staticmethod
    def obtener_cancion_turno(db: Session, partida_id: int):
        """Obtiene canción para el turno actual"""
        partida = db.query(PartidaTablero).filter(
            PartidaTablero.id == partida_id
        ).first()

        if not partida:
            return {'error': 'Partida no encontrada'}

        if partida.estado == 'finalizada':
            return {'error': 'La partida ha finalizado'}

        # Obtener canciones
        canciones = cancion_crud.get_all_by_playlist(db, partida.playlist_key)
        if not canciones:
            return {'error': 'No hay canciones disponibles'}

        # Inicializar canciones_servidas si no existe
        if not partida.canciones_servidas:
            partida.canciones_servidas = []

        # ✅ NUEVO: Obtener años ya usados por este jugador
        linea_tiempo = db.query(LineaTiempoJugador).filter(
            LineaTiempoJugador.partida_id == partida_id,
            LineaTiempoJugador.jugador_index == partida.turno_actual
        ).first()

        anios_usados_jugador = set()
        if linea_tiempo and linea_tiempo.canciones_por_anio:
            # Extraer años del SortedDict
            anios_usados_jugador = {
                int(info['anio'])
                for info in linea_tiempo.canciones_por_anio.values()
            }

        # ✅ FILTRAR: canciones con año que:
        # 1. No hayan sido servidas en toda la partida (compartido)
        # 2. El año NO esté ya usado por este jugador
        disponibles = [
            c for c in canciones
            if c.anio is not None
               and c.id not in partida.canciones_servidas
               and c.anio not in anios_usados_jugador  # ✅ Nueva condición
        ]

        # ✅ Si NO quedan canciones disponibles para este jugador
        if not disponibles:
            logger.info(f"🔄 No quedan canciones con años únicos para jugador {partida.turno_actual}")

            # Opción A: Resetear solo para este jugador
            # (permitir canciones con años repetidos pero no servidas aún)
            disponibles = [
                c for c in canciones
                if c.anio is not None
                   and c.id not in partida.canciones_servidas
            ]

            # Si aún así no hay disponibles, resetear las servidas
            if not disponibles:
                logger.info(f"🔄 Reseteando canciones servidas en partida {partida_id}")
                partida.canciones_servidas = []
                disponibles = [c for c in canciones if c.anio is not None]

        if not disponibles:
            return {'error': 'No hay canciones con año'}

        # ✅ Intentar hasta 5 canciones para encontrar preview
        max_intentos = 5
        intentos = 0
        preview_url = None
        cancion_seleccionada = None

        from ..services.itunes_service import ITunesService

        while intentos < max_intentos and not preview_url:
            # Seleccionar canción aleatoria
            cancion = random.choice(disponibles)

            # Buscar preview
            preview_url = ITunesService.buscar_preview(cancion.titulo, cancion.artista)

            if preview_url:
                cancion_seleccionada = cancion
                logger.info(f"✅ Preview encontrado para: {cancion.titulo} - {cancion.artista} ({cancion.anio})")
            else:
                logger.warning(
                    f"⚠️ No se encontró preview para: {cancion.titulo} - {cancion.artista}, intentando otra..."
                )
                # Marcar como servida para no repetirla
                partida.canciones_servidas.append(cancion.id)
                # Remover de disponibles
                disponibles = [c for c in disponibles if c.id != cancion.id]

                if not disponibles:
                    # Resetear y volver a intentar
                    partida.canciones_servidas = []
                    disponibles = [
                        c for c in canciones
                        if c.anio is not None
                           and c.anio not in anios_usados_jugador  # ✅ Mantener filtro de años
                    ]

            intentos += 1

        if not preview_url or not cancion_seleccionada:
            return {'error': 'No se encontró ninguna canción con preview disponible'}

        # Guardar la canción actual en la partida
        partida.cancion_actual = {
            'id': cancion_seleccionada.id,
            'titulo': cancion_seleccionada.titulo,
            'artista': cancion_seleccionada.artista,
            'anio': cancion_seleccionada.anio,
            'spotify_id': cancion_seleccionada.spotify_id,
            'spotify_url': cancion_seleccionada.spotify_url or f"https://open.spotify.com/track/{cancion_seleccionada.spotify_id}"
        }

        # Marcar como servida en la partida (para TODOS los jugadores)
        if cancion_seleccionada.id not in partida.canciones_servidas:
            partida.canciones_servidas.append(cancion_seleccionada.id)

        db.commit()

        return {
            'preview_url': preview_url,
            'turno_actual': partida.turno_actual,
            'jugador_info': TableroService._obtener_info_jugador_actual(partida),
            'canciones_servidas': len(partida.canciones_servidas),
            'canciones_totales': len(canciones),
            'anios_usados_jugador': len(anios_usados_jugador)  # ✅ Info adicional
        }

    @staticmethod
    def crear_casilla(db: Session, partida_id: int, jugador_index: int, posicion: int):
        """
        Prepara para crear una nueva casilla en la línea de tiempo
        En realidad las casillas se crean automáticamente al insertar canciones
        """
        linea_tiempo = db.query(LineaTiempoJugador).filter(
            LineaTiempoJugador.partida_id == partida_id,
            LineaTiempoJugador.jugador_index == jugador_index
        ).first()

        if not linea_tiempo:
            return {'error': 'Línea de tiempo no encontrada'}

        canciones_actuales = SortedDict(linea_tiempo.canciones_por_anio or {})
        num_casillas = len(canciones_actuales)

        return {
            'success': True,
            'num_casillas': num_casillas,
            'mensaje': f'Tienes {num_casillas} canciones. Puedes añadir en cualquier posición.'
        }

    @staticmethod
    def colocar_cancion(
            db: Session,
            partida_id: int,
            jugador_index: int,
            posicion: int,
            titulo_usuario: str,
            artista_usuario: str
    ):
        """
        Coloca una canción en la línea de tiempo y valida
        posicion: índice donde se quiere colocar (0=primero, 1=segundo, etc.)
        """
        partida = db.query(PartidaTablero).filter(
            PartidaTablero.id == partida_id
        ).first()

        if not partida:
            return {'error': 'Partida no encontrada'}

        if not partida.cancion_actual:
            return {'error': 'No hay canción actual'}

        cancion = partida.cancion_actual

        linea_tiempo = db.query(LineaTiempoJugador).filter(
            LineaTiempoJugador.partida_id == partida_id,
            LineaTiempoJugador.jugador_index == jugador_index
        ).first()

        if not linea_tiempo:
            return {'error': 'Línea de tiempo no encontrada'}

        # Detectar si es validación solo de año
        solo_anio = not titulo_usuario.strip() and not artista_usuario.strip()

        # Validar título y artista solo si se proporcionaron
        titulo_correcto = False
        artista_correcto = False

        if not solo_anio:
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

            logger.info(
                f"Validación - Título: {resultado_titulo['similitud']}% | Artista: {resultado_artista['similitud']}%"
            )

        # Cargar SortedDict actual
        canciones_dict = SortedDict(linea_tiempo.canciones_por_anio or {})
        anios_actuales = list(canciones_dict.keys())
        anio_cancion = str(cancion['anio'])

        # ✅ VALIDACIÓN EXTRA: Verificar que el año no exista ya
        if anio_cancion in canciones_dict:
            return {
                'error': f"Ya tienes una canción del año {anio_cancion} en tu línea de tiempo",
                'correcto_anio': False,
                'puntos_ganados': 0,
                'titulo_real': cancion['titulo'],
                'artista_real': cancion['artista'],
                'anio_real': cancion['anio']
            }

        # Verificar si la posición es correcta
        anio_correcto = TableroService._verificar_posicion_correcta(
            anios_actuales,
            posicion,
            int(anio_cancion)
        )

        # Calcular puntos
        puntos_ganados = 0

        if anio_correcto:
            puntos_ganados += 1  # 1 punto por año correcto

            # Añadir a la línea de tiempo (año como string)
            canciones_dict[anio_cancion] = {
                'titulo': cancion['titulo'],
                'artista': cancion['artista'],
                'anio': cancion['anio'],
                'spotify_id': cancion['spotify_id'],
                'spotify_url': cancion['spotify_url']
            }

        # Solo sumar puntos de título/artista si NO es validación solo de año
        if not solo_anio and titulo_correcto and artista_correcto:
            puntos_ganados += 5  # 5 puntos por título y artista

        # Actualizar línea de tiempo
        linea_tiempo.canciones_por_anio = dict(canciones_dict)
        linea_tiempo.puntos_actuales += puntos_ganados

        # Verificar si completó 10 canciones
        if len(canciones_dict) >= 10 and not linea_tiempo.completado_10:
            linea_tiempo.completado_10 = True

        db.commit()

        # Generar QR
        qr_code = generar_qr_base64(cancion['spotify_url'])

        # Convertir SortedDict a lista ordenada para el response
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
        canciones_ordenadas.reverse()

        return {
            'correcto_anio': anio_correcto,
            'correcto_titulo': titulo_correcto if not solo_anio else False,
            'correcto_artista': artista_correcto if not solo_anio else False,
            'similitud_titulo': resultado_titulo['similitud'] if not solo_anio else 0,
            'similitud_artista': resultado_artista['similitud'] if not solo_anio else 0,
            'puntos_ganados': puntos_ganados,
            'puntos_totales': linea_tiempo.puntos_actuales,
            'canciones_ordenadas': canciones_ordenadas,
            'completado_10': linea_tiempo.completado_10,
            'necesita_karaoke': linea_tiempo.completado_10 and not linea_tiempo.karaoke_realizado,
            'titulo_real': cancion['titulo'],
            'artista_real': cancion['artista'],
            'anio_real': cancion['anio'],
            'qr_code': qr_code,
            'spotify_url': cancion['spotify_url'],
            'solo_anio': solo_anio
        }

    @staticmethod
    def _verificar_posicion_correcta(anios_actuales: list, posicion: int, anio_nuevo: int) -> bool:
        """
        Verifica si el año se colocaría en la posición correcta
        anios_actuales: lista de años (strings) ya colocados, ordenados ASCENDENTEMENTE
        posicion: índice donde el usuario quiere colocar (0, 1, 2, ...)
        anio_nuevo: año de la nueva canción (int)
        """
        if not anios_actuales:
            return True

        # Convertir años a enteros
        anios_int = [int(a) for a in anios_actuales]

        # Verificar límites de posición
        if posicion < 0 or posicion > len(anios_int):
            return False

        # Si se inserta al principio (posición 0)
        # Debe ser MENOR O IGUAL que el primer año (más antiguo)
        if posicion == 0:
            return anio_nuevo <= anios_int[0]

        # Si se inserta al final
        # Debe ser MAYOR O IGUAL que el último año (más reciente)
        if posicion == len(anios_int):
            return anio_nuevo >= anios_int[-1]

        # Si se inserta en medio
        # Debe estar ENTRE el año anterior y el siguiente
        return anios_int[posicion - 1] <= anio_nuevo <= anios_int[posicion]

    @staticmethod
    def procesar_karaoke(db: Session, partida_id: int, jugador_index: int, puntos_karaoke: int):
        """
        Procesa el resultado del karaoke
        puntos_karaoke: entre 0 y 20
        """
        if puntos_karaoke < 0 or puntos_karaoke > 20:
            return {'error': 'Los puntos del karaoke deben estar entre 0 y 20'}

        linea_tiempo = db.query(LineaTiempoJugador).filter(
            LineaTiempoJugador.partida_id == partida_id,
            LineaTiempoJugador.jugador_index == jugador_index
        ).first()

        if not linea_tiempo:
            return {'error': 'Línea de tiempo no encontrada'}

        if linea_tiempo.karaoke_realizado:
            return {'error': 'El karaoke ya fue realizado'}

        if not linea_tiempo.completado_10:
            return {'error': 'Debes completar 10 canciones primero'}

        # Añadir puntos del karaoke
        linea_tiempo.puntos_karaoke = puntos_karaoke
        linea_tiempo.puntos_actuales += puntos_karaoke
        linea_tiempo.karaoke_realizado = True

        db.commit()

        return {
            'success': True,
            'puntos_karaoke': puntos_karaoke,
            'puntos_totales': linea_tiempo.puntos_actuales,
            'mensaje': f'¡Karaoke completado! +{puntos_karaoke} puntos'
        }

    @staticmethod
    def avanzar_turno(db: Session, partida_id: int):
        """Avanza al siguiente turno"""
        partida = db.query(PartidaTablero).filter(
            PartidaTablero.id == partida_id
        ).first()

        if not partida:
            return {'error': 'Partida no encontrada'}

        configuracion = partida.jugadores
        num_jugadores = (
            len(configuracion.get('jugadores_individuales', []))
            if partida.tipo_juego == 'individual'
            else len(configuracion.get('parejas', []))
        )

        partida.turno_actual = (partida.turno_actual + 1) % num_jugadores
        partida.cancion_actual = None

        db.commit()

        return {
            'turno_actual': partida.turno_actual,
            'jugador_turno': TableroService._obtener_info_jugador_actual(partida)
        }

    @staticmethod
    def obtener_estado_partida(db: Session, partida_id: int):
        """Obtiene el estado completo de la partida"""
        partida = db.query(PartidaTablero).filter(
            PartidaTablero.id == partida_id
        ).first()

        if not partida:
            return {'error': 'Partida no encontrada'}

        # Obtener líneas de tiempo de todos
        lineas_tiempo = db.query(LineaTiempoJugador).filter(
            LineaTiempoJugador.partida_id == partida_id
        ).all()

        jugadores_info = []
        for lt in lineas_tiempo:
            canciones_dict = SortedDict(lt.canciones_por_anio or {})
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

            jugadores_info.append({
                'jugador_index': lt.jugador_index,
                'puntos': lt.puntos_actuales,
                'canciones_ordenadas': canciones_ordenadas,
                'completado_10': lt.completado_10,
                'karaoke_realizado': lt.karaoke_realizado,
                'puntos_karaoke': lt.puntos_karaoke,
                'necesita_karaoke': lt.completado_10 and not lt.karaoke_realizado
            })

        return {
            'partida_id': partida.id,
            'tipo_juego': partida.tipo_juego,
            'estado': partida.estado,
            'turno_actual': partida.turno_actual,
            'jugadores': jugadores_info,
            'configuracion': partida.jugadores
        }

    @staticmethod
    def obtener_ganador(db: Session, partida_id: int):
        """Determina el ganador de la partida"""
        partida = db.query(PartidaTablero).filter(
            PartidaTablero.id == partida_id
        ).first()

        if not partida:
            return {'error': 'Partida no encontrada'}

        # Obtener todas las líneas de tiempo
        lineas_tiempo = db.query(LineaTiempoJugador).filter(
            LineaTiempoJugador.partida_id == partida_id
        ).order_by(LineaTiempoJugador.puntos_actuales.desc()).all()

        if not lineas_tiempo:
            return {'error': 'No hay jugadores'}

        ganador_linea = lineas_tiempo[0]
        configuracion = partida.jugadores

        # Obtener info del ganador
        if partida.tipo_juego == 'individual':
            jugador = configuracion['jugadores_individuales'][ganador_linea.jugador_index]
            ganador_info = {
                'tipo': 'individual',
                'nombre': jugador['nombre'],
                'puntos': ganador_linea.puntos_actuales,
                'es_registrado': jugador['tipo'] == 'registrado',
                'usuario_id': jugador.get('usuario_id')
            }
        else:
            pareja = configuracion['parejas'][ganador_linea.jugador_index]
            ganador_info = {
                'tipo': 'pareja',
                'nombre_pareja': pareja['nombre_pareja'],
                'miembro1': pareja['miembro1']['nombre'],
                'miembro2': pareja['miembro2']['nombre'],
                'puntos': ganador_linea.puntos_actuales,
                'miembros_registrados': [
                    m for m in [pareja['miembro1'], pareja['miembro2']]
                    if m['tipo'] == 'registrado'
                ]
            }

        return {
            'ganador': ganador_info,
            'ranking': [
                {
                    'jugador_index': lt.jugador_index,
                    'puntos': lt.puntos_actuales
                }
                for lt in lineas_tiempo
            ]
        }

    @staticmethod
    def finalizar_partida(db: Session, partida_id: int):
        """Finaliza la partida y suma puntos a usuarios registrados"""
        partida = db.query(PartidaTablero).filter(
            PartidaTablero.id == partida_id
        ).first()

        if not partida:
            return {'error': 'Partida no encontrada'}

        if partida.estado == 'finalizada':
            return {'error': 'La partida ya estaba finalizada'}

        # Obtener todas las líneas de tiempo
        lineas_tiempo = db.query(LineaTiempoJugador).filter(
            LineaTiempoJugador.partida_id == partida_id
        ).all()

        configuracion = partida.jugadores

        # Sumar puntos a usuarios registrados
        if partida.tipo_juego == 'individual':
            for lt in lineas_tiempo:
                jugador = configuracion['jugadores_individuales'][lt.jugador_index]
                if jugador['tipo'] == 'registrado' and jugador.get('usuario_id'):
                    usuario_crud.add_points(db, jugador['usuario_id'], lt.puntos_actuales)
        else:
            for lt in lineas_tiempo:
                pareja = configuracion['parejas'][lt.jugador_index]
                # Sumar puntos a cada miembro registrado
                for miembro in [pareja['miembro1'], pareja['miembro2']]:
                    if miembro['tipo'] == 'registrado' and miembro.get('usuario_id'):
                        usuario_crud.add_points(db, miembro['usuario_id'], lt.puntos_actuales)

        # Marcar partida como finalizada
        partida.estado = 'finalizada'
        partida.fecha_fin = datetime.now()
        db.commit()

        return {
            'success': True,
            'mensaje': 'Partida finalizada y puntos sumados'
        }

    @staticmethod
    def reiniciar_partida(db: Session, partida_id: int, mismos_jugadores: bool, token_principal: str):
        """
        Reinicia la partida
        Si mismos_jugadores=True, mantiene la configuración
        Si mismos_jugadores=False, permite reconfigurar y cierra sesiones
        """
        partida = db.query(PartidaTablero).filter(
            PartidaTablero.id == partida_id
        ).first()

        if not partida:
            return {'error': 'Partida no encontrada'}

        if mismos_jugadores:
            # Crear nueva partida con misma configuración
            nueva_partida = TableroService.crear_partida(
                db,
                partida.playlist_key,
                partida.jugadores
            )

            return {
                'success': True,
                'partida_id': nueva_partida.id,
                'mensaje': 'Partida reiniciada con los mismos jugadores'
            }
        else:
            # Cerrar sesiones de todos menos del usuario principal
            configuracion = partida.jugadores

            if partida.tipo_juego == 'individual':
                for jugador in configuracion['jugadores_individuales']:
                    if jugador['tipo'] == 'registrado' and jugador.get('token'):
                        if jugador['token'] != token_principal:
                            sesion_crud.delete_by_token(db, jugador['token'])
            else:
                for pareja in configuracion['parejas']:
                    for miembro in [pareja['miembro1'], pareja['miembro2']]:
                        if miembro['tipo'] == 'registrado' and miembro.get('token'):
                            if miembro['token'] != token_principal:
                                sesion_crud.delete_by_token(db, miembro['token'])

            return {
                'success': True,
                'mensaje': 'Sesiones cerradas. Puedes configurar nuevos jugadores'
            }

    @staticmethod
    def _obtener_info_jugador_actual(partida: PartidaTablero):
        """Obtiene info del jugador/pareja en turno"""
        configuracion = partida.jugadores
        turno = partida.turno_actual

        if partida.tipo_juego == 'individual':
            jugadores = configuracion.get('jugadores_individuales', [])
            if turno < len(jugadores):
                jugador = jugadores[turno]
                return {
                    'tipo': 'individual',
                    'nombre': jugador['nombre'],
                    'puntos': jugador.get('puntos', 0),
                    'es_registrado': jugador['tipo'] == 'registrado'
                }
        else:
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