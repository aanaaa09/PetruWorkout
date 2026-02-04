# backend/schemas/admin.py
"""
Schemas de Pydantic para el panel de administración
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional


class AdminLoginRequest(BaseModel):
    """Request para login de admin"""
    email: EmailStr
    password: str


class AdminChangePasswordRequest(BaseModel):
    """Request para cambiar contraseña"""
    current_password: str
    new_password: str


class AdminSendEmailRequest(BaseModel):
    """Request para enviar email"""
    subject: str
    message: str
    send_to: str  # "all" o "selected"
    selected_ids: Optional[List[int]] = None


class TrafficSourceStat(BaseModel):
    """Estadística de fuente de tráfico"""
    fuente: str
    total: int


class AdminDashboardResponse(BaseModel):
    """Response del dashboard"""
    total_usuarios_newsletter: int
    total_consultas: int
    total_visitas: int
    visitas_unicas: int
    total_clicks_calendly: int
    total_bookings: int
    tasa_conversion: float
    trafico_por_fuente: List[TrafficSourceStat]