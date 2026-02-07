# ==========================================
# backend/tests/unit/test_admin_crud.py
# ==========================================
"""Tests unitarios para admin_crud"""
import pytest
from datetime import datetime, timedelta


def test_get_users_list_default(db):
    """Test listar usuarios sin filtros"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.admin_crud import get_users_list

    # Crear usuarios
    for i in range(5):
        usuario_crud.create(
            db,
            nombre=f"User {i}",
            email=f"default{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    result = get_users_list(db)

    assert 'total' in result
    assert 'usuarios' in result
    assert result['total'] >= 5


def test_get_users_list_admin_filter(db):
    """Test filtrar solo administradores"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.admin_crud import get_users_list

    # Crear admins
    for i in range(2):
        usuario_crud.create(
            db,
            nombre=f"Admin {i}",
            email=f"admin_filter{i}@test.com",
            password="admin123",
            tipo_usuario=TipoUsuario.ADMIN
        )

    # Crear usuarios normales
    for i in range(3):
        usuario_crud.create(
            db,
            nombre=f"User {i}",
            email=f"user_filter{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    result = get_users_list(db, tipo='admin')

    # Solo debería retornar admins
    for usuario in result['usuarios']:
        assert usuario['tipo_usuario'] == 'admin'


def test_get_users_list_newsletter_filter(db):
    """Test filtrar solo usuarios newsletter"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.admin_crud import get_users_list

    # Crear admins
    usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_nl@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    # Crear usuarios newsletter
    for i in range(5):
        usuario_crud.create(
            db,
            nombre=f"Newsletter {i}",
            email=f"nl_filter{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    result = get_users_list(db, tipo='newsletter')

    # Solo debería retornar newsletter
    for usuario in result['usuarios']:
        assert usuario['tipo_usuario'] == 'newsletter'


def test_get_users_list_pagination(db):
    """Test paginación en listado de usuarios"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.admin_crud import get_users_list

    # Crear 20 usuarios
    for i in range(20):
        usuario_crud.create(
            db,
            nombre=f"Page {i}",
            email=f"pagination{i}@test.com",
            password="test123",
            tipo_usuario=TipoUsuario.NEWSLETTER
        )

    # Primera página
    page1 = get_users_list(db, limit=5, offset=0)
    assert len(page1['usuarios']) == 5

    # Segunda página
    page2 = get_users_list(db, limit=5, offset=5)
    assert len(page2['usuarios']) == 5

    # Verificar que son diferentes
    ids1 = [u['id'] for u in page1['usuarios']]
    ids2 = [u['id'] for u in page2['usuarios']]
    assert not any(id in ids2 for id in ids1)


def test_get_users_list_order_by_recent(db):
    """Test que usuarios se ordenan por más recientes primero"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.admin_crud import get_users_list

    # Crear usuarios con diferentes fechas
    user1 = usuario_crud.create(
        db,
        nombre="Old User",
        email="old@test.com",
        password="test123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    # Simular usuario antiguo
    user1.fecha_registro = datetime.now() - timedelta(days=30)
    db.commit()

    user2 = usuario_crud.create(
        db,
        nombre="Recent User",
        email="recent@test.com",
        password="test123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    result = get_users_list(db, limit=10)

    # El más reciente debe aparecer primero
    assert result['usuarios'][0]['email'] == "recent@test.com"


def test_delete_user_success(db):
    """Test eliminación exitosa de usuario"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.admin_crud import delete_user

    # Crear admin
    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_delete@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    # Crear usuario a eliminar
    user = usuario_crud.create(
        db,
        nombre="To Delete",
        email="delete_success@test.com",
        password="test123",
        tipo_usuario=TipoUsuario.NEWSLETTER
    )

    result = delete_user(db, user.id, admin.id)

    assert result['deleted'] is True
    assert result['user_id'] == user.id
    assert result['email'] == "delete_success@test.com"


def test_delete_user_cannot_delete_admin_type(db):
    """Test que no se puede eliminar usuario tipo ADMIN"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.admin_crud import delete_user

    # Crear dos admins
    admin1 = usuario_crud.create(
        db,
        nombre="Admin 1",
        email="admin1_nodelete@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    admin2 = usuario_crud.create(
        db,
        nombre="Admin 2",
        email="admin2_nodelete@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    # Intentar eliminar admin2
    with pytest.raises(ValueError, match="Solo se pueden eliminar usuarios de tipo NEWSLETTER"):
        delete_user(db, admin2.id, admin1.id)


def test_delete_user_cannot_self_delete(db):
    """Test que admin no puede auto-eliminarse"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.admin_crud import delete_user

    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_self@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    with pytest.raises(ValueError, match="Un administrador no puede eliminarse a sí mismo"):
        delete_user(db, admin.id, admin.id)


def test_delete_user_not_found(db):
    """Test eliminar usuario inexistente"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.admin_crud import delete_user

    admin = usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_notfound@test.com",
        password="admin123",
        tipo_usuario=TipoUsuario.ADMIN
    )

    with pytest.raises(ValueError, match="Usuario no encontrado"):
        delete_user(db, 99999, admin.id)


def test_get_consultas_list(db):
    """Test listar consultas"""
    from backend.crud.admin_crud import get_consultas_list
    from backend.models.consulta import Consulta

    # Crear consultas
    for i in range(5):
        consulta = Consulta(
            nombre=f"User {i}",
            email=f"consulta{i}@test.com",
            asunto=f"Asunto {i}",
            mensaje=f"Mensaje {i}"
        )
        db.add(consulta)
    db.commit()

    result = get_consultas_list(db)

    assert result['total'] >= 5
    assert len(result['consultas']) >= 5


def test_get_consultas_list_pagination(db):
    """Test paginación de consultas"""
    from backend.crud.admin_crud import get_consultas_list
    from backend.models.consulta import Consulta

    # Crear 10 consultas
    for i in range(10):
        consulta = Consulta(
            nombre=f"User {i}",
            email=f"page_consulta{i}@test.com",
            asunto="Test",
            mensaje="Test"
        )
        db.add(consulta)
    db.commit()

    page1 = get_consultas_list(db, limit=5, offset=0)
    page2 = get_consultas_list(db, limit=5, offset=5)

    assert len(page1['consultas']) == 5
    assert len(page2['consultas']) >= 5


def test_get_bookings_list(db):
    """Test listar bookings"""
    from backend.crud.admin_crud import get_bookings_list
    from backend.crud.tracking import tracking_crud

    # Crear bookings
    for i in range(5):
        tracking_crud.create_calendly_booking(
            db,
            calendly_event_id=f"evt_list_{i}",
            invitee_email=f"booking_list{i}@test.com",
            invitee_name=f"User {i}",
            event_start_time=datetime.now(),
            booking_timestamp=datetime.now(),
            session_id=f"session_{i}",
            traffic_source="test"
        )

    result = get_bookings_list(db)

    assert result['total'] >= 5
    assert len(result['bookings']) >= 5


def test_get_bookings_list_pagination(db):
    """Test paginación de bookings"""
    from backend.crud.admin_crud import get_bookings_list
    from backend.crud.tracking import tracking_crud

    # Crear 10 bookings
    for i in range(10):
        tracking_crud.create_calendly_booking(
            db,
            calendly_event_id=f"evt_page_{i}",
            invitee_email=f"page_booking{i}@test.com",
            invitee_name=f"User {i}",
            event_start_time=datetime.now(),
            booking_timestamp=datetime.now(),
            session_id=f"session_{i}",
            traffic_source="test"
        )

    page1 = get_bookings_list(db, limit=5, offset=0)
    page2 = get_bookings_list(db, limit=5, offset=5)

    assert len(page1['bookings']) == 5
    assert len(page2['bookings']) >= 5


def test_get_dashboard_stats_empty_database(db):
    """Test estadísticas con base de datos vacía"""
    from backend.crud.admin_crud import get_dashboard_stats

    stats = get_dashboard_stats(db)

    assert stats['total_usuarios_newsletter'] == 0
    assert stats['total_consultas'] == 0
    assert stats['total_visitas'] == 0
    assert stats['visitas_unicas'] == 0
    assert stats['total_clicks_calendly'] == 0
    assert stats['total_bookings'] == 0
    assert stats['tasa_conversion'] == 0
    assert len(stats['trafico_por_fuente']) == 0


def test_get_dashboard_stats_traffic_sources(db):
    """Test estadísticas de fuentes de tráfico en dashboard"""
    from backend.crud.admin_crud import get_dashboard_stats
    from backend.crud.tracking import tracking_crud

    # Crear visitas de diferentes fuentes
    sources_counts = {
        'linkedin': 10,
        'instagram': 5,
        'youtube': 3
    }

    for source, count in sources_counts.items():
        for i in range(count):
            tracking_crud.create_page_visit(
                db,
                session_id=f"{source}_session_{i}",
                traffic_source=source,
                landing_page="/"
            )

    stats = get_dashboard_stats(db)

    assert len(stats['trafico_por_fuente']) == 3

    # Verificar conteos
    for item in stats['trafico_por_fuente']:
        assert item['total'] == sources_counts[item['fuente']]


def test_get_dashboard_stats_conversion_rate_calculation(db):
    """Test cálculo correcto de tasa de conversión"""
    from backend.crud.admin_crud import get_dashboard_stats
    from backend.crud.tracking import tracking_crud

    # 100 visitas
    for i in range(100):
        tracking_crud.create_page_visit(
            db,
            session_id=f"conv_session_{i}",
            traffic_source="test",
            landing_page="/"
        )

    # 10 bookings = 10% de conversión
    for i in range(10):
        tracking_crud.create_calendly_booking(
            db,
            calendly_event_id=f"evt_conv_{i}",
            invitee_email=f"conv{i}@test.com",
            invitee_name=f"User {i}",
            event_start_time=datetime.now(),
            booking_timestamp=datetime.now(),
            session_id=f"conv_session_{i}",
            traffic_source="test"
        )

    stats = get_dashboard_stats(db)

    assert stats['total_visitas'] == 100
    assert stats['total_bookings'] == 10
    assert stats['tasa_conversion'] == 10.0


def test_authenticate_admin_with_wrong_credentials(db):
    """Test autenticación admin con credenciales incorrectas"""
    from backend.crud.usuario import usuario_crud
    from backend.models.usuario import TipoUsuario
    from backend.crud.admin_crud import authenticate_admin

    usuario_crud.create(
        db,
        nombre="Admin",
        email="admin_auth@test.com",
        password="correctpassword",
        tipo_usuario=TipoUsuario.ADMIN
    )

    # Password incorrecta
    result = authenticate_admin(db, "admin_auth@test.com", "wrongpassword")
    assert result is None

    # Email incorrecto
    result = authenticate_admin(db, "wrong@test.com", "correctpassword")
    assert result is None