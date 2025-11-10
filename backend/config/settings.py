from typing import ClassVar

from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    # Base de datos PostgreSQL
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "songbyte_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "realmadrid"

    # Spotify API
    SPOTIFY_CLIENT_ID: str = "51ce072da9c24789ae732edf00428af1"
    SPOTIFY_CLIENT_SECRET: str = "ddaea4e7dfa4428ca0ab97a877117444"

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
    # Playlists de Spotify
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
        env_file = ".env"
        case_sensitive = True


settings = Settings()
