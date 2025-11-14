from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class CancionCRUD:
    """CRUD para canciones (tablas dinámicas)"""

    def _get_table_name(self, playlist_key: str) -> str:
        """Obtiene el nombre de la tabla para una playlist"""
        return f"canciones_{playlist_key}"

    def create(self, db: Session, titulo: str, artista: str, playlist_key: str,
               anio: int = None, spotify_id: str = None, spotify_url: str = None):
        """Crea una canción usando SQL raw"""
        table_name = self._get_table_name(playlist_key)

        query = text(f"""
            INSERT INTO {table_name} (titulo, artista, anio, spotify_id, spotify_url)
            VALUES (:titulo, :artista, :anio, :spotify_id, :spotify_url)
            ON CONFLICT (titulo, artista) DO NOTHING
        """)

        db.execute(query, {
            'titulo': titulo,
            'artista': artista,
            'anio': anio,
            'spotify_id': spotify_id,
            'spotify_url': spotify_url
        })
        db.commit()

        logger.info(f"Canción guardada en {table_name}: {titulo} - {artista}")

    def get_all_by_playlist(self, db: Session, playlist_key: str):
        """Obtiene todas las canciones de una playlist (optimizado)"""
        table_name = self._get_table_name(playlist_key)

        query = text(f"""
            SELECT id, titulo, artista, anio, spotify_id, spotify_url
            FROM {table_name}
            ORDER BY fecha_agregada DESC
        """)

        result = db.execute(query).fetchall()  # ← Más eficiente

        from collections import namedtuple
        Cancion = namedtuple('Cancion', ['id', 'titulo', 'artista', 'anio', 'spotify_id', 'spotify_url'])

        return [Cancion(*row) for row in result]

    def get_spotify_ids(self, db: Session, playlist_key: str) -> set:
        """Obtiene todos los IDs de Spotify de una playlist"""
        table_name = self._get_table_name(playlist_key)

        query = text(f"SELECT spotify_id FROM {table_name}")
        result = db.execute(query)

        return {row[0] for row in result}

    def delete_by_spotify_ids(self, db: Session, playlist_key: str, spotify_ids: list):
        """Elimina canciones por IDs de Spotify"""
        if not spotify_ids:
            return 0

        table_name = self._get_table_name(playlist_key)

        placeholders = ','.join([f':id{i}' for i in range(len(spotify_ids))])
        query = text(f"DELETE FROM {table_name} WHERE spotify_id IN ({placeholders})")

        params = {f'id{i}': sid for i, sid in enumerate(spotify_ids)}

        result = db.execute(query, params)
        db.commit()

        logger.info(f"{result.rowcount} canciones eliminadas de {table_name}")
        return result.rowcount


cancion_crud = CancionCRUD()