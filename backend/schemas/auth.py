from pydantic import BaseModel, EmailStr

class RegistroRequest(BaseModel):
    nombre: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LogoutRequest(BaseModel):
    token: str

class VerificarRequest(BaseModel):
    token: str

class ActualizarPuntosRequest(BaseModel):
    token: str
    puntos: int