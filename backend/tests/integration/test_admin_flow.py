# ==========================================
# backend/tests/integration/test_admin_flow.py
# ==========================================
"""Tests de integración para flujo completo de administración"""
import pytest
from datetime import datetime
from unittest.mock import patch


def test_flujo_completo_admin_gestion_usuarios(client, db):
    """Test flujo: login admin → listar usuarios → eliminar usuario"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # 1. Crear admin
    usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_flow@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    # 2. Login
    response = client.post("/api/admin/login", json={
        "email": "admin_flow@test.com",
        "password": "admin123"
    })

    assert response.status_code == 200
    token = response.json()['token']

    # 3. Crear usuarios para gestionar
    for i in range(5):
        usuario_crud.create(
            db,
            nombre=f"User {i}",
            email=f"manage{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    # 4. Listar usuarios
    response = client.get(
        "/api/admin/users?tipo=newsletter",
        headers={"token": token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data['total'] >= 5

    # 5. Seleccionar un usuario para eliminar
    user_to_delete = data['usuarios'][0]
    user_id = user_to_delete['id']

    # 6. Eliminar usuario
    response = client.delete(
        f"/api/admin/users/{user_id}",
        headers={"token": token}
    )

    assert response.status_code == 200
    assert response.json()['deleted'] is True

    # 7. Verificar que fue eliminado
    response = client.get(
        "/api/admin/users",
        headers={"token": token}
    )

    assert response.status_code == 200
    remaining_users = response.json()['usuarios']
    assert not any(u['id'] == user_id for u in remaining_users)


def test_flujo_completo_envio_newsletter(client, db):
    """Test flujo: login → crear usuarios → enviar newsletter"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # 1. Crear admin
    usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_newsletter@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    # 2. Login
    response = client.post("/api/admin/login", json={
        "email": "admin_newsletter@test.com",
        "password": "admin123"
    })

    token = response.json()['token']

    # 3. Crear suscriptores
    for i in range(3):
        usuario_crud.create(
            db,
            nombre=f"Subscriber {i}",
            email=f"subscriber{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    # 4. Enviar newsletter a todos
    with patch('backend.services.email_service.email_service.send_newsletter_email') as mock_email:
        mock_email.return_value = True

        response = client.post(
            "/api/admin/send-email",
            headers={"token": token},
            data={
                "subject": "Newsletter Test",
                "message": "Contenido del newsletter",
                "send_to": "all"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data['success'] is True
        assert data['enviados'] >= 3
        assert data['errores'] == 0


def test_flujo_dashboard_estadisticas_completas(client, db):
    """Test flujo: crear datos → login admin → ver estadísticas completas"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.tracking import tracking_crud
    from backend.models.consulta import Consulta

    # 1. Crear datos de prueba

    # Usuarios newsletter
    for i in range(10):
        usuario_crud.create(
            db,
            nombre=f"User {i}",
            email=f"dashboard{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    # Visitas
    for i in range(50):
        tracking_crud.create_page_visit(
            db,
            session_id=f"session_{i}",
            traffic_source="linkedin" if i % 2 == 0 else "instagram",
            landing_page="/"
        )

    # Clicks
    for i in range(20):
        tracking_crud.create_calendly_click(
            db,
            session_id=f"session_{i}",
            traffic_source="linkedin" if i % 2 == 0 else "instagram",
            button_id="cta",
            button_location="hero"
        )

    # Bookings
    for i in range(5):
        tracking_crud.create_calendly_booking(
            db,
            calendly_event_id=f"evt_{i}",
            invitee_email=f"booking{i}@test.com",
            invitee_name=f"Booking {i}",
            event_start_time=datetime.now(),
            booking_timestamp=datetime.now(),
            session_id=f"session_{i}",
            traffic_source="linkedin"
        )

    # Consultas
    for i in range(8):
        consulta = Consulta(
            nombre=f"User {i}",
            email=f"consult{i}@test.com",
            asunto="Test",
            mensaje="Test message"
        )
        db.add(consulta)
    db.commit()

    # 2. Crear admin y login
    usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_stats@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    response = client.post("/api/admin/login", json={
        "email": "admin_stats@test.com",
        "password": "admin123"
    })

    token = response.json()['token']

    # 3. Obtener estadísticas
    response = client.get(
        "/api/admin/dashboard",
        headers={"token": token}
    )

    assert response.status_code == 200
    stats = response.json()

    # Verificar estadísticas
    assert stats['total_usuarios_newsletter'] >= 10
    assert stats['total_consultas'] >= 8
    assert stats['total_visitas'] >= 50
    assert stats['total_clicks_calendly'] >= 20
    assert stats['total_bookings'] >= 5
    assert stats['tasa_conversion'] == 10.0  # 5 bookings / 50 visitas * 100


def test_flujo_gestion_consultas(client, db):
    """Test flujo: recibir consultas → admin las revisa"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # 1. Usuario envía consulta
    with patch('backend.routers.consultas.enviar_email_brevo') as mock_email:
        mock_email.return_value = True

        response = client.post("/api/consultas/enviar", json={
            "nombre": "Juan Pérez",
            "email": "juan@test.com",
            "asunto": "Pregunta sobre entrenamiento",
            "mensaje": "¿Cuándo empiezan las clases?"
        })

        assert response.status_code == 200

    # 2. Admin login
    usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_consultas@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    response = client.post("/api/admin/login", json={
        "email": "admin_consultas@test.com",
        "password": "admin123"
    })

    token = response.json()['token']

    # 3. Admin revisa consultas
    response = client.get(
        "/api/admin/consultas",
        headers={"token": token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data['total'] >= 1
    assert any(c['email'] == "juan@test.com" for c in data['consultas'])


def test_flujo_segmentacion_envio_emails(client, db):
    """Test flujo: crear usuarios → seleccionar específicos → enviar email"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # 1. Crear admin
    usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_segment@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    response = client.post("/api/admin/login", json={
        "email": "admin_segment@test.com",
        "password": "admin123"
    })

    token = response.json()['token']

    # 2. Crear usuarios
    users_ids = []
    for i in range(5):
        user = usuario_crud.create(
            db,
            nombre=f"User {i}",
            email=f"segment{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )
        users_ids.append(user.id)

    # 3. Seleccionar solo los primeros 3 usuarios
    selected_ids = ",".join(str(id) for id in users_ids[:3])

    # 4. Enviar email a seleccionados
    with patch('backend.services.email_service.email_service.send_newsletter_email') as mock_email:
        mock_email.return_value = True

        response = client.post(
            "/api/admin/send-email",
            headers={"token": token},
            data={
                "subject": "Email Segmentado",
                "message": "Solo para usuarios seleccionados",
                "send_to": "selected",
                "selected_ids": selected_ids
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data['enviados'] == 3
        assert data['total'] == 3


def test_flujo_tracking_completo_admin(client, db):
    """Test flujo: usuario navega → hace booking → admin ve estadísticas"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.tracking import tracking_crud

    session_id = "admin_tracking_test"

    # 1. Usuario visita la web
    response = client.post("/api/tracking/visit", json={
        "session_id": session_id,
        "traffic_source": "youtube",
        "landing_page": "/"
    })
    assert response.status_code == 200

    # 2. Usuario hace click en Calendly
    response = client.post("/api/tracking/click", json={
        "session_id": session_id,
        "traffic_source": "youtube",
        "button_id": "hero-cta",
        "button_location": "hero"
    })
    assert response.status_code == 200

    # 3. Usuario completa booking
    response = client.post("/api/tracking/booking-completed", json={
        "session_id": session_id,
        "traffic_source": "youtube",
        "invitee_email": "tracking@test.com",
        "invitee_name": "Tracking Test",
        "event_uri": "evt_tracking_123"
    })
    assert response.status_code == 200

    # 4. Admin login
    usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_tracking@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    response = client.post("/api/admin/login", json={
        "email": "admin_tracking@test.com",
        "password": "admin123"
    })

    token = response.json()['token']

    # 5. Admin revisa bookings
    response = client.get(
        "/api/admin/bookings",
        headers={"token": token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data['total'] >= 1
    assert any(b['invitee_email'] == "tracking@test.com" for b in data['bookings'])

    # 6. Admin revisa dashboard
    response = client.get(
        "/api/admin/dashboard",
        headers={"token": token}
    )

    assert response.status_code == 200
    stats = response.json()

    assert stats['total_visitas'] >= 1
    assert stats['total_clicks_calendly'] >= 1
    assert stats['total_bookings'] >= 1


def test_flujo_paginacion_usuarios(client, db):
    """Test flujo: crear muchos usuarios → navegar por páginas"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    # 1. Crear admin
    usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_pagination@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    response = client.post("/api/admin/login", json={
        "email": "admin_pagination@test.com",
        "password": "admin123"
    })

    token = response.json()['token']

    # 2. Crear 25 usuarios
    for i in range(25):
        usuario_crud.create(
            db,
            nombre=f"Page User {i}",
            email=f"page_user{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    # 3. Primera página (10 usuarios)
    response = client.get(
        "/api/admin/users?limit=10&offset=0",
        headers={"token": token}
    )

    assert response.status_code == 200
    page1 = response.json()
    assert page1['total'] >= 25
    assert len(page1['usuarios']) == 10

    # 4. Segunda página
    response = client.get(
        "/api/admin/users?limit=10&offset=10",
        headers={"token": token}
    )

    assert response.status_code == 200
    page2 = response.json()
    assert len(page2['usuarios']) == 10

    # 5. Tercera página
    response = client.get(
        "/api/admin/users?limit=10&offset=20",
        headers={"token": token}
    )

    assert response.status_code == 200
    page3 = response.json()
    assert len(page3['usuarios']) >= 5

    # Verificar que no hay usuarios duplicados entre páginas
    ids_page1 = [u['id'] for u in page1['usuarios']]
    ids_page2 = [u['id'] for u in page2['usuarios']]
    ids_page3 = [u['id'] for u in page3['usuarios']]

    assert not any(id in ids_page2 for id in ids_page1)
    assert not any(id in ids_page3 for id in ids_page2)