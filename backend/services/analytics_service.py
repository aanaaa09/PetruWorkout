# backend/services/analytics_service.py
"""
Lógica de negocio de analytics (Six Sigma, RTY, IC Wilson, Plotly).
El acceso a BD se delega completamente a backend.crud.analytics_crud.
"""

from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta
import math
import logging

from ..crud.analytics_crud import (
    KNOWN_SOURCES,
    KNOWN_BUTTONS,
    get_date_range,
    visits_count, clicks_count, bookings_count,
    visits_by_source, clicks_by_source, bookings_by_source,
    visits_daily, clicks_daily, bookings_daily,
    group_by_button,
    count_filtered, group_by_source, daily_series,
)

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════
#  UTILIDADES PURAMENTE MATEMÁTICAS
# ════════════════════════════════════════════════════════════

def wilson_ci(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0  # Sin datos, sin intervalo

    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom

    inside = p * (1 - p) / n + z * z / (4 * n * n)
    if inside < 0:
        inside = 0  # Evitar dominio negativo por errores de punto flotante

    margin = (z * math.sqrt(inside)) / denom

    return max(0.0, center - margin), min(1.0, center + margin)


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
#  FUNCIÓN PRINCIPAL
# ════════════════════════════════════════════════════════════

def get_full_analytics(
    db: Session,
    days:      Optional[int]  = None,
    date_from: Optional[str]  = None,
    date_to:   Optional[str]  = None,
    source:    Optional[str]  = None,
    button:    Optional[str]  = None,
) -> dict:
    start, end = get_date_range(days, date_from, date_to)

    # ── Totales ──────────────────────────────────────────────
    # El filtro de botón solo afecta a clicks (visitas y bookings no tienen button_location)
    total_visits   = visits_count(db, start, end, source)
    total_clicks   = clicks_count(db, start, end, source, button)
    total_bookings = bookings_count(db, start, end, source)

    # ── Six Sigma ─────────────────────────────────────────────
    dpmo  = round((1 - total_bookings / max(total_visits, 1)) * 1_000_000)
    sigma = dpmo_to_sigma(dpmo)
    y1    = total_clicks   / max(total_visits, 1)
    y2    = total_bookings / max(total_clicks,  1)
    rty   = y1 * y2
    ci_low, ci_high = wilson_ci(total_bookings, total_visits)

    # ── Por fuente ────────────────────────────────────────────
    v_map = visits_by_source(db, start, end, source)
    c_map = clicks_by_source(db, start, end, source, button)
    b_map = bookings_by_source(db, start, end, source)

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

    # ── Por botón (clicks) ─────────────────────────────────────
    # Nota: siempre devuelve la distribución completa (sin filtrar por button)
    # para que el gráfico muestre todos los botones aunque haya un filtro activo.
    btn_map = group_by_button(db, start, end, source)
    total_btn_clicks = sum(btn_map.values()) or 1
    buttons_stats = [
        {
            "button":  btn,
            "clicks":  cnt,
            "pct":     round(cnt / total_btn_clicks, 6),
        }
        for btn, cnt in sorted(btn_map.items(), key=lambda x: -x[1])
    ]

    # ── Tendencia diaria ──────────────────────────────────────
    vd = visits_daily(db, start, end, source)
    cd = clicks_daily(db, start, end, source, button)
    bd = bookings_daily(db, start, end, source)

    from datetime import date as date_type
    full_days = []
    cur = start
    while cur <= end:
        full_days.append(str(cur))
        cur += timedelta(days=1)

    trend = [
        {
            "date":     day,
            "visits":   vd.get(day, 0),
            "clicks":   cd.get(day, 0),
            "bookings": bd.get(day, 0),
        }
        for day in full_days
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
        "buttons": buttons_stats,
        "trend":   trend,
    }


def get_dashboard_kpis(
    db: Session,
    days:      Optional[int] = 30,
    date_from: Optional[str] = None,
    date_to:   Optional[str] = None,
    source:    Optional[str] = None,
    button:    Optional[str] = None,
) -> dict:
    start, end = get_date_range(days, date_from, date_to)
    v = visits_count(db, start, end, source)
    c = clicks_count(db, start, end, source, button)
    b = bookings_count(db, start, end, source)
    return {
        "success":         True,
        "total_visits":    v,
        "total_clicks":    c,
        "total_bookings":  b,
        "conversion_rate": round(b / max(v, 1), 6),
        "period":          {"start": str(start), "end": str(end)},
    }


def generate_trend_chart_html(
    db: Session,
    days:      Optional[int] = None,
    date_from: Optional[str] = None,
    date_to:   Optional[str] = None,
    source:    Optional[str] = None,
    button:    Optional[str] = None,
) -> str:
    """Genera HTML de Plotly para el gráfico de tendencia temporal."""
    import plotly.graph_objects as go
    from datetime import timedelta

    start, end = get_date_range(days, date_from, date_to)

    vd = visits_daily(db, start, end, source)
    cd = clicks_daily(db, start, end, source, button)
    bd = bookings_daily(db, start, end, source)

    from datetime import date as date_type
    full_days, cur = [], start
    while cur <= end:
        full_days.append(str(cur))
        cur += timedelta(days=1)

    visits_data   = [vd.get(d, 0) for d in full_days]
    clicks_data   = [cd.get(d, 0) for d in full_days]
    bookings_data = [bd.get(d, 0) for d in full_days]

    if sum(visits_data) + sum(clicks_data) + sum(bookings_data) == 0:
        return ""

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=full_days, y=visits_data, name="Visitas",
        mode="lines+markers",
        line=dict(color="#06d6a0", width=2), marker=dict(size=5, color="#06d6a0"),
        fill="tozeroy", fillcolor="rgba(6,214,160,0.07)",
        hovertemplate="<b>%{x}</b><br>Visitas: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=full_days, y=clicks_data, name="Clicks Calendly",
        mode="lines+markers",
        line=dict(color="#e63946", width=2), marker=dict(size=5, color="#e63946"),
        fill="tozeroy", fillcolor="rgba(230,57,70,0.07)",
        hovertemplate="<b>%{x}</b><br>Clicks: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=full_days, y=bookings_data, name="Citas agendadas",
        mode="lines+markers",
        line=dict(color="#ffd166", width=2), marker=dict(size=5, color="#ffd166"),
        fill="tozeroy", fillcolor="rgba(255,209,102,0.07)",
        hovertemplate="<b>%{x}</b><br>Citas: %{y}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=10, b=40), height=260,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(color="rgba(255,255,255,0.55)", size=12), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="rgba(255,255,255,0.45)", size=11), linecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="rgba(255,255,255,0.45)", size=11), rangemode="tozero"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="rgba(10,10,10,0.9)", font=dict(color="white", size=12), bordercolor="rgba(255,255,255,0.1)"),
    )
    return fig.to_html(
        full_html=False, include_plotlyjs="cdn",
        config={"displayModeBar": False, "responsive": True},
    )