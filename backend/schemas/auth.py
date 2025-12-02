# backend/schemas/auth.py
from pydantic import BaseModel, EmailStr

class NewsletterRegistroRequest(BaseModel):
    """Registro solo para newsletter"""
    nombre: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    """Login solo para admin"""
    email: EmailStr
    password: str

class LogoutRequest(BaseModel):
    token: str

class VerificarRequest(BaseModel):
    token: str

class NewsletterUnsubscribeRequest(BaseModel):
    """Cancelar suscripción"""
    email: EmailStr