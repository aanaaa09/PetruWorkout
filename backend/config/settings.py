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

    SESSION_DURATION_DAYS: int = 7
    GITHUB_TOKEN: str = ""
    GITHUB_REPO: str = ""
    GITHUB_BRANCH: str = "main"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"
        GITHUB_TOKEN: str = ""
        GITHUB_REPO: str = ""
        GITHUB_BRANCH: str = "main"


settings = Settings()