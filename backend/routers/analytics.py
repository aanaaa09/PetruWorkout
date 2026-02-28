# backend/routers/analytics.py
"""
Router para el dashboard de analytics con métricas Six Sigma.
Endpoints:
  GET /api/admin/analytics  → todo en uno (tendencia + Six Sigma + por fuente)
  GET /api/admin/dashboard  → KPIs básicos (actualizado con filtros)
  GET /api/tracking/funnel  → embudo visita → click → booking (actualizado con filtros)
  GET /api/tracking/stats   → distribución por fuente (actualizado con filtros)
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from datetime import datetime, timedelta, date
import math
import logging
from datetime import timezone, timedelta

from ..config.database import get_db
from ..models.usuario import Usuario, TipoUsuario
from ..models.page_visit import PageVisit
from ..models.calendly_click import CalendlyClick
from ..models.calendly_booking import CalendlyBooking
from ..crud.sesion import sesion_crud
from ..crud.usuario import usuario_crud

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analytics"])

SPAIN_TZ = timezone(timedelta(hours=1))
EXCLUDED_SOURCES = ("direct", "internal")


# ════════════════════════════════════════════════════════════
#  DEPENDENCIA: igual que en admin_panel.py
# ════════════════════════════════════════════════════════════

def verify_admin_token(
        token: str = Header(None, alias="token"),
        db: Session = Depends(get_db)
) -> Usuario:
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado en el header")

    sesion = sesion_crud.validate_token(db, token)
    if not sesion:
        raise HTTPException(status_code=401, detail="Sesión expirada o inválida")

    usuario = usuario_crud.get_by_id(db, sesion.usuario_id)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if usuario.tipo_usuario != TipoUsuario.ADMIN:
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requieren permisos de administrador.")

    return usuario


# ════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════

def get_date_range(
    days: Optional[int],
    date_from: Optional[str],
    date_to: Optional[str]
):
    """Devuelve (fecha_inicio, fecha_fin) como objetos date en hora España, hasta d-1."""
    now_spain = datetime.now(SPAIN_TZ)
    yesterday = now_spain.date() - timedelta(days=1)

    if date_from and date_to:
        try:
            start = date.fromisoformat(date_from)
            end   = min(date.fromisoformat(date_to), yesterday)
            return start, end
        except ValueError:
            pass

    days  = days or 30
    start = yesterday - timedelta(days=days - 1)
    return start, yesterday


def wilson_ci(k: int, n: int, z: float = 1.96):
    """Intervalo de confianza de Wilson al 95% para una proporción."""
    if n == 0:
        return 0.0, 0.0
    p      = k / n
    denom  = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def dpmo_to_sigma(dpmo: float) -> float:
    """Conversión DPMO → nivel sigma usando tabla de referencia estándar."""
    table = [
        (691462, 1.0),
        (308538, 2.0),
        (66807,  3.0),
        (6210,   4.0),
        (233,    5.0),
        (3.4,    6.0),
    ]
    if dpmo >= 691462: return 1.0
    if dpmo <= 3.4:    return 6.0
    for i in range(len(table) - 1):
        hi, s_lo = table[i]
        lo, s_hi = table[i + 1]
        if lo <= dpmo <= hi:
            t = (dpmo - hi) / (lo - hi)
            return round(s_lo + t * (s_hi - s_lo), 3)
    return 1.0


# ════════════════════════════════════════════════════════════
#  ENDPOINT 1: /api/admin/analytics  (NUEVO — todo en uno)
# ════════════════════════════════════════════════════════════

@router.get("/api/admin/analytics")
def get_analytics(
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db),
        days:      Optional[int] = Query(None, description="Días hacia atrás (7, 30, 90)"),
        date_from: Optional[str] = Query(None, description="Fecha inicio YYYY-MM-DD"),
        date_to:   Optional[str] = Query(None, description="Fecha fin YYYY-MM-DD"),
        source:    Optional[str] = Query(None, description="Filtro fuente de tráfico"),
):
    """
    Devuelve en una sola llamada:
    - totals: visitas, clicks, bookings del período
    - six_sigma: DPMO, nivel sigma, RTY, IC 95%
    - sources: métricas por fuente (con IC 95% y sigma individual)
    - trend: serie temporal diaria (visitas, clicks, bookings)
    """
    try:
        start, end = get_date_range(days, date_from, date_to)

        # ── Filtro fuente ────────────────────────────────────────────────
        def apply_source_filter(query, model):
            query = query.filter(model.traffic_source.notin_(EXCLUDED_SOURCES))
            if source and source not in EXCLUDED_SOURCES:
                query = query.filter(model.traffic_source == source)
            return query

        # ── Totales del período ──────────────────────────────────────────
        visits_q = apply_source_filter(
            db.query(func.count(PageVisit.id))
              .filter(func.date(PageVisit.fecha).between(start, end)),
            PageVisit
        )
        clicks_q = apply_source_filter(
            db.query(func.count(CalendlyClick.id))
              .filter(func.date(CalendlyClick.timestamp).between(start, end)),
            CalendlyClick
        )
        bookings_q = apply_source_filter(
            db.query(func.count(CalendlyBooking.id))
              .filter(func.date(CalendlyBooking.timestamp).between(start, end)),
            CalendlyBooking
        )

        total_visits   = visits_q.scalar()   or 0
        total_clicks   = clicks_q.scalar()   or 0
        total_bookings = bookings_q.scalar() or 0

        # ── Six Sigma global ─────────────────────────────────────────────
        dpmo  = round((1 - total_bookings / max(total_visits, 1)) * 1_000_000)
        sigma = dpmo_to_sigma(dpmo)

        y1  = total_clicks   / max(total_visits, 1)
        y2  = total_bookings / max(total_clicks, 1)
        rty = y1 * y2

        ci_low, ci_high = wilson_ci(total_bookings, total_visits)

        # ── Por fuente ───────────────────────────────────────────────────
        # Visitas por fuente
        v_by_src = (
            apply_source_filter(
                db.query(PageVisit.traffic_source, func.count(PageVisit.id).label("n"))
                  .filter(func.date(PageVisit.fecha).between(start, end)),
                PageVisit
            )
            .group_by(PageVisit.traffic_source)
            .all()
        )
        v_map = {r.traffic_source: r.n for r in v_by_src}

        # Clicks por fuente
        c_by_src = (
            apply_source_filter(
                db.query(CalendlyClick.traffic_source, func.count(CalendlyClick.id).label("n"))
                  .filter(func.date(CalendlyClick.timestamp).between(start, end)),
                CalendlyClick
            )
            .group_by(CalendlyClick.traffic_source)
            .all()
        )
        c_map = {r.traffic_source: r.n for r in c_by_src}

        # Bookings por fuente
        b_by_src = (
            apply_source_filter(
                db.query(CalendlyBooking.traffic_source, func.count(CalendlyBooking.id).label("n"))
                  .filter(func.date(CalendlyBooking.timestamp).between(start, end)),
                CalendlyBooking
            )
            .group_by(CalendlyBooking.traffic_source)
            .all()
        )
        b_map = {r.traffic_source: r.n for r in b_by_src}

        all_sources = set(v_map) | set(c_map) | set(b_map)
        sources_stats = []
        for src in all_sources:
            n = v_map.get(src, 0)
            c = c_map.get(src, 0)
            k = b_map.get(src, 0)
            src_ci_low, src_ci_high = wilson_ci(k, n)
            src_dpmo  = round((1 - k / max(n, 1)) * 1_000_000)
            src_sigma = dpmo_to_sigma(src_dpmo)
            sources_stats.append({
                "source":    src,
                "visits":    n,
                "clicks":    c,
                "bookings":  k,
                "conv_rate": round(k / max(n, 1), 6),
                "ci_low":    round(src_ci_low,  6),
                "ci_high":   round(src_ci_high, 6),
                "dpmo":      src_dpmo,
                "sigma":     src_sigma,
            })
        sources_stats.sort(key=lambda x: x["visits"], reverse=True)

        # ── Tendencia diaria ─────────────────────────────────────────────
        v_daily = (
            apply_source_filter(
                db.query(
                    func.date(PageVisit.fecha).label("day"),
                    func.count(PageVisit.id).label("n")
                ).filter(func.date(PageVisit.fecha).between(start, end)),
                PageVisit
            )
            .group_by(func.date(PageVisit.fecha))
            .all()
        )
        c_daily = (
            apply_source_filter(
                db.query(
                    func.date(CalendlyClick.timestamp).label("day"),
                    func.count(CalendlyClick.id).label("n")
                ).filter(func.date(CalendlyClick.timestamp).between(start, end)),
                CalendlyClick
            )
            .group_by(func.date(CalendlyClick.timestamp))
            .all()
        )
        b_daily = (
            apply_source_filter(
                db.query(
                    func.date(CalendlyBooking.timestamp).label("day"),
                    func.count(CalendlyBooking.id).label("n")
                ).filter(func.date(CalendlyBooking.timestamp).between(start, end)),
                CalendlyBooking
            )
            .group_by(func.date(CalendlyBooking.timestamp))
            .all()
        )

        vd = {str(r.day): r.n for r in v_daily}
        cd = {str(r.day): r.n for r in c_daily}
        bd = {str(r.day): r.n for r in b_daily}

        all_days = sorted(set(vd) | set(cd) | set(bd))
        trend = [
            {
                "date":     day,
                "visits":   vd.get(day, 0),
                "clicks":   cd.get(day, 0),
                "bookings": bd.get(day, 0),
            }
            for day in all_days
        ]

        return {
            "period": {"start": str(start), "end": str(end)},
            "totals": {
                "visits":   total_visits,
                "clicks":   total_clicks,
                "bookings": total_bookings,
            },
            "six_sigma": {
                "dpmo":   dpmo,
                "sigma":  sigma,
                "rty":    round(rty, 6),
                "rty_y1": round(y1, 6),
                "rty_y2": round(y2, 6),
                "ci_low":  round(ci_low,  6),
                "ci_high": round(ci_high, 6),
            },
            "sources": sources_stats,
            "trend":   trend,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en analytics: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener analytics")


# ════════════════════════════════════════════════════════════
#  ENDPOINT 2: /api/admin/dashboard  (actualizado con filtros)
#  NOTA: Si ya tienes este endpoint en admin_panel.py,
#  reemplázalo con este o fusiona la lógica de filtros.
# ════════════════════════════════════════════════════════════

@router.get("/api/admin/dashboard")
def get_dashboard_filtered(
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db),
        days:      Optional[int] = Query(30),
        date_from: Optional[str] = Query(None),
        date_to:   Optional[str] = Query(None),
        source:    Optional[str] = Query(None),
):
    """KPIs básicos del dashboard con soporte de filtros."""
    try:
        start, end = get_date_range(days, date_from, date_to)

        def apply_source_filter(query, model):
            query = query.filter(model.traffic_source.notin_(EXCLUDED_SOURCES))
            if source and source not in EXCLUDED_SOURCES:
                query = query.filter(model.traffic_source == source)
            return query

        total_visits = apply_source_filter(
            db.query(func.count(PageVisit.id))
              .filter(func.date(PageVisit.fecha).between(start, end)),
            PageVisit
        ).scalar() or 0

        total_clicks = apply_source_filter(
            db.query(func.count(CalendlyClick.id))
              .filter(func.date(CalendlyClick.timestamp).between(start, end)),
            CalendlyClick
        ).scalar() or 0

        total_bookings = apply_source_filter(
            db.query(func.count(CalendlyBooking.id))
              .filter(func.date(CalendlyBooking.timestamp).between(start, end)),
            CalendlyBooking
        ).scalar() or 0

        return {
            "success":         True,
            "total_visits":    total_visits,
            "total_clicks":    total_clicks,
            "total_bookings":  total_bookings,
            "conversion_rate": round(total_bookings / max(total_visits, 1), 6),
            "period":          {"start": str(start), "end": str(end)},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas")


# ════════════════════════════════════════════════════════════
#  ENDPOINT 3: /api/tracking/funnel  (actualizado con filtros)
# ════════════════════════════════════════════════════════════

@router.get("/api/tracking/funnel")
def get_funnel(
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db),
        days:      Optional[int] = Query(30),
        date_from: Optional[str] = Query(None),
        date_to:   Optional[str] = Query(None),
        source:    Optional[str] = Query(None),
):
    """Embudo de conversión: visita → click Calendly → booking."""
    try:
        start, end = get_date_range(days, date_from, date_to)

        def apply_source_filter(query, model):
            query = query.filter(model.traffic_source.notin_(EXCLUDED_SOURCES))
            if source and source not in EXCLUDED_SOURCES:
                query = query.filter(model.traffic_source == source)
            return query

        v = apply_source_filter(
            db.query(func.count(PageVisit.id))
              .filter(func.date(PageVisit.fecha).between(start, end)),
            PageVisit
        ).scalar() or 0

        c = apply_source_filter(
            db.query(func.count(CalendlyClick.id))
              .filter(func.date(CalendlyClick.timestamp).between(start, end)),
            CalendlyClick
        ).scalar() or 0

        b = apply_source_filter(
            db.query(func.count(CalendlyBooking.id))
              .filter(func.date(CalendlyBooking.timestamp).between(start, end)),
            CalendlyBooking
        ).scalar() or 0

        return {
            "success":  True,
            "visits":   v,
            "clicks":   c,
            "bookings": b,
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


# ════════════════════════════════════════════════════════════
#  ENDPOINT 4: /api/tracking/stats  (actualizado con filtros)
# ════════════════════════════════════════════════════════════

@router.get("/api/tracking/stats")
def get_stats(
        admin: Usuario = Depends(verify_admin_token),
        db: Session = Depends(get_db),
        days:      Optional[int] = Query(30),
        date_from: Optional[str] = Query(None),
        date_to:   Optional[str] = Query(None),
        source:    Optional[str] = Query(None),
):
    """Distribución de tráfico y conversión por fuente."""
    try:
        start, end = get_date_range(days, date_from, date_to)

        def apply_source_filter(query, model):
            query = query.filter(model.traffic_source.notin_(EXCLUDED_SOURCES))
            if source and source not in EXCLUDED_SOURCES:
                query = query.filter(model.traffic_source == source)
            return query

        v_by_src = (
            apply_source_filter(
                db.query(PageVisit.traffic_source, func.count(PageVisit.id).label("n"))
                  .filter(func.date(PageVisit.fecha).between(start, end)),
                PageVisit
            )
            .group_by(PageVisit.traffic_source).all()
        )
        c_by_src = (
            apply_source_filter(
                db.query(CalendlyClick.traffic_source, func.count(CalendlyClick.id).label("n"))
                  .filter(func.date(CalendlyClick.timestamp).between(start, end)),
                CalendlyClick
            )
            .group_by(CalendlyClick.traffic_source).all()
        )
        b_by_src = (
            apply_source_filter(
                db.query(CalendlyBooking.traffic_source, func.count(CalendlyBooking.id).label("n"))
                  .filter(func.date(CalendlyBooking.timestamp).between(start, end)),
                CalendlyBooking
            )
            .group_by(CalendlyBooking.traffic_source).all()
        )

        v_map = {r.traffic_source: r.n for r in v_by_src}
        c_map = {r.traffic_source: r.n for r in c_by_src}
        b_map = {r.traffic_source: r.n for r in b_by_src}

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


# ════════════════════════════════════════════════════════════
#  ENDPOINT 5: /api/admin/verify  (ya existe — no tocar)
#  ENDPOINT 6: /api/admin/logout  (ya existe — no tocar)
# ════════════════════════════════════════════════════════════