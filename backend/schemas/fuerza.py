# backend/schemas/fuerza.py
from pydantic import BaseModel, EmailStr
from typing import Literal


class FuerzaRequest(BaseModel):
    sexo:  Literal["m", "f"]
    pull:  int = 0
    dips:  int = 0
    push:  int = 0
    squat: int = 0


class FuerzaRegisterRequest(BaseModel):
    nombre: str
    email:  EmailStr
    sexo:   Literal["m", "f"]
    pull:   int = 0
    dips:   int = 0
    push:   int = 0
    squat:  int = 0


class FuerzaScores(BaseModel):
    pull:  int
    dips:  int
    push:  int
    squat: int


class FuerzaBarColors(BaseModel):
    pull:  str
    dips:  str
    push:  str
    squat: str


class FuerzaReps(BaseModel):
    pull:  int
    dips:  int
    push:  int
    squat: int


class FuerzaResult(BaseModel):
    score:      int
    level:      str
    scores:     FuerzaScores
    bar_colors: FuerzaBarColors
    weakest:    str
    weak_label: str
    reps:       FuerzaReps


class FuerzaRegisterResult(FuerzaResult):
    registered: bool
    nuevo:      bool