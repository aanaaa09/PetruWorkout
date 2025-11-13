import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from backend.services.auth_service import AuthService
from backend.models.usuario import Usuario
from backend.models.sesion import Sesion


class TestAuthServiceUnitario:
    """Tests unitarios para AuthService"""

    def test_registrar_usuario_validaciones_nombre_corto(self):
        """Test: nombre muy corto debe fallar"""
        db = Mock()
        resultado = AuthService.registrar_usuario(db, "A", "test@test.com", "123456")

        assert resultado['success'] is False
        assert 'nombre' in resultado['error'].lower()

    def test_registrar_usuario_validaciones_email_invalido(self):
        """Test: email inválido debe fallar"""
        db = Mock()
        resultado = AuthService.registrar_usuario(db, "Test User", "emailinvalido", "123456")

        assert resultado['success'] is False
        assert 'email' in resultado['error'].lower()

    def test_registrar_usuario_validaciones_password_corta(self):
        """Test: password muy corta debe fallar"""
        db = Mock()
        resultado = AuthService.registrar_usuario(db, "Test User", "test@test.com", "123")

        assert resultado['success'] is False
        assert 'contraseña' in resultado['error'].lower() or 'password' in resultado['error'].lower()

    def test_registrar_usuario_email_duplicado(self, mocker):
        """Test: email duplicado debe fallar"""
        db = Mock()

        # Mock del usuario existente
        usuario_existente = Usuario(
            id=1,
            nombre="Usuario Existente",
            email="test@test.com",
            password_hash="hash",
            puntos=0
        )

        mocker.patch(
            'backend.crud.usuario.usuario_crud.get_by_email',
            return_value=usuario_existente
        )

        resultado = AuthService.registrar_usuario(db, "Nuevo User", "test@test.com", "123456")

        assert resultado['success'] is False
        assert 'ya está registrado' in resultado['error'].lower()

    def test_registrar_usuario_exitoso(self, mocker):
        """Test: registro exitoso debe crear usuario y sesión"""
        db = Mock()

        # Mock usuario no existe
        mocker.patch(
            'backend.crud.usuario.usuario_crud.get_by_email',
            return_value=None
        )

        # Mock crear usuario
        nuevo_usuario = Usuario(
            id=1,
            nombre="Test User",
            email="test@test.com",
            password_hash="hash",
            puntos=0
        )
        mocker.patch(
            'backend.crud.usuario.usuario_crud.create',
            return_value=nuevo_usuario
        )

        # Mock crear sesión
        nueva_sesion = Sesion(
            id=1,
            usuario_id=1,
            token="test_token_123",
            fecha_expiracion=datetime.now() + timedelta(days=7)
        )
        mocker.patch(
            'backend.crud.sesion.sesion_crud.create',
            return_value=nueva_sesion
        )

        resultado = AuthService.registrar_usuario(db, "Test User", "test@test.com", "123456")

        assert resultado['success'] is True
        assert 'token' in resultado['data']
        assert 'usuario' in resultado['data']
        assert resultado['data']['token'] == "test_token_123"
        assert resultado['data']['usuario']['email'] == "test@test.com"

    def test_iniciar_sesion_campos_vacios(self):
        """Test: login sin email o password debe fallar"""
        db = Mock()

        resultado1 = AuthService.iniciar_sesion(db, "", "123456")
        assert resultado1['success'] is False

        resultado2 = AuthService.iniciar_sesion(db, "test@test.com", "")
        assert resultado2['success'] is False

    def test_iniciar_sesion_credenciales_incorrectas(self, mocker):
        """Test: credenciales incorrectas debe fallar"""
        db = Mock()

        mocker.patch(
            'backend.crud.usuario.usuario_crud.authenticate',
            return_value=None
        )

        resultado = AuthService.iniciar_sesion(db, "test@test.com", "wrongpass")

        assert resultado['success'] is False
        assert 'incorrectos' in resultado['error'].lower()

    def test_iniciar_sesion_exitoso(self, mocker):
        """Test: login exitoso debe retornar token"""
        db = Mock()

        # Mock usuario autenticado
        usuario = Usuario(
            id=1,
            nombre="Test User",
            email="test@test.com",
            password_hash="hash",
            puntos=100
        )
        mocker.patch(
            'backend.crud.usuario.usuario_crud.authenticate',
            return_value=usuario
        )

        # Mock update_last_login
        mocker.patch(
            'backend.crud.usuario.usuario_crud.update_last_login',
            return_value=None
        )

        # Mock crear sesión
        sesion = Sesion(
            id=1,
            usuario_id=1,
            token="login_token_456",
            fecha_expiracion=datetime.now() + timedelta(days=7)
        )
        mocker.patch(
            'backend.crud.sesion.sesion_crud.create',
            return_value=sesion
        )

        resultado = AuthService.iniciar_sesion(db, "test@test.com", "correctpass")

        assert resultado['success'] is True
        assert resultado['data']['token'] == "login_token_456"
        assert resultado['data']['usuario']['puntos'] == 100

    def test_verificar_sesion_token_invalido(self, mocker):
        """Test: token inválido debe retornar error"""
        db = Mock()

        mocker.patch(
            'backend.crud.sesion.sesion_crud.validate_token',
            return_value=None
        )

        resultado = AuthService.verificar_sesion(db, "token_invalido")

        assert resultado['valida'] is False
        assert 'error' in resultado

    def test_verificar_sesion_valida(self, mocker):
        """Test: token válido debe retornar usuario"""
        db = Mock()

        # Mock sesión válida
        sesion = Sesion(
            id=1,
            usuario_id=1,
            token="valid_token",
            fecha_expiracion=datetime.now() + timedelta(days=7)
        )
        mocker.patch(
            'backend.crud.sesion.sesion_crud.validate_token',
            return_value=sesion
        )

        # Mock usuario
        usuario = Usuario(
            id=1,
            nombre="Test User",
            email="test@test.com",
            password_hash="hash",
            puntos=200
        )
        mocker.patch(
            'backend.crud.usuario.usuario_crud.get_by_id',
            return_value=usuario
        )

        resultado = AuthService.verificar_sesion(db, "valid_token")

        assert resultado['valida'] is True
        assert resultado['usuario']['id'] == 1
        assert resultado['usuario']['puntos'] == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])