# ==========================================
# backend/tests/unit/test_admin_panel.py
# ==========================================
"""Tests unitarios completos para el panel de administración"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


def test_admin_login_successful(client, db):
    """Test login exitoso de administrador"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # Crear admin
    usuario_crud.create(
        db,
        nombre="Admin Test",
        email="admin@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    response = client.post("/api/admin/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })

    assert response.status_code == 200
    data = response.json()

    assert data['success'] is True
    assert 'token' in data
    assert 'admin' in data
    assert data['admin']['email'] == "admin@test.com"


def test_admin_login_wrong_password(client, db):
    """Test login con contraseña incorrecta"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    usuario_crud.create(
        db,
        nombre="Admin Test",
        email="admin2@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    response = client.post("/api/admin/login", json={
        "email": "admin2@test.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401


def test_admin_login_non_admin_user(client, db):
    """Test login con usuario no administrador"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # Crear usuario normal
    usuario_crud.create(
        db,
        nombre="Normal User",
        email="user@test.com",
        password="user123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    response = client.post("/api/admin/login", json={
        "email": "user@test.com",
        "password": "user123"
    })

    assert response.status_code == 401


def test_admin_dashboard_stats(client, db):
    """Test obtención de estadísticas del dashboard"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud

    # Crear admin y obtener token
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin3@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Crear algunos usuarios newsletter
    for i in range(5):
        usuario_crud.create(
            db,
            nombre=f"User {i}",
            email=f"user{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    # Obtener dashboard
    response = client.get(
        "/api/admin/dashboard",
        headers={"token": sesion.token}
    )

    assert response.status_code == 200
    data = response.json()

    assert 'total_usuarios_newsletter' in data
    assert 'total_consultas' in data
    assert 'total_visitas' in data
    assert 'visitas_unicas' in data
    assert 'total_clicks_calendly' in data
    assert 'total_bookings' in data
    assert 'tasa_conversion' in data
    assert 'trafico_por_fuente' in data

    assert data['total_usuarios_newsletter'] >= 5


def test_admin_dashboard_unauthorized(client, db):
    """Test acceso a dashboard sin autenticación"""
    response = client.get("/api/admin/dashboard")

    assert response.status_code == 401


def test_admin_dashboard_invalid_token(client, db):
    """Test acceso a dashboard con token inválido"""
    response = client.get(
        "/api/admin/dashboard",
        headers={"token": "invalid_token_12345"}
    )

    assert response.status_code == 401


def test_admin_get_users_list(client, db):
    """Test listar usuarios"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin4@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Crear usuarios
    for i in range(3):
        usuario_crud.create(
            db,
            nombre=f"User {i}",
            email=f"list{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    response = client.get(
        "/api/admin/users",
        headers={"token": sesion.token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data['success'] is True
    assert 'total' in data
    assert 'usuarios' in data
    assert data['total'] >= 3


def test_admin_get_users_filtered_by_type(client, db):
    """Test listar usuarios filtrados por tipo"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin5@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Crear usuarios newsletter
    for i in range(3):
        usuario_crud.create(
            db,
            nombre=f"Newsletter {i}",
            email=f"newsletter{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    # Filtrar solo newsletter
    response = client.get(
        "/api/admin/users?tipo=newsletter",
        headers={"token": sesion.token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data['total'] >= 3
    # Verificar que todos son newsletter
    for usuario in data['usuarios']:
        assert usuario['tipo_usuario'] == 'newsletter'


def test_admin_get_users_pagination(client, db):
    """Test paginación de usuarios"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin6@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Crear 10 usuarios
    for i in range(10):
        usuario_crud.create(
            db,
            nombre=f"Page User {i}",
            email=f"page{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    # Primera página (5 usuarios)
    response1 = client.get(
        "/api/admin/users?limit=5&offset=0",
        headers={"token": sesion.token}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1['usuarios']) <= 5

    # Segunda página
    response2 = client.get(
        "/api/admin/users?limit=5&offset=5",
        headers={"token": sesion.token}
    )

    assert response2.status_code == 200
    data2 = response2.json()

    # Los usuarios deben ser diferentes
    ids_page1 = [u['id'] for u in data1['usuarios']]
    ids_page2 = [u['id'] for u in data2['usuarios']]
    assert not any(id in ids_page2 for id in ids_page1)


def test_admin_delete_user_newsletter(client, db):
    """Test eliminar usuario tipo NEWSLETTER"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin7@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Crear usuario a eliminar
    user = usuario_crud.create(
        db,
        nombre="To Delete",
        email="delete@test.com",
        password="test123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )
    user_id = user.id

    # Eliminar
    response = client.delete(
        f"/api/admin/users/{user_id}",
        headers={"token": sesion.token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data['deleted'] is True
    assert data['user_id'] == user_id

    # Verificar que fue eliminado
    deleted_user = usuario_crud.get_by_id(db, user_id)
    assert deleted_user is None


def test_admin_delete_user_cannot_delete_admin(client, db):
    """Test que no se puede eliminar un usuario ADMIN"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud

    # Crear dos admins
    admin1 = usuario_crud.create(
        db,
        nombre="Admin 1",
        email="admin8@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin1.id)

    admin2 = usuario_crud.create(
        db,
        nombre="Admin 2",
        email="admin9@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    # Intentar eliminar el otro admin
    response = client.delete(
        f"/api/admin/users/{admin2.id}",
        headers={"token": sesion.token}
    )

    assert response.status_code == 403  # Forbidden


def test_admin_delete_user_cannot_self_delete(client, db):
    """Test que un admin no puede eliminarse a sí mismo"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin10@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Intentar auto-eliminarse
    response = client.delete(
        f"/api/admin/users/{admin.id}",
        headers={"token": sesion.token}
    )

    assert response.status_code == 403


def test_admin_get_consultas_list(client, db):
    """Test listar consultas"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud
    from backend.models.consulta import Consulta

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin11@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Crear consultas
    for i in range(3):
        consulta = Consulta(
            nombre=f"User {i}",
            email=f"consult{i}@test.com",
            asunto=f"Asunto {i}",
            mensaje=f"Mensaje {i}"
        )
        db.add(consulta)
    db.commit()

    response = client.get(
        "/api/admin/consultas",
        headers={"token": sesion.token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data['success'] is True
    assert data['total'] >= 3
    assert len(data['consultas']) >= 3


def test_admin_get_bookings_list(client, db):
    """Test listar bookings de Calendly"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud
    from backend.crud.tracking import tracking_crud

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin12@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Crear bookings
    for i in range(3):
        tracking_crud.create_calendly_booking(
            db,
            calendly_event_id=f"evt_{i}",
            invitee_email=f"booking{i}@test.com",
            invitee_name=f"Booking {i}",
            event_start_time=datetime.now(),
            booking_timestamp=datetime.now(),
            session_id=f"session_{i}",
            traffic_source="test"
        )

    response = client.get(
        "/api/admin/bookings",
        headers={"token": sesion.token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data['success'] is True
    assert data['total'] >= 3


def test_admin_send_email_validation(client, db):
    """Test validación de envío de email"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin13@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Intentar enviar sin destinatarios válidos
    response = client.post(
        "/api/admin/send-email",
        headers={"token": sesion.token},
        data={
            "subject": "Test",
            "message": "Test message",
            "send_to": "invalid"
        }
    )

    assert response.status_code == 400


def test_admin_send_email_to_all(client, db):
    """Test envío de email a todos los usuarios newsletter"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin14@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Crear usuarios newsletter
    for i in range(3):
        usuario_crud.create(
            db,
            nombre=f"Newsletter {i}",
            email=f"newsletter_email{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    # Mock del servicio de email
    with patch('backend.services.email_service.email_service.send_newsletter_email') as mock_email:
        mock_email.return_value = True

        response = client.post(
            "/api/admin/send-email",
            headers={"token": sesion.token},
            data={
                "subject": "Test Newsletter",
                "message": "This is a test",
                "send_to": "all"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data['success'] is True
        assert data['enviados'] >= 3
        assert data['total'] >= 3


def test_admin_send_email_to_selected(client, db):
    """Test envío de email a usuarios seleccionados"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin15@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Crear usuarios
    user1 = usuario_crud.create(
        db,
        nombre="User 1",
        email="selected1@test.com",
        password="test123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )
    user2 = usuario_crud.create(
        db,
        nombre="User 2",
        email="selected2@test.com",
        password="test123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    with patch('backend.services.email_service.email_service.send_newsletter_email') as mock_email:
        mock_email.return_value = True

        response = client.post(
            "/api/admin/send-email",
            headers={"token": sesion.token},
            data={
                "subject": "Test Selected",
                "message": "Test",
                "send_to": "selected",
                "selected_ids": f"{user1.id},{user2.id}"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data['success'] is True
        assert data['enviados'] == 2


def test_verify_admin_token_middleware(client, db):
    """Test verificación del token de admin en el middleware"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud

    # Crear usuario normal (no admin)
    user = usuario_crud.create(
        db,
        nombre="Normal User",
        email="normal@test.com",
        password="test123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )
    sesion = sesion_crud.create(db, user.id)

    # Intentar acceder a endpoint de admin con token de usuario normal
    response = client.get(
        "/api/admin/dashboard",
        headers={"token": sesion.token}
    )

    assert response.status_code == 403  # Forbidden


def test_admin_dashboard_traffic_sources(client, db):
    """Test estadísticas de fuentes de tráfico en dashboard"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud
    from backend.crud.tracking import tracking_crud

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin16@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Crear visitas de diferentes fuentes
    sources = ["linkedin", "instagram", "youtube"]
    for source in sources:
        for i in range(2):
            tracking_crud.create_page_visit(
                db,
                session_id=f"{source}_session_{i}",
                traffic_source=source,
                landing_page="/"
            )

    response = client.get(
        "/api/admin/dashboard",
        headers={"token": sesion.token}
    )

    assert response.status_code == 200
    data = response.json()

    assert 'trafico_por_fuente' in data
    assert len(data['trafico_por_fuente']) >= 3


def test_admin_dashboard_conversion_rate(client, db):
    """Test cálculo de tasa de conversión en dashboard"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.sesion import sesion_crud
    from backend.crud.tracking import tracking_crud

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin17@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )
    sesion = sesion_crud.create(db, admin.id)

    # Crear 100 visitas
    for i in range(100):
        tracking_crud.create_page_visit(
            db,
            session_id=f"conversion_session_{i}",
            traffic_source="test",
            landing_page="/"
        )

    # Crear 10 bookings (10% de conversión)
    for i in range(10):
        tracking_crud.create_calendly_booking(
            db,
            calendly_event_id=f"evt_conversion_{i}",
            invitee_email=f"conversion{i}@test.com",
            invitee_name=f"User {i}",
            event_start_time=datetime.now(),
            booking_timestamp=datetime.now(),
            session_id=f"conversion_session_{i}",
            traffic_source="test"
        )

    response = client.get(
        "/api/admin/dashboard",
        headers={"token": sesion.token}
    )

    assert response.status_code == 200
    data = response.json()

    assert 'tasa_conversion' in data
    assert data['tasa_conversion'] == 10.0


def test_admin_authenticate_function(db):
    """Test función authenticate_admin directamente"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.admin_crud import authenticate_admin

    # Crear admin
    usuario_crud.create(
        db,
        nombre="Admin",
        email="admin18@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    # Autenticar correctamente
    usuario = authenticate_admin(db, "admin18@test.com", "admin123")
    assert usuario is not None
    assert usuario.tipo_usuario == TipoUsuario.ADMIN

    # Contraseña incorrecta
    usuario = authenticate_admin(db, "admin18@test.com", "wrong")
    assert usuario is None

    # Usuario que no es admin
    usuario_crud.create(
        db,
        nombre="User",
        email="user18@test.com",
        password="user123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )
    usuario = authenticate_admin(db, "user18@test.com", "user123")
    assert usuario is None


def test_admin_get_dashboard_stats_function(db):
    """Test función get_dashboard_stats directamente"""
    from backend.crud.admin_crud import get_dashboard_stats
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # Crear usuarios
    for i in range(5):
        usuario_crud.create(
            db,
            nombre=f"User {i}",
            email=f"stats{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    stats = get_dashboard_stats(db)

    assert 'total_usuarios_newsletter' in stats
    assert 'total_consultas' in stats
    assert 'total_visitas' in stats
    assert 'visitas_unicas' in stats
    assert 'total_clicks_calendly' in stats
    assert 'total_bookings' in stats
    assert 'tasa_conversion' in stats
    assert 'trafico_por_fuente' in stats

    assert stats['total_usuarios_newsletter'] >= 5