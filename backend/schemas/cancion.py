from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CancionBase(BaseModel):
    titulo: str
    artista: str
    anio: Optional[int] = None
    spotify_id: Optional[str] = None
    spotify_url: Optional[str] = None


class CancionCreate(CancionBase):
    pass


class CancionResponse(CancionBase):
    id: int
    fecha_agregada: Optional[datetime] = None

    class Config:
        from_attributes = True