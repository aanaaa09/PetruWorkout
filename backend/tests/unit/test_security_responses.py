# ==========================================
# backend/tests/unit/test_security_responses.py
# ==========================================
"""
Tests de seguridad y validación de respuestas HTTP:
  - 401 Unauthorized  → sin token / token inválido / token expirado
  - 403 Forbidden     → rol insuficiente (NEWSLETTER intentando acceder a ADMIN)
  - 400 / 422         → datos inválidos / campos requeridos ausentes
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────

def _create_admin(db, email="sec_admin@test.com", password="admin123"):
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    return usuario_crud.create(db, nombre="Admin", email=email,
                               password=password, tipo_usuario=TipoUsuario.ADMIN)


def _create_newsletter_user(db, email="sec_user@test.com", password="user123"):
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    return usuario_crud.create(db, nombre="User", email=email,
                               password=password, tipo_usuario=TipoUsuario.NEWSLETTER)


def _admin_token(client, db, email="sec_admin@test.com", password="admin123"):
    _create_admin(db, email, password)
    resp = client.post("/api/admin/login", json={"email": email, "password": password})
    return resp.json()["token"]


def _newsletter_token(db, email="sec_user@test.com"):
    from backend.crud.sesion import sesion_crud
    user = _create_newsletter_user(db, email)
    return sesion_crud.create(db, user.id).token


# ══════════════════════════════════════════════════════════════
#  1.  401 UNAUTHORIZED
#      Sin token, token vacío, token aleatorio, token expirado
# ══════════════════════════════════════════════════════════════

PROTECTED_GET_ENDPOINTS = [
    "/api/admin/dashboard",
    "/api/admin/users",
    "/api/admin/consultas",
    "/api/admin/bookings",
    "/api/admin/analytics",
    "/api/tracking/funnel",
    "/api/tracking/stats",
]

PROTECTED_DELETE_TEMPLATE = "/api/admin/users/9999"


class TestUnauthorized:
    """Todos los endpoints protegidos deben devolver 401 sin credenciales."""

    @pytest.mark.parametrize("endpoint", PROTECTED_GET_ENDPOINTS)
    def test_get_without_token_returns_401(self, client, db, endpoint):
        response = client.get(endpoint)
        assert response.status_code == 401, (
            f"{endpoint} debería devolver 401 sin token, devolvió {response.status_code}"
        )

    def test_delete_without_token_returns_401(self, client, db):
        response = client.delete(PROTECTED_DELETE_TEMPLATE)
        assert response.status_code == 401

    def test_send_email_without_token_returns_401(self, client, db):
        response = client.post(
            "/api/admin/send-email",
            data={"subject": "Test", "message": "Test", "send_to": "all"},
        )
        assert response.status_code == 401

    # ── Token vacío (header presente pero vacío) ──────────────
    @pytest.mark.parametrize("endpoint", PROTECTED_GET_ENDPOINTS)
    def test_get_with_empty_token_returns_401(self, client, db, endpoint):
        response = client.get(endpoint, headers={"token": ""})
        assert response.status_code == 401

    # ── Token aleatorio (no existe en BD) ────────────────────
    @pytest.mark.parametrize("endpoint", PROTECTED_GET_ENDPOINTS)
    def test_get_with_random_token_returns_401(self, client, db, endpoint):
        response = client.get(endpoint, headers={"token": "totalmente_falso_xyz_12345"})
        assert response.status_code == 401

    # ── Token expirado ────────────────────────────────────────
    def test_expired_session_token_returns_401(self, client, db):
        from backend.models.sesion import Sesion
        from backend.crud.sesion import sesion_crud

        admin = _create_admin(db, "expired_admin@test.com")
        sesion = sesion_crud.create(db, admin.id)

        # Forzar expiración
        sesion.fecha_expiracion = datetime.now() - timedelta(hours=1)
        db.commit()

        response = client.get("/api/admin/dashboard", headers={"token": sesion.token})
        assert response.status_code == 401

    # ── Token de calculadora no sirve para endpoints de admin ─
    def test_calculator_token_does_not_grant_admin_access(self, client, db):
        from backend.services.calculator_token_service import calculator_token_service

        _create_newsletter_user(db, "calc_sec@test.com")
        result = calculator_token_service.create_token_for_user(db, "calc_sec@test.com")
        calc_token = result["token"]

        response = client.get("/api/admin/dashboard", headers={"token": calc_token})
        # El token de calculadora no es un token de sesión → 401
        assert response.status_code == 401

    # ── Admin login con email inexistente ─────────────────────
    def test_admin_login_unknown_email_returns_401(self, client, db):
        response = client.post("/api/admin/login",
                               json={"email": "noexiste@test.com", "password": "pass123"})
        assert response.status_code == 401

    # ── Admin login con contraseña incorrecta ─────────────────
    def test_admin_login_wrong_password_returns_401(self, client, db):
        _create_admin(db, "wrongpass@test.com", "correctpass")
        response = client.post("/api/admin/login",
                               json={"email": "wrongpass@test.com", "password": "incorrecta"})
        assert response.status_code == 401

    # ── Calculadora sin header Authorization ──────────────────
    def test_calculator_without_auth_header_returns_401(self, client, db):
        response = client.post("/api/calculator/calculate", json={
            "gender": "male", "age": 25, "weight": 70,
            "height": 175, "activity_level": "moderate", "goal": "maintain",
        })
        assert response.status_code == 401

    # ── Calculadora con Bearer token inventado ────────────────
    def test_calculator_with_fake_bearer_token_returns_401(self, client, db):
        response = client.post(
            "/api/calculator/calculate",
            headers={"Authorization": "Bearer token_inventado_99999"},
            json={
                "gender": "male", "age": 25, "weight": 70,
                "height": 175, "activity_level": "moderate", "goal": "maintain",
            },
        )
        assert response.status_code == 401

    # ── Calculadora con scheme incorrecto ─────────────────────
    def test_calculator_with_wrong_scheme_returns_401(self, client, db):
        from backend.services.calculator_token_service import calculator_token_service

        _create_newsletter_user(db, "scheme@test.com")
        result = calculator_token_service.create_token_for_user(db, "scheme@test.com")
        token = result["token"]

        response = client.post(
            "/api/calculator/calculate",
            headers={"Authorization": f"Basic {token}"},   # debe ser Bearer
            json={
                "gender": "male", "age": 25, "weight": 70,
                "height": 175, "activity_level": "moderate", "goal": "maintain",
            },
        )
        assert response.status_code == 401


# ══════════════════════════════════════════════════════════════
#  2.  403 FORBIDDEN
#      Token válido pero rol insuficiente (NEWSLETTER → endpoints ADMIN)
# ══════════════════════════════════════════════════════════════

class TestForbidden:
    """Usuario NEWSLETTER con sesión válida no puede acceder a endpoints de admin."""

    def _newsletter_headers(self, db, email="forbidden_user@test.com"):
        token = _newsletter_token(db, email)
        return {"token": token}

    @pytest.mark.parametrize("endpoint", PROTECTED_GET_ENDPOINTS)
    def test_newsletter_user_gets_403_on_admin_endpoints(self, client, db, endpoint):
        headers = self._newsletter_headers(db, f"forbidden_{endpoint.replace('/', '_')}@test.com")
        response = client.get(endpoint, headers=headers)
        assert response.status_code == 403, (
            f"Usuario NEWSLETTER en {endpoint} debería obtener 403, obtuvo {response.status_code}"
        )

    def test_newsletter_user_cannot_delete_users(self, client, db):
        headers = self._newsletter_headers(db, "forbidden_del@test.com")
        # Crear un usuario para intentar borrarlo
        victim = _create_newsletter_user(db, "victim@test.com")
        response = client.delete(f"/api/admin/users/{victim.id}", headers=headers)
        assert response.status_code == 403

    def test_newsletter_user_cannot_send_emails(self, client, db):
        headers = self._newsletter_headers(db, "forbidden_email@test.com")
        response = client.post(
            "/api/admin/send-email",
            headers=headers,
            data={"subject": "Test", "message": "Test", "send_to": "all"},
        )
        assert response.status_code == 403

    def test_admin_cannot_delete_another_admin(self, client, db):
        """Admin con token válido → 403 al intentar borrar otro admin."""
        token = _admin_token(client, db, "admin_del_admin@test.com")
        other_admin = _create_admin(db, "target_admin@test.com")
        response = client.delete(f"/api/admin/users/{other_admin.id}",
                                 headers={"token": token})
        assert response.status_code == 403

    def test_admin_cannot_self_delete(self, client, db):
        """Admin con token válido → 403 al intentar borrarse a sí mismo."""
        admin = _create_admin(db, "self_del@test.com")
        from backend.crud.sesion import sesion_crud
        token = sesion_crud.create(db, admin.id).token
        response = client.delete(f"/api/admin/users/{admin.id}",
                                 headers={"token": token})
        assert response.status_code == 403

    def test_non_admin_login_attempt_returns_401_not_403(self, client, db):
        """
        Un usuario NEWSLETTER que intenta hacer login como admin debe recibir 401
        (credenciales inválidas para ese rol), no 403.
        """
        _create_newsletter_user(db, "nl_login@test.com", "nl123")
        response = client.post("/api/admin/login",
                               json={"email": "nl_login@test.com", "password": "nl123"})
        assert response.status_code == 401


# ══════════════════════════════════════════════════════════════
#  3.  400 / 422 BAD REQUEST — datos inválidos o campos ausentes
# ══════════════════════════════════════════════════════════════

class TestBadRequest:
    """Validación de payloads incorrectos en todos los endpoints."""

    # ── /api/admin/login ──────────────────────────────────────

    def test_login_missing_email_returns_422(self, client, db):
        response = client.post("/api/admin/login", json={"password": "admin123"})
        assert response.status_code == 422

    def test_login_missing_password_returns_422(self, client, db):
        response = client.post("/api/admin/login", json={"email": "admin@test.com"})
        assert response.status_code == 422

    def test_login_empty_body_returns_422(self, client, db):
        response = client.post("/api/admin/login", json={})
        assert response.status_code == 422

    def test_login_malformed_email_returns_422(self, client, db):
        response = client.post("/api/admin/login",
                               json={"email": "not-an-email", "password": "admin123"})
        assert response.status_code == 422

    # ── /api/admin/send-email ─────────────────────────────────

    def test_send_email_invalid_send_to_returns_400(self, client, db):
        token = _admin_token(client, db, "send_bad1@test.com")
        response = client.post(
            "/api/admin/send-email",
            headers={"token": token},
            data={"subject": "S", "message": "M", "send_to": "INVALID_VALUE"},
        )
        assert response.status_code == 400

    def test_send_email_selected_without_ids_returns_400(self, client, db):
        token = _admin_token(client, db, "send_bad2@test.com")
        response = client.post(
            "/api/admin/send-email",
            headers={"token": token},
            data={"subject": "S", "message": "M", "send_to": "selected"},
            # selected_ids ausente
        )
        assert response.status_code == 400

    def test_send_email_no_recipients_returns_400(self, client, db):
        """send_to='all' pero no hay usuarios newsletter → 400."""
        token = _admin_token(client, db, "send_bad3@test.com")
        response = client.post(
            "/api/admin/send-email",
            headers={"token": token},
            data={"subject": "S", "message": "M", "send_to": "all"},
        )
        assert response.status_code == 400

    # ── /api/consultas/enviar ─────────────────────────────────

    def test_consulta_missing_nombre_returns_422(self, client, db):
        response = client.post("/api/consultas/enviar", json={
            "email": "a@b.com", "asunto": "Test", "mensaje": "Hola"
        })
        assert response.status_code == 422

    def test_consulta_invalid_email_returns_422(self, client, db):
        response = client.post("/api/consultas/enviar", json={
            "nombre": "Pepe", "email": "no-email", "asunto": "Test", "mensaje": "Hola"
        })
        assert response.status_code == 422

    def test_consulta_empty_body_returns_422(self, client, db):
        response = client.post("/api/consultas/enviar", json={})
        assert response.status_code == 422

    # ── /api/lead/register ────────────────────────────────────

    def test_lead_register_missing_email_returns_422(self, client, db):
        response = client.post("/api/lead/register", json={})
        assert response.status_code == 422

    def test_lead_register_invalid_email_returns_422(self, client, db):
        response = client.post("/api/lead/register", json={"email": "@@@@"})
        assert response.status_code == 422

    def test_lead_register_empty_email_returns_422(self, client, db):
        response = client.post("/api/lead/register", json={"email": ""})
        assert response.status_code == 422

    # ── /api/tracking/visit ───────────────────────────────────

    def test_visit_missing_session_id_returns_422(self, client, db):
        response = client.post("/api/tracking/visit", json={
            "traffic_source": "instagram"
        })
        assert response.status_code == 422

    def test_visit_missing_traffic_source_returns_422(self, client, db):
        response = client.post("/api/tracking/visit", json={
            "session_id": "abc123"
        })
        assert response.status_code == 422

    def test_visit_empty_body_returns_422(self, client, db):
        response = client.post("/api/tracking/visit", json={})
        assert response.status_code == 422

    # ── /api/tracking/click ───────────────────────────────────

    def test_click_missing_session_id_returns_422(self, client, db):
        response = client.post("/api/tracking/click", json={
            "traffic_source": "instagram"
        })
        assert response.status_code == 422

    def test_click_missing_traffic_source_returns_422(self, client, db):
        response = client.post("/api/tracking/click", json={
            "session_id": "abc123"
        })
        assert response.status_code == 422

    # ── /api/calculator/calculate ─────────────────────────────

    def test_calculator_missing_gender_returns_422(self, client, db):
        from backend.services.calculator_token_service import calculator_token_service
        _create_newsletter_user(db, "calc_bad1@test.com")
        result = calculator_token_service.create_token_for_user(db, "calc_bad1@test.com")
        token = result["token"]

        response = client.post(
            "/api/calculator/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json={"age": 25, "weight": 70, "height": 175,
                  "activity_level": "moderate", "goal": "maintain"},
        )
        assert response.status_code == 422

    def test_calculator_invalid_activity_level_returns_422(self, client, db):
        from backend.services.calculator_token_service import calculator_token_service
        _create_newsletter_user(db, "calc_bad2@test.com")
        result = calculator_token_service.create_token_for_user(db, "calc_bad2@test.com")
        token = result["token"]

        response = client.post(
            "/api/calculator/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json={"gender": "male", "age": 25, "weight": 70, "height": 175,
                  "activity_level": "INVALID", "goal": "maintain"},
        )
        assert response.status_code == 422

    def test_calculator_age_below_minimum_returns_422(self, client, db):
        from backend.services.calculator_token_service import calculator_token_service
        _create_newsletter_user(db, "calc_bad3@test.com")
        result = calculator_token_service.create_token_for_user(db, "calc_bad3@test.com")
        token = result["token"]

        response = client.post(
            "/api/calculator/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json={"gender": "male", "age": 5,   # mínimo es 15
                  "weight": 70, "height": 175,
                  "activity_level": "moderate", "goal": "maintain"},
        )
        assert response.status_code == 422

    def test_calculator_weight_out_of_range_returns_422(self, client, db):
        from backend.services.calculator_token_service import calculator_token_service
        _create_newsletter_user(db, "calc_bad4@test.com")
        result = calculator_token_service.create_token_for_user(db, "calc_bad4@test.com")
        token = result["token"]

        response = client.post(
            "/api/calculator/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json={"gender": "female", "age": 25, "weight": 5,  # mínimo es 30
                  "height": 165, "activity_level": "light", "goal": "lose"},
        )
        assert response.status_code == 422

    def test_calculator_invalid_goal_returns_422(self, client, db):
        from backend.services.calculator_token_service import calculator_token_service
        _create_newsletter_user(db, "calc_bad5@test.com")
        result = calculator_token_service.create_token_for_user(db, "calc_bad5@test.com")
        token = result["token"]

        response = client.post(
            "/api/calculator/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json={"gender": "male", "age": 25, "weight": 70, "height": 175,
                  "activity_level": "moderate", "goal": "INVALID_GOAL"},
        )
        assert response.status_code == 422

    # ── /api/auth/newsletter/registro ────────────────────────

    def test_newsletter_registro_missing_email_returns_422(self, client, db):
        response = client.post("/api/auth/newsletter/registro", json={
            "nombre": "Alicia", "password": "pass123"
        })
        assert response.status_code == 422

    def test_newsletter_registro_short_password_returns_400(self, client, db):
        """Contraseña de menos de 6 caracteres → lógica de negocio → 400."""
        response = client.post("/api/auth/newsletter/registro", json={
            "nombre": "Alicia", "email": "alicia@test.com", "password": "abc"
        })
        assert response.status_code == 400

    def test_newsletter_registro_short_name_returns_400(self, client, db):
        response = client.post("/api/auth/newsletter/registro", json={
            "nombre": "A", "email": "short@test.com", "password": "pass123"
        })
        assert response.status_code == 400

    def test_newsletter_registro_duplicate_email_returns_400(self, client, db):
        client.post("/api/auth/newsletter/registro", json={
            "nombre": "Alicia", "email": "dup@test.com", "password": "pass123"
        })
        response = client.post("/api/auth/newsletter/registro", json={
            "nombre": "Alicia2", "email": "dup@test.com", "password": "pass456"
        })
        assert response.status_code == 400

    # ── /api/admin/users paginación ───────────────────────────

    def test_admin_delete_nonexistent_user_returns_403(self, client, db):
        """ID que no existe → 403 con mensaje claro."""
        token = _admin_token(client, db, "del_ghost@test.com")
        response = client.delete("/api/admin/users/999999",
                                 headers={"token": token})
        assert response.status_code == 403