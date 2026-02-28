# backend/services/analytics_service.py
"""
Servicio que concentra toda la lógica de cálculo de analytics:
  - Rango de fechas
  - Filtro por fuente (excluye direct/internal)
  - Six Sigma: DPMO, sigma, RTY, IC Wilson
  - Construcción de totales, fuentes y tendencia diaria
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta, date, timezone
import math
import logging

from ..models.page_visit import PageVisit
from ..models.calendly_click import CalendlyClick
from ..models.calendly_booking import CalendlyBooking

logger = logging.getLogger(__name__)

SPAIN_TZ = timezone(timedelta(hours=1))
EXCLUDED_SOURCES = ("direct", "internal")


# ════════════════════════════════════════════════════════════
#  UTILIDADES PURAS
# ════════════════════════════════════════════════════════════

def get_date_range(
    days: Optional[int],
    date_from: Optional[str],
    date_to: Optional[str],
):
    """Devuelve (start, end) como date. Siempre hasta ayer (hora España)."""
    now_spain = datetime.now(SPAIN_TZ)
    yesterday = now_spain.date() - timedelta(days=1)

    if date_from and date_to:
        try:
            start = date.fromisoformat(date_from)
            end   = min(date.fromisoformat(date_to), yesterday)
            return start, end
        except ValueError:
            pass

    d     = days or 30
    start = yesterday - timedelta(days=d - 1)
    return start, yesterday


def wilson_ci(k: int, n: int, z: float = 1.96):
    """IC de Wilson al 95% para una proporción k/n."""
    if n == 0:
        return 0.0, 0.0
    p      = k / n
    denom  = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def dpmo_to_sigma(dpmo: float) -> float:
    table = [
        (691462, 1.0), (308538, 2.0), (66807, 3.0),
        (6210,   4.0), (233,    5.0), (3.4,   6.0),
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
#  HELPERS DE CONSULTA
# ════════════════════════════════════════════════════════════

def _apply_source_filter(query, model, source: Optional[str]):
    """
    Siempre excluye direct/internal.
    Si source es una fuente concreta, filtra además por ella.
    """
    query = query.filter(model.traffic_source.notin_(EXCLUDED_SOURCES))
    if source and source not in EXCLUDED_SOURCES:
        query = query.filter(model.traffic_source == source)
    return query


def count_filtered(db: Session, model, date_col, start, end, source):
    return _apply_source_filter(
        db.query(func.count(model.id))
          .filter(func.date(date_col).between(start, end)),
        model, source
    ).scalar() or 0


def group_by_source(db: Session, model, date_col, start, end, source):
    return {
        r.traffic_source: r.n
        for r in _apply_source_filter(
            db.query(model.traffic_source, func.count(model.id).label("n"))
              .filter(func.date(date_col).between(start, end)),
            model, source
        ).group_by(model.traffic_source).all()
    }


def daily_series(db: Session, model, date_col, start, end, source):
    return {
        str(r.day): r.n
        for r in _apply_source_filter(
            db.query(func.date(date_col).label("day"), func.count(model.id).label("n"))
              .filter(func.date(date_col).between(start, end)),
            model, source
        ).group_by(func.date(date_col)).all()
    }


# ════════════════════════════════════════════════════════════
#  FUNCIÓN PRINCIPAL
# ════════════════════════════════════════════════════════════

def get_full_analytics(
    db: Session,
    days:      Optional[int]  = None,
    date_from: Optional[str]  = None,
    date_to:   Optional[str]  = None,
    source:    Optional[str]  = None,
) -> dict:
    """
    Devuelve el payload completo para /api/admin/analytics:
      period, totals, six_sigma, sources, trend
    """
    start, end = get_date_range(days, date_from, date_to)

    # ── Totales ──────────────────────────────────────────────────────────
    total_visits   = count_filtered(db, PageVisit,       PageVisit.fecha,          start, end, source)
    total_clicks   = count_filtered(db, CalendlyClick,   CalendlyClick.timestamp,  start, end, source)
    total_bookings = count_filtered(db, CalendlyBooking, CalendlyBooking.timestamp, start, end, source)

    # ── Six Sigma ─────────────────────────────────────────────────────────
    dpmo  = round((1 - total_bookings / max(total_visits, 1)) * 1_000_000)
    sigma = dpmo_to_sigma(dpmo)
    y1    = total_clicks   / max(total_visits, 1)
    y2    = total_bookings / max(total_clicks,  1)
    rty   = y1 * y2
    ci_low, ci_high = wilson_ci(total_bookings, total_visits)

    # ── Por fuente ────────────────────────────────────────────────────────
    v_map = group_by_source(db, PageVisit,       PageVisit.fecha,          start, end, source)
    c_map = group_by_source(db, CalendlyClick,   CalendlyClick.timestamp,  start, end, source)
    b_map = group_by_source(db, CalendlyBooking, CalendlyBooking.timestamp, start, end, source)

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

    # ── Tendencia diaria ─────────────────────────────────────────────────
    # SIEMPRE excluye direct/internal → el gráfico tiene datos con source=None (todos)
    vd = daily_series(db, PageVisit,       PageVisit.fecha,          start, end, source)
    cd = daily_series(db, CalendlyClick,   CalendlyClick.timestamp,  start, end, source)
    bd = daily_series(db, CalendlyBooking, CalendlyBooking.timestamp, start, end, source)

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
        "period":  {"start": str(start), "end": str(end)},
        "totals":  {
            "visits":   total_visits,
            "clicks":   total_clicks,
            "bookings": total_bookings,
        },
        "six_sigma": {
            "dpmo":    dpmo,
            "sigma":   sigma,
            "rty":     round(rty,    6),
            "rty_y1":  round(y1,     6),
            "rty_y2":  round(y2,     6),
            "ci_low":  round(ci_low, 6),
            "ci_high": round(ci_high,6),
        },
        "sources": sources_stats,
        "trend":   trend,
    }


def get_dashboard_kpis(
    db: Session,
    days:      Optional[int] = 30,
    date_from: Optional[str] = None,
    date_to:   Optional[str] = None,
    source:    Optional[str] = None,
) -> dict:
    """KPIs básicos para /api/admin/dashboard."""
    start, end = get_date_range(days, date_from, date_to)
    v = count_filtered(db, PageVisit,       PageVisit.fecha,          start, end, source)
    c = count_filtered(db, CalendlyClick,   CalendlyClick.timestamp,  start, end, source)
    b = count_filtered(db, CalendlyBooking, CalendlyBooking.timestamp, start, end, source)
    return {
        "success":         True,
        "total_visits":    v,
        "total_clicks":    c,
        "total_bookings":  b,
        "conversion_rate": round(b / max(v, 1), 6),
        "period":          {"start": str(start), "end": str(end)},
    }