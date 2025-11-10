import re


def validar_email(email):
    """Validación básica de email"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None


def validar_password(password):
    """Valida que la contraseña tenga al menos 6 caracteres"""
    return len(password) >= 6


def validar_nombre(nombre):
    """Valida que el nombre tenga al menos 2 caracteres"""
    return len(nombre.strip()) >= 2


def validar_token(token):
    """Valida que el token no esté vacío"""
    return token is not None and len(token.strip()) > 0