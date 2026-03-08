# ==========================================
# backend/tests/unit/test_button_distribution.py
# ==========================================
"""
Tests para la distribución de clicks por botón (button_location).

Cubre:
  - group_by_button (analytics_crud)
  - campo 'buttons' en get_full_analytics (analytics_service)
  - endpoint GET /api/admin/analytics  → sección 'buttons'
  - filtros: por fuente, por botón concreto, rango de fechas
  - exclusión de fuentes no conocidas (direct, internal, …)
  - exclusión de botones no conocidos
  - ordenación por clicks descendente
  - pct suma ~ 1.0 cuando hay datos
"""
import pytest
from datetime import datetime, timedelta, date


# ─────────────────────────────────────────────────────────────
#  Constantes sincronizadas con analytics_crud.py
# ─────────────────────────────────────────────────────────────
KNOWN_SOURCES = ("instagram", "organic_search", "youtube", "facebook", "linkedin")
KNOWN_BUTTONS = (
    "calculator-section",
    "results-section",
    "services-section",
    "video-section",
    "full-footer",
    "full-navbar",
    "simple-footer",
)


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────

def _yesterday():
    return date.today() - timedelta(days=1)


def _move_to_yesterday(db, obj):
    obj.fecha = _yesterday()
    if hasattr(obj, "timestamp"):
        obj.timestamp = datetime.now() - timedelta(days=1)
    db.commit()
    return obj


def _create_click(db, session_id, source, button_location):
    """Crea un CalendlyClick con fuente y botón dados, datado ayer."""
    from backend.crud.tracking import tracking_crud
    click = tracking_crud.create_calendly_click(
        db,
        session_id=session_id,
        traffic_source=source,
        button_id=f"btn_{button_location}",
        button_location=button_location,
    )
    return _move_to_yesterday(db, click)


def _admin_session(db, email="btn_admin@test.com"):
    from backend.crud.usuario import usuario_crud
    from backend.crud.sesion import sesion_crud
    from backend.models.usuario import TipoUsuario
    admin = usuario_crud.create(db, nombre="Admin", email=email,
                                password="admin123", tipo_usuario=TipoUsuario.ADMIN)
    return sesion_crud.create(db, admin.id).token


# ══════════════════════════════════════════════════════════════
#  A.  group_by_button (analytics_crud — nivel de acceso a BD)
# ══════════════════════════════════════════════════════════════

class TestGroupByButton:

    def test_empty_db_returns_empty_dict(self, db):
        from backend.crud.analytics_crud import group_by_button, get_date_range
        start, end = get_date_range(30, None, None)
        result = group_by_button(db, start, end)
        assert result == {}

    def test_counts_clicks_per_button(self, db):
        from backend.crud.analytics_crud import group_by_button, get_date_range

        _create_click(db, "s1", "instagram", "full-navbar")
        _create_click(db, "s2", "instagram", "full-navbar")
        _create_click(db, "s3", "youtube",   "calculator-section")

        start, end = get_date_range(30, None, None)
        result = group_by_button(db, start, end)

        assert result.get("full-navbar") == 2
        assert result.get("calculator-section") == 1

    def test_excludes_unknown_buttons(self, db):
        from backend.crud.analytics_crud import group_by_button, get_date_range

        # Botón desconocido: no debe aparecer en el resultado
        _create_click(db, "s_unk", "instagram", "unknown-widget")

        start, end = get_date_range(30, None, None)
        result = group_by_button(db, start, end)

        assert "unknown-widget" not in result

    def test_excludes_unknown_traffic_sources(self, db):
        from backend.crud.analytics_crud import group_by_button, get_date_range

        # Fuente desconocida: el click no debe contar
        _create_click(db, "s_dir", "direct", "full-navbar")

        start, end = get_date_range(30, None, None)
        result = group_by_button(db, start, end)

        # Si solo hay ese click, el resultado debe estar vacío (fuente excluida)
        assert result.get("full-navbar", 0) == 0

    def test_source_filter_narrows_results(self, db):
        from backend.crud.analytics_crud import group_by_button, get_date_range

        _create_click(db, "sg1", "instagram", "full-footer")
        _create_click(db, "sg2", "youtube",   "full-footer")

        start, end = get_date_range(30, None, None)

        # Solo instagram
        result_ig = group_by_button(db, start, end, source="instagram")
        result_yt = group_by_button(db, start, end, source="youtube")

        assert result_ig.get("full-footer") == 1
        assert result_yt.get("full-footer") == 1

    def test_all_known_buttons_can_appear(self, db):
        from backend.crud.analytics_crud import group_by_button, get_date_range

        for i, btn in enumerate(KNOWN_BUTTONS):
            _create_click(db, f"all_btn_{i}", "instagram", btn)

        start, end = get_date_range(30, None, None)
        result = group_by_button(db, start, end)

        for btn in KNOWN_BUTTONS:
            assert btn in result, f"Botón conocido '{btn}' no aparece en el resultado"

    def test_date_range_filters_old_clicks(self, db):
        from backend.crud.analytics_crud import group_by_button
        from datetime import date as date_type

        # Click de ayer (dentro del rango)
        _create_click(db, "old1", "instagram", "full-navbar")

        # Rango: solo hace 1 día (ayer)
        start = _yesterday()
        end   = _yesterday()
        result_in_range = group_by_button(db, start, end)
        assert result_in_range.get("full-navbar", 0) >= 1

        # Rango: hace 60–31 días (click de ayer queda fuera)
        far_end   = _yesterday() - timedelta(days=31)
        far_start = _yesterday() - timedelta(days=60)
        result_out_range = group_by_button(db, far_start, far_end)
        assert result_out_range.get("full-navbar", 0) == 0


# ══════════════════════════════════════════════════════════════
#  B.  get_full_analytics → sección 'buttons'
# ══════════════════════════════════════════════════════════════

class TestFullAnalyticsButtons:

    def test_buttons_key_present_in_response(self, db):
        from backend.services.analytics_service import get_full_analytics
        result = get_full_analytics(db)
        assert "buttons" in result

    def test_buttons_empty_when_no_clicks(self, db):
        from backend.services.analytics_service import get_full_analytics
        result = get_full_analytics(db)
        assert result["buttons"] == []

    def test_buttons_has_required_fields(self, db):
        from backend.services.analytics_service import get_full_analytics
        _create_click(db, "bf1", "instagram", "full-navbar")
        result = get_full_analytics(db)
        btn = result["buttons"][0]
        assert "button" in btn
        assert "clicks" in btn
        assert "pct"    in btn

    def test_buttons_sorted_by_clicks_descending(self, db):
        from backend.services.analytics_service import get_full_analytics

        # 5 clicks en full-navbar, 2 en calculator-section, 1 en results-section
        for i in range(5):
            _create_click(db, f"bs_nav_{i}", "instagram", "full-navbar")
        for i in range(2):
            _create_click(db, f"bs_calc_{i}", "youtube", "calculator-section")
        _create_click(db, "bs_res_0", "instagram", "results-section")

        result = get_full_analytics(db)
        buttons = result["buttons"]

        clicks_list = [b["clicks"] for b in buttons]
        assert clicks_list == sorted(clicks_list, reverse=True), (
            "Los botones deben ordenarse por clicks de mayor a menor"
        )

    def test_buttons_pct_sums_to_one(self, db):
        from backend.services.analytics_service import get_full_analytics

        _create_click(db, "pct1", "instagram", "full-navbar")
        _create_click(db, "pct2", "youtube",   "calculator-section")
        _create_click(db, "pct3", "facebook",  "full-footer")

        result = get_full_analytics(db)
        total_pct = sum(b["pct"] for b in result["buttons"])
        assert abs(total_pct - 1.0) < 1e-4, (
            f"La suma de pct debería ser ~1.0, obtuvo {total_pct}"
        )

    def test_buttons_pct_proportional(self, db):
        from backend.services.analytics_service import get_full_analytics

        # 3 clics en full-navbar (75 %), 1 en full-footer (25 %)
        for i in range(3):
            _create_click(db, f"prop_nav_{i}", "instagram", "full-navbar")
        _create_click(db, "prop_foot_0", "instagram", "full-footer")

        result = get_full_analytics(db)
        btn_map = {b["button"]: b for b in result["buttons"]}

        assert abs(btn_map["full-navbar"]["pct"]  - 0.75) < 1e-4
        assert abs(btn_map["full-footer"]["pct"]  - 0.25) < 1e-4

    def test_buttons_single_button_has_pct_one(self, db):
        from backend.services.analytics_service import get_full_analytics

        _create_click(db, "sole1", "instagram", "services-section")

        result = get_full_analytics(db)
        assert len(result["buttons"]) == 1
        assert abs(result["buttons"][0]["pct"] - 1.0) < 1e-4

    def test_buttons_only_known_buttons_appear(self, db):
        from backend.services.analytics_service import get_full_analytics

        _create_click(db, "unk_s1", "instagram", "unknown-widget-xyz")
        _create_click(db, "knw_s2", "youtube",   "full-navbar")

        result = get_full_analytics(db)
        btn_names = [b["button"] for b in result["buttons"]]
        assert "unknown-widget-xyz" not in btn_names
        assert "full-navbar" in btn_names

    def test_buttons_filtered_by_source(self, db):
        """
        Con source='instagram', 'buttons' muestra solo los clicks
        de esa fuente (group_by_button recibe el source y filtra).
        Sin filtro devuelve la distribución completa.
        """
        from backend.services.analytics_service import get_full_analytics

        _create_click(db, "naf_ig1", "instagram", "full-navbar")
        _create_click(db, "naf_yt1", "youtube",   "calculator-section")

        # Sin filtro: dos botones (uno por fuente)
        result_all = get_full_analytics(db)
        assert len(result_all["buttons"]) == 2

        # Con filtro instagram: solo aparece el botón de instagram
        result_ig = get_full_analytics(db, source="instagram")
        btn_names_ig = [b["button"] for b in result_ig["buttons"]]
        assert "full-navbar" in btn_names_ig
        assert "calculator-section" not in btn_names_ig

        # Con filtro youtube: solo aparece el botón de youtube
        result_yt = get_full_analytics(db, source="youtube")
        btn_names_yt = [b["button"] for b in result_yt["buttons"]]
        assert "calculator-section" in btn_names_yt
        assert "full-navbar" not in btn_names_yt

    def test_buttons_counts_match_group_by_button(self, db):
        """Consistencia entre group_by_button (crud) y buttons (service)."""
        from backend.services.analytics_service import get_full_analytics
        from backend.crud.analytics_crud import group_by_button, get_date_range

        _create_click(db, "cons1", "instagram",      "video-section")
        _create_click(db, "cons2", "youtube",         "video-section")
        _create_click(db, "cons3", "organic_search",  "full-navbar")

        start, end = get_date_range(30, None, None)
        crud_map = group_by_button(db, start, end)

        result = get_full_analytics(db)
        svc_map = {b["button"]: b["clicks"] for b in result["buttons"]}

        for btn, cnt in crud_map.items():
            assert svc_map.get(btn) == cnt, (
                f"Discrepancia en botón '{btn}': crud={cnt}, service={svc_map.get(btn)}"
            )


# ══════════════════════════════════════════════════════════════
#  C.  Endpoint HTTP GET /api/admin/analytics → sección 'buttons'
# ══════════════════════════════════════════════════════════════

class TestAnalyticsEndpointButtons:

    def test_buttons_present_in_endpoint_response(self, client, db):
        token = _admin_session(db, "ep_btn1@test.com")
        response = client.get("/api/admin/analytics", headers={"token": token})
        assert response.status_code == 200
        assert "buttons" in response.json()

    def test_buttons_empty_list_when_no_data(self, client, db):
        token = _admin_session(db, "ep_btn2@test.com")
        response = client.get("/api/admin/analytics", headers={"token": token})
        assert response.json()["buttons"] == []

    def test_buttons_populated_after_clicks(self, client, db):
        token = _admin_session(db, "ep_btn3@test.com")
        _create_click(db, "ep_c1", "instagram", "full-navbar")
        _create_click(db, "ep_c2", "youtube",   "results-section")

        response = client.get("/api/admin/analytics", headers={"token": token})
        buttons = response.json()["buttons"]
        assert len(buttons) == 2
        btn_names = [b["button"] for b in buttons]
        assert "full-navbar"     in btn_names
        assert "results-section" in btn_names

    def test_buttons_sorted_desc_in_response(self, client, db):
        token = _admin_session(db, "ep_btn4@test.com")
        for i in range(4):
            _create_click(db, f"ep_nav_{i}", "instagram", "full-navbar")
        _create_click(db, "ep_cal_0", "youtube", "calculator-section")

        response = client.get("/api/admin/analytics", headers={"token": token})
        buttons = response.json()["buttons"]
        clicks = [b["clicks"] for b in buttons]
        assert clicks == sorted(clicks, reverse=True)

    def test_buttons_pct_field_between_0_and_1(self, client, db):
        token = _admin_session(db, "ep_btn5@test.com")
        for btn in ("full-navbar", "full-footer", "video-section"):
            _create_click(db, f"ep_pct_{btn}", "instagram", btn)

        response = client.get("/api/admin/analytics", headers={"token": token})
        for btn in response.json()["buttons"]:
            assert 0.0 <= btn["pct"] <= 1.0, (
                f"pct fuera de rango [0,1]: {btn}"
            )

    def test_buttons_with_source_query_param_filters_correctly(self, client, db):
        """?source=instagram devuelve solo los botones clicados desde instagram."""
        token = _admin_session(db, "ep_btn6@test.com")
        _create_click(db, "ep_src1", "instagram", "full-navbar")
        _create_click(db, "ep_src2", "youtube",   "full-footer")

        response = client.get("/api/admin/analytics?source=instagram",
                              headers={"token": token})
        assert response.status_code == 200
        data = response.json()
        assert "buttons" in data
        btn_names = [b["button"] for b in data["buttons"]]
        assert "full-navbar" in btn_names
        assert "full-footer" not in btn_names

    def test_buttons_with_button_query_param(self, client, db):
        """?button=full-navbar filtra clicks de ese botón en totales, no en 'buttons'."""
        token = _admin_session(db, "ep_btn7@test.com")
        _create_click(db, "ep_filt1", "instagram", "full-navbar")
        _create_click(db, "ep_filt2", "instagram", "full-footer")

        response = client.get("/api/admin/analytics?button=full-navbar",
                              headers={"token": token})
        data = response.json()

        # totals['clicks'] debe reflejar SOLO el botón filtrado
        assert data["totals"]["clicks"] == 1
        # buttons sigue mostrando la distribución completa
        btn_names = [b["button"] for b in data["buttons"]]
        assert "full-footer" in btn_names

    def test_buttons_requires_auth(self, client, db):
        """Sin token → 401, no filtramos la sección 'buttons'."""
        response = client.get("/api/admin/analytics")
        assert response.status_code == 401

    def test_buttons_forbidden_for_newsletter_user(self, client, db):
        from backend.crud.sesion import sesion_crud
        user = _create_click  # reutilizamos helper de fixture
        # Crear usuario newsletter y su sesión
        from backend.crud.usuario import usuario_crud
        from backend.models.usuario import TipoUsuario
        nl = usuario_crud.create(db, nombre="NL", email="nl_btn@test.com",
                                 password="nl123", tipo_usuario=TipoUsuario.NEWSLETTER)
        token = sesion_crud.create(db, nl.id).token

        response = client.get("/api/admin/analytics", headers={"token": token})
        assert response.status_code == 403

    def test_buttons_with_date_range(self, client, db):
        """?date_from / ?date_to funciona y 'buttons' aparece en respuesta."""
        token = _admin_session(db, "ep_btn8@test.com")
        _create_click(db, "ep_dr1", "instagram", "full-navbar")

        yesterday = _yesterday().isoformat()
        response = client.get(
            f"/api/admin/analytics?date_from={yesterday}&date_to={yesterday}",
            headers={"token": token}
        )
        assert response.status_code == 200
        assert "buttons" in response.json()

    def test_buttons_clicks_match_totals_clicks_without_button_filter(self, client, db):
        """
        Sin filtro de botón, la suma de clicks en 'buttons' debe coincidir
        con totals['clicks'] (ambos usan los mismos KNOWN_SOURCES y KNOWN_BUTTONS).
        """
        token = _admin_session(db, "ep_btn9@test.com")
        _create_click(db, "ep_sum1", "instagram", "full-navbar")
        _create_click(db, "ep_sum2", "youtube",   "full-footer")
        _create_click(db, "ep_sum3", "facebook",  "video-section")

        response = client.get("/api/admin/analytics", headers={"token": token})
        data = response.json()

        total_in_buttons = sum(b["clicks"] for b in data["buttons"])
        total_clicks     = data["totals"]["clicks"]
        assert total_in_buttons == total_clicks


# ══════════════════════════════════════════════════════════════
#  D.  Tests de todos los botones conocidos individualmente
# ══════════════════════════════════════════════════════════════

class TestEachKnownButton:
    """Un test por botón conocido para asegurar que cada uno se registra bien."""

    @pytest.mark.parametrize("button_location", KNOWN_BUTTONS)
    def test_known_button_appears_in_analytics(self, client, db, button_location):
        import uuid
        token = _admin_session(db, f"btn_{uuid.uuid4().hex[:8]}@test.com")
        _create_click(db, f"each_{button_location}", "instagram", button_location)

        response = client.get("/api/admin/analytics", headers={"token": token})
        assert response.status_code == 200
        btn_names = [b["button"] for b in response.json()["buttons"]]
        assert button_location in btn_names, (
            f"El botón '{button_location}' no aparece en la respuesta"
        )

    @pytest.mark.parametrize("button_location", KNOWN_BUTTONS)
    def test_known_button_group_by_button_crud(self, db, button_location):
        from backend.crud.analytics_crud import group_by_button, get_date_range
        _create_click(db, f"crud_{button_location}", "youtube", button_location)

        start, end = get_date_range(30, None, None)
        result = group_by_button(db, start, end)
        assert result.get(button_location, 0) >= 1