# ==========================================
# backend/tests/unit/test_analytics.py
# ==========================================
"""
Tests para analytics_service y los endpoints de analytics:
  /api/admin/analytics
  /api/tracking/funnel
  /api/tracking/stats
"""
import pytest
from datetime import datetime, timedelta, date


# ──────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────

def _create_admin_session(db, email="analytics_admin@test.com"):
    from backend.crud.usuario import usuario_crud
    from backend.crud.sesion import sesion_crud
    from backend.models.usuario import TipoUsuario

    admin = usuario_crud.create(db, nombre="Admin", email=email,
                                password="admin123", tipo_usuario=TipoUsuario.ADMIN)
    sesion = sesion_crud.create(db, admin.id)
    return sesion.token


def _yesterday():
    return date.today() - timedelta(days=1)


def _move_to_yesterday(db, obj):
    """Ajusta fecha del registro para que entre en el periodo del dashboard."""
    yd = _yesterday()
    obj.fecha = yd
    if hasattr(obj, 'timestamp'):
        obj.timestamp = datetime.now() - timedelta(days=1)
    db.commit()
    return obj


def _seed_tracking(db, source="instagram", visits=10, clicks=5, bookings=2):
    """Crea registros de tracking en fuentes conocidas, fechados ayer."""
    from backend.crud.tracking import tracking_crud

    visit_objs = []
    for i in range(visits):
        v = tracking_crud.create_page_visit(db, session_id=f"{source}_v_{i}",
                                            traffic_source=source, landing_page="/")
        _move_to_yesterday(db, v)
        visit_objs.append(v)

    click_objs = []
    for i in range(clicks):
        c = tracking_crud.create_calendly_click(db, session_id=f"{source}_c_{i}",
                                                traffic_source=source, button_id="hero-cta")
        _move_to_yesterday(db, c)
        click_objs.append(c)

    booking_objs = []
    for i in range(bookings):
        b = tracking_crud.create_calendly_booking(
            db, calendly_event_id=f"evt_{source}_{i}",
            invitee_email=f"{source}_user{i}@test.com", invitee_name=f"User {i}",
            event_start_time=datetime.now(), booking_timestamp=datetime.now(),
            session_id=f"{source}_v_{i}", traffic_source=source
        )
        _move_to_yesterday(db, b)
        booking_objs.append(b)

    return visit_objs, click_objs, booking_objs


# ══════════════════════════════════════════
#  TESTS DE analytics_service (unidad pura)
# ══════════════════════════════════════════

class TestAnalyticsServiceUnit:

    def test_get_date_range_default(self):
        """Sin parámetros devuelve 30 días hasta ayer"""
        from backend.services.analytics_service import get_date_range
        start, end = get_date_range(None, None, None)
        yd = _yesterday()
        assert end == yd
        assert (end - start).days == 29   # 30 días inclusive

    def test_get_date_range_custom_days(self):
        from backend.services.analytics_service import get_date_range
        start, end = get_date_range(7, None, None)
        assert (end - start).days == 6

    def test_get_date_range_explicit_dates(self):
        from backend.services.analytics_service import get_date_range
        start, end = get_date_range(None, "2026-01-01", "2026-01-31")
        assert str(start) == "2026-01-01"
        assert str(end) == "2026-01-31"

    def test_get_date_range_caps_at_yesterday(self):
        """date_to en el futuro queda acotado a ayer"""
        from backend.services.analytics_service import get_date_range
        future = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        start, end = get_date_range(None, "2026-01-01", future)
        assert end == _yesterday()

    def test_wilson_ci_zero_events(self):
        from backend.services.analytics_service import wilson_ci
        lo, hi = wilson_ci(0, 0)
        assert lo == 0.0
        assert hi == 0.0

    def test_wilson_ci_perfect_conversion(self):
        from backend.services.analytics_service import wilson_ci
        lo, hi = wilson_ci(10, 10)
        assert lo > 0.7
        assert hi == 1.0

    def test_wilson_ci_low_conversion(self):
        from backend.services.analytics_service import wilson_ci
        lo, hi = wilson_ci(1, 100)
        assert 0 <= lo < hi <= 1

    def test_dpmo_to_sigma_boundaries(self):
        from backend.services.analytics_service import dpmo_to_sigma
        assert dpmo_to_sigma(3.4) == 6.0
        assert dpmo_to_sigma(691462) == 1.0
        assert dpmo_to_sigma(700000) == 1.0   # por encima del máximo

    def test_dpmo_to_sigma_typical(self):
        from backend.services.analytics_service import dpmo_to_sigma
        # 66807 DPMO ≈ sigma 3
        sigma = dpmo_to_sigma(66807)
        assert 2.9 <= sigma <= 3.1

    def test_dpmo_to_sigma_six_sigma(self):
        from backend.services.analytics_service import dpmo_to_sigma
        sigma = dpmo_to_sigma(3.4)
        assert sigma == 6.0

    def test_count_filtered_empty_db(self, db):
        from backend.services.analytics_service import count_filtered, get_date_range
        from backend.models.page_visit import PageVisit
        start, end = get_date_range(30, None, None)
        result = count_filtered(db, PageVisit, PageVisit.fecha, start, end, None)
        assert result == 0

    def test_count_filtered_with_known_source(self, db):
        from backend.services.analytics_service import count_filtered, get_date_range
        from backend.models.page_visit import PageVisit
        from backend.crud.tracking import tracking_crud

        v = tracking_crud.create_page_visit(db, "s1", "instagram", landing_page="/")
        _move_to_yesterday(db, v)

        start, end = get_date_range(30, None, None)
        result = count_filtered(db, PageVisit, PageVisit.fecha, start, end, None)
        assert result >= 1

    def test_count_filtered_excludes_unknown_source(self, db):
        from backend.services.analytics_service import count_filtered, get_date_range
        from backend.models.page_visit import PageVisit
        from backend.crud.tracking import tracking_crud

        # "direct" está excluido por KNOWN_SOURCES
        v = tracking_crud.create_page_visit(db, "s_direct", "direct", landing_page="/")
        _move_to_yesterday(db, v)

        start, end = get_date_range(30, None, None)
        result = count_filtered(db, PageVisit, PageVisit.fecha, start, end, None)
        assert result == 0

    def test_group_by_source_returns_dict(self, db):
        from backend.services.analytics_service import group_by_source, get_date_range
        from backend.models.page_visit import PageVisit
        from backend.crud.tracking import tracking_crud

        for _ in range(3):
            v = tracking_crud.create_page_visit(db, f"sg_{_}", "instagram", landing_page="/")
            _move_to_yesterday(db, v)
        for _ in range(2):
            v = tracking_crud.create_page_visit(db, f"sg_yt_{_}", "youtube", landing_page="/")
            _move_to_yesterday(db, v)

        start, end = get_date_range(30, None, None)
        result = group_by_source(db, PageVisit, PageVisit.fecha, start, end, None)
        assert result.get("instagram", 0) == 3
        assert result.get("youtube", 0) == 2


class TestGetFullAnalytics:

    def test_returns_all_sections(self, db):
        from backend.services.analytics_service import get_full_analytics
        result = get_full_analytics(db)
        assert 'period' in result
        assert 'totals' in result
        assert 'six_sigma' in result
        assert 'sources' in result
        assert 'trend' in result

    def test_totals_zero_with_empty_db(self, db):
        from backend.services.analytics_service import get_full_analytics
        result = get_full_analytics(db)
        assert result['totals']['visits'] == 0
        assert result['totals']['clicks'] == 0
        assert result['totals']['bookings'] == 0

    def test_totals_with_data(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="instagram", visits=10, clicks=5, bookings=2)
        result = get_full_analytics(db)
        assert result['totals']['visits'] == 10
        assert result['totals']['clicks'] == 5
        assert result['totals']['bookings'] == 2

    def test_six_sigma_structure(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="instagram", visits=10, clicks=5, bookings=2)
        result = get_full_analytics(db)
        ss = result['six_sigma']
        assert 'dpmo' in ss
        assert 'sigma' in ss
        assert 'rty' in ss
        assert 'ci_low' in ss
        assert 'ci_high' in ss
        assert ss['ci_low'] <= ss['ci_high']

    def test_sources_list_contains_seeded_source(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="youtube", visits=5, clicks=2, bookings=1)
        result = get_full_analytics(db)
        src_names = [s['source'] for s in result['sources']]
        assert 'youtube' in src_names

    def test_sources_sorted_by_visits_desc(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="instagram", visits=20, clicks=5, bookings=1)
        _seed_tracking(db, source="youtube", visits=5, clicks=2, bookings=0)
        result = get_full_analytics(db)
        visits = [s['visits'] for s in result['sources']]
        assert visits == sorted(visits, reverse=True)

    def test_trend_is_list(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="instagram", visits=5, clicks=2, bookings=1)
        result = get_full_analytics(db)
        assert isinstance(result['trend'], list)

    def test_trend_contains_yesterday(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="instagram", visits=3, clicks=1, bookings=0)
        result = get_full_analytics(db)
        dates = [entry['date'] for entry in result['trend']]
        assert str(_yesterday()) in dates

    def test_source_filter_returns_only_one_source(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="instagram", visits=10, clicks=3, bookings=1)
        _seed_tracking(db, source="youtube", visits=5, clicks=2, bookings=0)
        result = get_full_analytics(db, source="instagram")
        assert result['totals']['visits'] == 10
        for s in result['sources']:
            assert s['source'] == "instagram"

    def test_per_source_conv_rate(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="facebook", visits=20, clicks=5, bookings=4)
        result = get_full_analytics(db, source="facebook")
        fb = next(s for s in result['sources'] if s['source'] == 'facebook')
        assert abs(fb['conv_rate'] - 4 / 20) < 1e-5

    def test_per_source_wilson_ci(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="organic_search", visits=50, clicks=10, bookings=5)
        result = get_full_analytics(db, source="organic_search")
        src = next(s for s in result['sources'] if s['source'] == 'organic_search')
        assert 0 <= src['ci_low'] <= src['conv_rate'] <= src['ci_high'] <= 1


class TestGetDashboardKpis:

    def test_returns_expected_keys(self, db):
        from backend.services.analytics_service import get_dashboard_kpis
        result = get_dashboard_kpis(db)
        for key in ('success', 'total_visits', 'total_clicks', 'total_bookings',
                    'conversion_rate', 'period'):
            assert key in result

    def test_success_true(self, db):
        from backend.services.analytics_service import get_dashboard_kpis
        assert get_dashboard_kpis(db)['success'] is True

    def test_conversion_rate_fraction(self, db):
        """conversion_rate es fracción 0–1, no porcentaje"""
        from backend.services.analytics_service import get_dashboard_kpis
        _seed_tracking(db, source="instagram", visits=100, clicks=10, bookings=10)
        result = get_dashboard_kpis(db)
        assert abs(result['conversion_rate'] - 0.1) < 0.001

    def test_zero_visits_gives_zero_rate(self, db):
        from backend.services.analytics_service import get_dashboard_kpis
        result = get_dashboard_kpis(db)
        assert result['conversion_rate'] == 0.0


# ══════════════════════════════════════════
#  TESTS DE ENDPOINTS HTTP
# ══════════════════════════════════════════

class TestAnalyticsEndpoints:

    # ── /api/admin/analytics ──────────────────────────────────────────

    def test_analytics_endpoint_unauthorized(self, client, db):
        response = client.get("/api/admin/analytics")
        assert response.status_code == 401

    def test_analytics_endpoint_returns_200(self, client, db):
        token = _create_admin_session(db, "analytics_ep1@test.com")
        response = client.get("/api/admin/analytics", headers={"token": token})
        assert response.status_code == 200

    def test_analytics_endpoint_structure(self, client, db):
        token = _create_admin_session(db, "analytics_ep2@test.com")
        response = client.get("/api/admin/analytics", headers={"token": token})
        data = response.json()
        assert 'period' in data
        assert 'totals' in data
        assert 'six_sigma' in data
        assert 'sources' in data
        assert 'trend' in data

    def test_analytics_with_source_filter(self, client, db):
        token = _create_admin_session(db, "analytics_ep3@test.com")
        _seed_tracking(db, source="instagram", visits=5, clicks=2, bookings=1)
        response = client.get("/api/admin/analytics?source=instagram", headers={"token": token})
        assert response.status_code == 200

    def test_analytics_with_days_filter(self, client, db):
        token = _create_admin_session(db, "analytics_ep4@test.com")
        response = client.get("/api/admin/analytics?days=7", headers={"token": token})
        assert response.status_code == 200
        data = response.json()
        from datetime import date as date_type
        start = date_type.fromisoformat(data['period']['start'])
        end = date_type.fromisoformat(data['period']['end'])
        assert (end - start).days == 6

    def test_analytics_with_date_range(self, client, db):
        token = _create_admin_session(db, "analytics_ep5@test.com")
        response = client.get(
            "/api/admin/analytics?date_from=2026-01-01&date_to=2026-01-31",
            headers={"token": token}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['period']['start'] == "2026-01-01"

    def test_analytics_totals_with_data(self, client, db):
        token = _create_admin_session(db, "analytics_ep6@test.com")
        _seed_tracking(db, source="instagram", visits=8, clicks=4, bookings=2)
        response = client.get("/api/admin/analytics", headers={"token": token})
        data = response.json()
        assert data['totals']['visits'] == 8
        assert data['totals']['clicks'] == 4
        assert data['totals']['bookings'] == 2

    def test_analytics_sources_sorted_by_visits(self, client, db):
        token = _create_admin_session(db, "analytics_ep7@test.com")
        _seed_tracking(db, source="instagram", visits=20, clicks=5, bookings=2)
        _seed_tracking(db, source="youtube", visits=5, clicks=2, bookings=0)
        response = client.get("/api/admin/analytics", headers={"token": token})
        data = response.json()
        visits = [s['visits'] for s in data['sources']]
        assert visits == sorted(visits, reverse=True)

    # ── /api/tracking/funnel (auth requerida — analytics.py) ─────────

    def test_funnel_endpoint_unauthorized(self, client, db):
        response = client.get("/api/tracking/funnel")
        assert response.status_code == 401

    def test_funnel_endpoint_structure(self, client, db):
        token = _create_admin_session(db, "funnel_ep1@test.com")
        response = client.get("/api/tracking/funnel", headers={"token": token})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'visits' in data
        assert 'clicks' in data
        assert 'bookings' in data
        assert 'steps' in data

    def test_funnel_endpoint_steps_order(self, client, db):
        token = _create_admin_session(db, "funnel_ep2@test.com")
        _seed_tracking(db, source="instagram", visits=10, clicks=5, bookings=2)
        response = client.get("/api/tracking/funnel", headers={"token": token})
        data = response.json()
        steps = data['steps']
        assert len(steps) == 3
        assert steps[0]['name'] == "Visitas"
        assert steps[1]['name'] == "Clicks Calendly"
        assert steps[2]['name'] == "Citas agendadas"

    def test_funnel_steps_rates_coherent(self, client, db):
        token = _create_admin_session(db, "funnel_ep3@test.com")
        _seed_tracking(db, source="instagram", visits=10, clicks=5, bookings=2)
        response = client.get("/api/tracking/funnel", headers={"token": token})
        data = response.json()
        steps = data['steps']
        assert steps[0]['rate'] == 1.0
        assert 0 <= steps[1]['rate'] <= 1
        assert 0 <= steps[2]['rate'] <= 1

    def test_funnel_with_source_filter(self, client, db):
        token = _create_admin_session(db, "funnel_ep4@test.com")
        _seed_tracking(db, source="youtube", visits=8, clicks=4, bookings=1)
        _seed_tracking(db, source="instagram", visits=15, clicks=6, bookings=3)
        response = client.get("/api/tracking/funnel?source=youtube", headers={"token": token})
        assert response.status_code == 200
        data = response.json()
        assert data['visits'] == 8

    def test_funnel_conversion_rate(self, client, db):
        token = _create_admin_session(db, "funnel_ep5@test.com")
        _seed_tracking(db, source="instagram", visits=10, clicks=5, bookings=2)
        response = client.get("/api/tracking/funnel", headers={"token": token})
        data = response.json()
        # bookings/visits = 2/10 = 0.2
        assert abs(data['steps'][2]['rate'] - 0.2) < 0.001

    # ── /api/tracking/stats (auth requerida — analytics.py) ──────────

    def test_stats_endpoint_unauthorized(self, client, db):
        response = client.get("/api/tracking/stats")
        assert response.status_code == 401

    def test_stats_endpoint_structure(self, client, db):
        token = _create_admin_session(db, "stats_ep1@test.com")
        response = client.get("/api/tracking/stats", headers={"token": token})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'sources' in data
        assert isinstance(data['sources'], list)

    def test_stats_endpoint_source_fields(self, client, db):
        token = _create_admin_session(db, "stats_ep2@test.com")
        _seed_tracking(db, source="instagram", visits=5, clicks=2, bookings=1)
        response = client.get("/api/tracking/stats", headers={"token": token})
        data = response.json()
        if data['sources']:
            src = data['sources'][0]
            for field in ('source', 'visits', 'clicks', 'bookings', 'conv_rate'):
                assert field in src

    def test_stats_sorted_by_visits_desc(self, client, db):
        token = _create_admin_session(db, "stats_ep3@test.com")
        _seed_tracking(db, source="instagram", visits=20, clicks=5, bookings=2)
        _seed_tracking(db, source="youtube", visits=5, clicks=2, bookings=0)
        response = client.get("/api/tracking/stats", headers={"token": token})
        data = response.json()
        visits = [s['visits'] for s in data['sources']]
        assert visits == sorted(visits, reverse=True)

    # ── /api/admin/dashboard ──────────────────────────────────────────

    def test_dashboard_unauthorized(self, client, db):
        response = client.get("/api/admin/dashboard")
        assert response.status_code == 401

    def test_dashboard_returns_kpis(self, client, db):
        token = _create_admin_session(db, "dash_ep1@test.com")
        _seed_tracking(db, source="instagram", visits=10, clicks=4, bookings=2)
        response = client.get("/api/admin/dashboard", headers={"token": token})
        assert response.status_code == 200
        data = response.json()
        assert data['total_visits'] == 10
        assert data['total_clicks'] == 4
        assert data['total_bookings'] == 2
        assert abs(data['conversion_rate'] - 0.2) < 0.001


class TestSixSigmaMetrics:
    """Tests específicos para que las métricas Six Sigma sean coherentes."""

    def test_perfect_conversion_gives_high_sigma(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="instagram", visits=10, clicks=10, bookings=10)
        result = get_full_analytics(db)
        # 100 % conversión → DPMO≈0 → sigma 6
        assert result['six_sigma']['sigma'] == 6.0
        assert result['six_sigma']['dpmo'] == 0

    def test_zero_conversion_gives_low_sigma(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="instagram", visits=10, clicks=0, bookings=0)
        result = get_full_analytics(db)
        # 0 % conversión → DPMO=1_000_000 → sigma 1
        assert result['six_sigma']['sigma'] == 1.0
        assert result['six_sigma']['dpmo'] == 1_000_000

    def test_rty_is_product_of_y1_y2(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="instagram", visits=10, clicks=5, bookings=2)
        result = get_full_analytics(db)
        ss = result['six_sigma']
        expected_rty = round(ss['rty_y1'] * ss['rty_y2'], 6)
        assert abs(ss['rty'] - expected_rty) < 1e-4

    def test_ci_low_less_than_ci_high(self, db):
        from backend.services.analytics_service import get_full_analytics
        _seed_tracking(db, source="instagram", visits=50, clicks=20, bookings=5)
        result = get_full_analytics(db)
        ss = result['six_sigma']
        assert ss['ci_low'] <= ss['ci_high']

    def test_empty_db_six_sigma_safe(self, db):
        from backend.services.analytics_service import get_full_analytics
        result = get_full_analytics(db)
        ss = result['six_sigma']
        # No debe lanzar excepción y valores deben ser numéricos
        assert isinstance(ss['dpmo'], (int, float))
        assert isinstance(ss['sigma'], float)