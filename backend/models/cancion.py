from sqlalchemy import Column, Integer, String, DateTime, func, Index
from backend.config.database import Base


# Función helper para crear modelos dinámicos de canciones
def crear_modelo_cancion(playlist_key: str):
    """
    Crea dinámicamente un modelo de Cancion para cada playlist
    """
    class_name = f"Cancion_{playlist_key.capitalize()}"
    table_name = f"canciones_{playlist_key}"

    class CancionDinamica(Base):
        __tablename__ = table_name

        id = Column(Integer, primary_key=True, index=True)
        titulo = Column(String(500), nullable=False)
        artista = Column(String(500), nullable=False)
        anio = Column(Integer, nullable=True)
        spotify_id = Column(String(100), unique=True, index=True)
        spotify_url = Column(String(500))
        fecha_agregada = Column(DateTime(timezone=True), server_default=func.now())

        __table_args__ = (
            Index(f'idx_titulo_{playlist_key}', 'titulo'),
            Index(f'idx_artista_{playlist_key}', 'artista'),
            Index(f'unique_song_{playlist_key}', 'titulo', 'artista', unique=True),
        )

    CancionDinamica.__name__ = class_name
    return CancionDinamica


# Diccionario para almacenar los modelos creados
MODELOS_CANCIONES = {}


def get_modelo_cancion(playlist_key: str):
    """
    Obtiene o crea el modelo de Cancion para una playlist
    """
    if playlist_key not in MODELOS_CANCIONES:
        MODELOS_CANCIONES[playlist_key] = crear_modelo_cancion(playlist_key)
    return MODELOS_CANCIONES[playlist_key]