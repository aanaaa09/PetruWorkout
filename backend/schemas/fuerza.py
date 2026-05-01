from pydantic import BaseModel, EmailStr, model_validator
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
    edad: int = 0
    pull:   int = 0
    dips:   int = 0
    push:   int = 0
    squat:  int = 0

    @model_validator(mode='after')
    def at_least_one_exercise(self):
        if self.pull == 0 and self.dips == 0 and self.push == 0 and self.squat == 0:
            raise ValueError('Introduce al menos un ejercicio con valor mayor que 0')
        return self

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