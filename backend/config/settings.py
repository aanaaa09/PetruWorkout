import os
from typing import ClassVar
from pydantic_settings import BaseSettings


from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import model_validator

class Settings(BaseSettings):
    # Base de datos - pueden venir por separado o como URL completa
    DATABASE_URL: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    EMAIL_API: str = ""

    CALENDLY_API_KEY: str = ""
    CALENDLY_USER_URI: str = ""
    CALENDLY_EVENT_URL: str = ""

    SESSION_DURATION_DAYS: int = 7
    GITHUB_TOKEN: str = ""
    GITHUB_REPO: str = ""
    GITHUB_BRANCH: str = "main"

    @model_validator(mode='after')
    def build_database_url(self):
        if not self.DATABASE_URL and self.DB_HOST:
            # Construye la URL desde las piezas (como antes)
            self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()