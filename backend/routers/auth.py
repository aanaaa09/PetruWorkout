from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..schemas.auth import (
    RegistroRequest, LoginRequest, LogoutRequest,
    VerificarRequest
)
from ..services.AuthService import AuthService
from ..crud.sesion import sesion_crud

router = APIRouter(tags=["auth"])


@router.post("/registro")
def registro(data: RegistroRequest, db: Session = Depends(get_db)):
    """Registra un nuevo usuario"""
    resultado = AuthService.registrar_usuario(db, data.nombre, data.email, data.password)

    if not resultado['success']:
        raise HTTPException(status_code=400, detail=resultado['error'])

    return {
        'success': True,
        'mensaje': 'Usuario registrado correctamente',
        'token': resultado['data']['token'],
        'usuario': resultado['data']['usuario']
    }


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Inicia sesión"""
    resultado = AuthService.iniciar_sesion(db, data.email, data.password)

    if not resultado['success']:
        raise HTTPException(status_code=401, detail=resultado['error'])

    return {
        'success': True,
        'mensaje': 'Sesión iniciada correctamente',
        'token': resultado['data']['token'],
        'usuario': resultado['data']['usuario']
    }


@router.post("/logout")
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    """Cierra sesión"""
    resultado = AuthService.cerrar_sesion(db, data.token)

    if not resultado['success']:
        raise HTTPException(status_code=400, detail=resultado.get('error'))

    return {'success': True, 'mensaje': 'Sesión cerrada correctamente'}


@router.post("/verificar")
def verificar_sesion(data: VerificarRequest, db: Session = Depends(get_db)):
    """Verifica si una sesión es válida"""
    resultado = AuthService.verificar_sesion(db, data.token)

    if not resultado['valida']:
        raise HTTPException(status_code=401, detail=resultado.get('error'))

    return {'valida': True, 'usuario': resultado['usuario']}


@router.post("/limpiar-sesiones-expiradas")
def limpiar_sesiones_expiradas(db: Session = Depends(get_db)):
    """Limpia sesiones expiradas (endpoint de mantenimiento)"""
    eliminadas = sesion_crud.clean_expired(db)
    return {'success': True, 'mensaje': f'{eliminadas} sesiones expiradas eliminadas'}