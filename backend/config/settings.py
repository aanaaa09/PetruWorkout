import os
from typing import ClassVar
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de datos PostgreSQL
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # Spotify API
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str

    # Sesiones
    SESSION_DURATION_DAYS: int = 7

    # Fuzzy matching
    FUZZY_MATCH_THRESHOLD: int = 75

    # Juego
    PUNTOS_TITULO: int = 2
    PUNTOS_ARTISTA: int = 2
    PUNTOS_ANIO: int = 4
    PREGUNTAS_POR_RONDA: int = 10
    BONUS_RACHA: int = 1
    RONDAS_ACTIVAS: ClassVar[dict] = {}
    SERVIDAS: ClassVar[dict] = {}
    CANCION_ACTUAL: ClassVar[dict] = {}
    CACHE_ITUNES: ClassVar[dict] = {}

    PLAYLISTS: dict = {
        'juego_clasico': '5ChPyb9z3oH6MWzdkqwh2h',
        'urban_hits': '5BbhkBazvF4Fciu83ifxZu',
        'ochenta_noventa': '2ezIJcEgvaOxF4D4fVV1Q1',
        'flamenco_rumba': '7x6lkSKibepRrx1XhHSP4u',
        'pop_espanol': '5LbZON97B8T7t32c4pfGP3'
    }

    TIPOS_PREGUNTA: list = ['solo_titulo', 'solo_anio', 'solo_artista']

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        case_sensitive = True

settings = Settings()
