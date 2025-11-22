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

    # Email (para enviar códigos de registro, notificaciones)

    EMAIL_API: str = ""

    # Calendly
    CALENDLY_API_KEY: str = ""
    CALENDLY_USER_URI: str = ""
    CALENDLY_EVENT_URL: str = ""

    # AÑADE ESTOS CAMPOS QUE FALTAN:
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    SPOTIFY_REFRESH_TOKEN: str = ""
    OPENAI_API_KEY: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        case_sensitive = True
        extra = "allow"


settings = Settings()