from pydantic import BaseModel
from typing import Optional

class VerificarRespuestaRequest(BaseModel):
    titulo: str = ""
    artista: str = ""

class VerificarRespuestaRondaRequest(BaseModel):
    titulo: Optional[str] = None
    artista: Optional[str] = None
    anio: Optional[str] = None