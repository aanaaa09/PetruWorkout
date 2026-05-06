# ==========================================
# backend/tests/integration/test_admin_flow.py
# ==========================================
"""Tests de integración para flujo completo de administración"""
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import patch


def _move_to_yesterday(db, obj):
    yesterday = date.today() - timedelta(days=1)
    obj.fecha = yesterday
    if hasattr(obj, 'timestamp'):
        obj.timestamp = datetime.now() - timedelta(days=1)
    db.commit()
    return obj


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
    response = client.get("/api/admin/users?tipo=newsletter", headers={"token": token})
    assert response.status_code == 200
    data = response.json()
    assert data['total'] >= 5

    # 5. Eliminar un usuario
    user_id = data['usuarios'][0]['id']
    response = client.delete(f"/api/admin/users/{user_id}", headers={"token": token})
    assert response.status_code == 200
    assert response.json()['deleted'] is True

    # 6. Verificar que fue eliminado
    response = client.get("/api/admin/users", headers={"token": token})
    assert response.status_code == 200
    assert not any(u['id'] == user_id for u in response.json()['usuarios'])


def test_flujo_completo_envio_newsletter(client, db):
    """Test flujo: login → crear usuarios → enviar newsletter"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    usuario_crud.create(
        db, nombre="Admin", email="admin_newsletter@test.com",
        password="admin123", tipo_usuario=TipoUsuario.ADMIN
    )
    token = client.post("/api/admin/login", json={
        "email": "admin_newsletter@test.com", "password": "admin123"
    }).json()['token']

    for i in range(3):
        usuario_crud.create(
            db, nombre=f"Subscriber {i}", email=f"subscriber{i}@test.com",
            password="test123", tipo_usuario=TipoUsuario.NEWSLETTER
        )

    with patch('backend.services.email_service.email_service.send_newsletter_email') as mock_email:
        mock_email.return_value = True
        response = client.post(
            "/api/admin/send-email",
            headers={"token": token},
            data={"subject": "Newsletter Test", "message": "Contenido", "send_to": "all"}
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
    from backend.models.page_visit import PageVisit
    from backend.models.calendly_click import CalendlyClick
    from backend.models.calendly_booking import CalendlyBooking

    # Usuarios newsletter
    for i in range(10):
        usuario_crud.create(
            db, nombre=f"User {i}", email=f"dashboard{i}@test.com",
            password="test123", tipo_usuario=TipoUsuario.NEWSLETTER
        )

    # Visitas con fuentes CONOCIDAS — mover a ayer para entrar en el rango
    for i in range(50):
        visit = tracking_crud.create_page_visit(
            db,
            session_id=f"session_{i}",
            traffic_source="instagram" if i % 2 == 0 else "youtube",
            landing_page="/"
        )
        _move_to_yesterday(db, visit)

    # Clicks — mover a ayer
    for i in range(20):
        click = tracking_crud.create_calendly_click(
            db,
            session_id=f"session_{i}",
            traffic_source="instagram" if i % 2 == 0 else "youtube",
            button_id="cta",
            button_location="hero"
        )
        _move_to_yesterday(db, click)

    # Bookings — mover a ayer
    for i in range(5):
        booking = tracking_crud.create_calendly_booking(
            db,
            calendly_event_id=f"evt_{i}",
            invitee_email=f"booking{i}@test.com",
            invitee_name=f"Booking {i}",
            event_start_time=datetime.now(),
            booking_timestamp=datetime.now(),
            session_id=f"session_{i}",
            traffic_source="instagram"
        )
        _move_to_yesterday(db, booking)

    # Consultas
    for i in range(8):
        db.add(Consulta(
            nombre=f"User {i}", email=f"consult{i}@test.com",
            asunto="Test", mensaje="Test message"
        ))
    db.commit()

    # Login admin
    usuario_crud.create(
        db, nombre="Admin", email="admin_stats@test.com",
        password="admin123", tipo_usuario=TipoUsuario.ADMIN
    )
    token = client.post("/api/admin/login", json={
        "email": "admin_stats@test.com", "password": "admin123"
    }).json()['token']

    # Dashboard — rango por defecto (últimos 30 días hasta ayer inclusive)
    response = client.get("/api/admin/dashboard", headers={"token": token})
    assert response.status_code == 200
    stats = response.json()

    assert stats['total_visits'] >= 1
    assert stats['total_bookings'] >= 1
    assert stats['total_clicks'] >= 1
    assert 0 <= stats['conversion_rate'] <= 1


def test_flujo_gestion_consultas(client, db):
    """Test flujo: recibir consultas → admin las revisa"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    with patch('backend.services.email_service.email_service.send_consulta_email') as mock_email:
        mock_email.return_value = True
        response = client.post("/api/consultas/enviar", json={
            "nombre": "Juan Pérez", "email": "juan@test.com",
            "asunto": "Pregunta sobre entrenamiento",
            "mensaje": "¿Cuándo empiezan las clases?"
        })
        assert response.status_code == 200

    usuario_crud.create(
        db, nombre="Admin", email="admin_consultas@test.com",
        password="admin123", tipo_usuario=TipoUsuario.ADMIN
    )
    token = client.post("/api/admin/login", json={
        "email": "admin_consultas@test.com", "password": "admin123"
    }).json()['token']

    response = client.get("/api/admin/consultas", headers={"token": token})
    assert response.status_code == 200
    data = response.json()
    assert data['total'] >= 1
    assert any(c['email'] == "juan@test.com" for c in data['consultas'])


def test_flujo_segmentacion_envio_emails(client, db):
    """Test flujo: crear usuarios → seleccionar específicos → enviar email"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    usuario_crud.create(
        db, nombre="Admin", email="admin_segment@test.com",
        password="admin123", tipo_usuario=TipoUsuario.ADMIN
    )
    token = client.post("/api/admin/login", json={
        "email": "admin_segment@test.com", "password": "admin123"
    }).json()['token']

    users_ids = []
    for i in range(5):
        user = usuario_crud.create(
            db, nombre=f"User {i}", email=f"segment{i}@test.com",
            password="test123", tipo_usuario=TipoUsuario.NEWSLETTER
        )
        users_ids.append(user.id)

    selected_ids = ",".join(str(id) for id in users_ids[:3])

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
    from backend.models.page_visit import PageVisit
    from backend.models.calendly_click import CalendlyClick
    from backend.models.calendly_booking import CalendlyBooking

    session_id = "admin_tracking_test"

    # 1. Visita — fuente conocida, mover a ayer
    response = client.post("/api/tracking/visit", json={
        "session_id": session_id,
        "traffic_source": "youtube",
        "landing_page": "/"
    })
    assert response.status_code == 200
    visit = db.query(PageVisit).filter(PageVisit.session_id == session_id).first()
    _move_to_yesterday(db, visit)

    # 2. Click — mover a ayer
    response = client.post("/api/tracking/click", json={
        "session_id": session_id,
        "traffic_source": "youtube",
        "button_id": "hero-cta",
        "button_location": "hero"
    })
    assert response.status_code == 200
    click = db.query(CalendlyClick).filter(CalendlyClick.session_id == session_id).first()
    _move_to_yesterday(db, click)

    # 3. Booking — mover a ayer
    response = client.post("/api/tracking/booking-completed", json={
        "session_id": session_id,
        "traffic_source": "youtube",
        "invitee_email": "tracking@test.com",
        "invitee_name": "Tracking Test",
        "event_uri": "evt_tracking_123"
    })
    assert response.status_code == 200
    booking = db.query(CalendlyBooking).filter(CalendlyBooking.session_id == session_id).first()
    _move_to_yesterday(db, booking)

    # 4. Crear admin y login
    usuario_crud.create(
        db, nombre="Admin", email="admin_tracking_flow@test.com",
        password="admin123", tipo_usuario=TipoUsuario.ADMIN
    )
    token = client.post("/api/admin/login", json={
        "email": "admin_tracking_flow@test.com", "password": "admin123"
    }).json()['token']
    headers = {"token": token}

    # 5. Verificar funnel — rango por defecto (hasta ayer inclusive)
    response = client.get("/api/tracking/funnel?source=youtube", headers=headers)
    assert response.status_code == 200

    # 6. Dashboard — rango por defecto
    response = client.get("/api/admin/dashboard", headers=headers)
    assert response.status_code == 200
    stats = response.json()

    assert stats['total_visits'] >= 1
    assert stats['total_clicks'] >= 1
    assert stats['total_bookings'] >= 1


def test_flujo_paginacion_usuarios(client, db):
    """Test flujo: crear muchos usuarios → navegar por páginas"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario

    usuario_crud.create(
        db, nombre="Admin", email="admin_pagination@test.com",
        password="admin123", tipo_usuario=TipoUsuario.ADMIN
    )
    token = client.post("/api/admin/login", json={
        "email": "admin_pagination@test.com", "password": "admin123"
    }).json()['token']

    for i in range(25):
        usuario_crud.create(
            db, nombre=f"Page User {i}", email=f"page_user{i}@test.com",
            password="test123", tipo_usuario=TipoUsuario.NEWSLETTER
        )

    response = client.get("/api/admin/users?limit=10&offset=0", headers={"token": token})
    assert response.status_code == 200
    page1 = response.json()
    assert page1['total'] >= 25
    assert len(page1['usuarios']) == 10

    response = client.get("/api/admin/users?limit=10&offset=10", headers={"token": token})
    assert response.status_code == 200
    page2 = response.json()
    assert len(page2['usuarios']) == 10

    response = client.get("/api/admin/users?limit=10&offset=20", headers={"token": token})
    assert response.status_code == 200
    page3 = response.json()
    assert len(page3['usuarios']) >= 5

    ids_page1 = [u['id'] for u in page1['usuarios']]
    ids_page2 = [u['id'] for u in page2['usuarios']]
    ids_page3 = [u['id'] for u in page3['usuarios']]

    assert not any(id in ids_page2 for id in ids_page1)
    assert not any(id in ids_page3 for id in ids_page2)