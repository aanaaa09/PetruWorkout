# backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..schemas.auth import (
    NewsletterRegistroRequest,
    LoginRequest,
    LogoutRequest,
    VerificarRequest,
    NewsletterUnsubscribeRequest
)
from ..services.auth_service import AuthService

router = APIRouter(tags=["auth"])


@router.post("/newsletter/registro")
def registro_newsletter(data: NewsletterRegistroRequest, db: Session = Depends(get_db)):
    """Registro para newsletter (sin crear sesión)"""
    resultado = AuthService.registrar_newsletter(db, data.nombre, data.email, data.password)

    if not resultado['success']:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return resultado


@router.post("/newsletter/cancelar")
def cancelar_newsletter(data: NewsletterUnsubscribeRequest, db: Session = Depends(get_db)):
    """Cancelar suscripción a newsletter"""
    resultado = AuthService.cancelar_suscripcion(db, data.email)

    if not resultado['success']:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return resultado


@router.post("/admin/login")
def login_admin(data: LoginRequest, db: Session = Depends(get_db)):
    """Login solo para administrador"""
    resultado = AuthService.login_admin(db, data.email, data.password)

    if not resultado['success']:
        raise HTTPException(status_code=401, detail=resultado['error'])

    return resultado


@router.post("/admin/logout")
def logout_admin(data: LogoutRequest, db: Session = Depends(get_db)):
    """Cierra sesión de admin"""
    resultado = AuthService.cerrar_sesion(db, data.token)

    if not resultado['success']:
        raise HTTPException(status_code=400, detail=resultado.get('error'))

    return resultado


@router.post("/admin/verificar")
def verificar_admin(data: VerificarRequest, db: Session = Depends(get_db)):
    """Verifica si el token es de admin"""
    resultado = AuthService.verificar_admin(db, data.token)

    if not resultado['valida']:
        raise HTTPException(status_code=401, detail=resultado.get('error'))

    return resultado