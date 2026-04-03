# backend/routers/analytics.py
"""
Router de analytics.
Delega toda la lógica en analytics_service.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional
import logging

from ..config.database import get_db
from ..models.usuario import Usuario
from ..models.page_visit import PageVisit
from ..models.calendly_click import CalendlyClick
from ..models.calendly_booking import CalendlyBooking
from ..services.auth_service import verify_admin_token
from ..services.analytics_service import (
    get_full_analytics,
    get_dashboard_kpis,
    generate_trend_chart_html,
    count_filtered,
    group_by_source,
    get_date_range,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analytics"])


# ── Analytics completo ────────────────────────────────────────────

@router.get("/api/admin/analytics")
def get_analytics(
    admin: Usuario = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    days:      Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to:   Optional[str] = Query(None),
    source:    Optional[str] = Query(None),
    button:    Optional[str] = Query(None),
):
    try:
        return get_full_analytics(
            db, days=days, date_from=date_from, date_to=date_to,
            source=source, button=button,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en analytics: {e}")
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error al obtener analytics")


# ── Gráfico de tendencia (Plotly HTML) ───────────────────────────

@router.get("/api/admin/trend-chart", response_class=HTMLResponse)
def get_trend_chart(
    admin: Usuario = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    days:      Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to:   Optional[str] = Query(None),
    source:    Optional[str] = Query(None),
    button:    Optional[str] = Query(None),
):
    try:
        html = generate_trend_chart_html(
            db, days=days, date_from=date_from, date_to=date_to,
            source=source, button=button,
        )
        return HTMLResponse(
            content=html or "<p style='color:rgba(255,255,255,.4);text-align:center;padding:3rem'>Sin datos para este período</p>"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando gráfico tendencia: {e}")
        raise HTTPException(status_code=500, detail="Error al generar gráfico")


# ── Dashboard KPIs ────────────────────────────────────────────────

@router.get("/api/admin/dashboard")
def get_dashboard_filtered(
    admin: Usuario = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    days:      Optional[int] = Query(30),
    date_from: Optional[str] = Query(None),
    date_to:   Optional[str] = Query(None),
    source:    Optional[str] = Query(None),
    button:    Optional[str] = Query(None),
):
    try:
        return get_dashboard_kpis(
            db, days=days, date_from=date_from, date_to=date_to,
            source=source, button=button,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas")


# ── Embudo de conversión ──────────────────────────────────────────

@router.get("/api/tracking/funnel")
def get_funnel(
    admin: Usuario = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    days:      Optional[int] = Query(30),
    date_from: Optional[str] = Query(None),
    date_to:   Optional[str] = Query(None),
    source:    Optional[str] = Query(None),
    button:    Optional[str] = Query(None),
):
    try:
        start, end = get_date_range(days, date_from, date_to)
        v = count_filtered(db, PageVisit,       PageVisit.fecha,          start, end, source)
        c = count_filtered(db, CalendlyClick,   CalendlyClick.timestamp,  start, end, source, button)
        b = count_filtered(db, CalendlyBooking, CalendlyBooking.timestamp, start, end, source)
        return {
            "success": True, "visits": v, "clicks": c, "bookings": b,
            "steps": [
                {"name": "Visitas",         "count": v, "rate": 1.0},
                {"name": "Clicks Calendly", "count": c, "rate": round(c / max(v, 1), 6)},
                {"name": "Citas agendadas", "count": b, "rate": round(b / max(v, 1), 6)},
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en funnel: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener embudo")


# ── Stats por fuente ──────────────────────────────────────────────

@router.get("/api/tracking/stats")
def get_stats(
    admin: Usuario = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    days:      Optional[int] = Query(30),
    date_from: Optional[str] = Query(None),
    date_to:   Optional[str] = Query(None),
    source:    Optional[str] = Query(None),
    button:    Optional[str] = Query(None),
):
    try:
        start, end = get_date_range(days, date_from, date_to)
        v_map = group_by_source(db, PageVisit,       PageVisit.fecha,          start, end, source)
        c_map = group_by_source(db, CalendlyClick,   CalendlyClick.timestamp,  start, end, source, button)
        b_map = group_by_source(db, CalendlyBooking, CalendlyBooking.timestamp, start, end, source)

        all_sources = set(v_map) | set(c_map) | set(b_map)
        sources = []
        for src in all_sources:
            n = v_map.get(src, 0)
            k = b_map.get(src, 0)
            sources.append({
                "source":    src,
                "visits":    n,
                "clicks":    c_map.get(src, 0),
                "bookings":  k,
                "conv_rate": round(k / max(n, 1), 6),
            })
        sources.sort(key=lambda x: x["visits"], reverse=True)
        return {"success": True, "sources": sources}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en stats: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas")