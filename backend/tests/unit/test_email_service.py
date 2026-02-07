# ==========================================
# backend/tests/unit/test_email_service.py
# ==========================================
"""Tests unitarios para el servicio de email"""
import pytest
from unittest.mock import patch, MagicMock
import base64


@pytest.mark.asyncio
async def test_send_newsletter_email_simple():
    """Test envío de email simple sin adjuntos"""
    from backend.services.email_service import email_service

    with patch('requests.post') as mock_post:
        # Simular respuesta exitosa de Brevo
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        result = await email_service.send_newsletter_email(
            to_email="test@example.com",
            to_name="Test User",
            subject="Newsletter Test",
            message="Este es un mensaje de prueba"
        )

        assert result is True
        assert mock_post.called

        # Verificar que se llamó con los parámetros correctos
        call_args = mock_post.call_args
        payload = call_args[1]['json']

        assert payload['subject'] == "Newsletter Test"
        assert payload['to'][0]['email'] == "test@example.com"
        assert payload['to'][0]['name'] == "Test User"


@pytest.mark.asyncio
async def test_send_newsletter_email_with_html():
    """Test envío de email con contenido HTML"""
    from backend.services.email_service import email_service

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        html_message = """
        <html>
            <body>
                <h1>Newsletter</h1>
                <p>Contenido del newsletter</p>
            </body>
        </html>
        """

        result = await email_service.send_newsletter_email(
            to_email="html@test.com",
            to_name="HTML User",
            subject="HTML Newsletter",
            message=html_message
        )

        assert result is True


@pytest.mark.asyncio
async def test_send_newsletter_email_with_attachments():
    """Test envío de email con adjuntos"""
    from backend.services.email_service import email_service

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        # Crear adjuntos de prueba
        pdf_content = b'%PDF-1.4 fake pdf content'
        image_content = b'\x89PNG\r\n\x1a\n fake png content'

        attachments = [
            {
                'content': pdf_content,
                'name': 'documento.pdf'
            },
            {
                'content': image_content,
                'name': 'imagen.png'
            }
        ]

        result = await email_service.send_newsletter_email(
            to_email="attach@test.com",
            to_name="Attach User",
            subject="Email con Adjuntos",
            message="Este email tiene adjuntos",
            attachments=attachments
        )

        assert result is True

        # Verificar que los adjuntos se procesaron correctamente
        call_args = mock_post.call_args
        payload = call_args[1]['json']

        assert 'attachment' in payload
        assert len(payload['attachment']) == 2
        assert payload['attachment'][0]['name'] == 'documento.pdf'
        assert payload['attachment'][1]['name'] == 'imagen.png'


@pytest.mark.asyncio
async def test_send_newsletter_email_failure():
    """Test manejo de error en envío de email"""
    from backend.services.email_service import email_service

    with patch('requests.post') as mock_post:
        # Simular error de Brevo
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        result = await email_service.send_newsletter_email(
            to_email="error@test.com",
            to_name="Error User",
            subject="Error Test",
            message="Este email fallará"
        )

        assert result is False


@pytest.mark.asyncio
async def test_send_newsletter_email_exception():
    """Test manejo de excepción en envío de email"""
    from backend.services.email_service import email_service

    with patch('requests.post') as mock_post:
        # Simular excepción de red
        mock_post.side_effect = Exception("Network error")

        result = await email_service.send_newsletter_email(
            to_email="exception@test.com",
            to_name="Exception User",
            subject="Exception Test",
            message="Este email causará una excepción"
        )

        assert result is False


@pytest.mark.asyncio
async def test_send_plain_email():
    """Test envío de email plain sin template"""
    from backend.services.email_service import email_service

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        html_content = "<h1>Test</h1><p>Plain email</p>"

        result = await email_service.send_plain_email(
            to_email="plain@test.com",
            to_name="Plain User",
            subject="Plain Email",
            html_content=html_content
        )

        assert result is True


@pytest.mark.asyncio
async def test_send_newsletter_email_text_to_html_conversion():
    """Test conversión automática de texto a HTML"""
    from backend.services.email_service import email_service

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        # Mensaje de texto simple (sin HTML)
        text_message = "Línea 1\nLínea 2\nLínea 3"

        result = await email_service.send_newsletter_email(
            to_email="convert@test.com",
            to_name="Convert User",
            subject="Text to HTML",
            message=text_message
        )

        assert result is True

        # Verificar que los saltos de línea se convirtieron a <br>
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        html_content = payload['htmlContent']

        assert '<br>' in html_content


@pytest.mark.asyncio
async def test_attachment_base64_encoding():
    """Test codificación correcta de adjuntos a base64"""
    from backend.services.email_service import email_service

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        # Contenido de prueba
        file_content = b'Test file content 12345'
        expected_b64 = base64.b64encode(file_content).decode('utf-8')

        attachments = [
            {
                'content': file_content,
                'name': 'test.txt'
            }
        ]

        result = await email_service.send_newsletter_email(
            to_email="b64@test.com",
            to_name="B64 User",
            subject="Base64 Test",
            message="Testing base64 encoding",
            attachments=attachments
        )

        assert result is True

        # Verificar codificación
        call_args = mock_post.call_args
        payload = call_args[1]['json']

        assert payload['attachment'][0]['content'] == expected_b64


@pytest.mark.asyncio
async def test_multiple_attachments_different_types():
    """Test envío con múltiples adjuntos de diferentes tipos"""
    from backend.services.email_service import email_service

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        attachments = [
            {'content': b'PDF content', 'name': 'doc.pdf'},
            {'content': b'PNG content', 'name': 'img.png'},
            {'content': b'JPEG content', 'name': 'photo.jpg'},
            {'content': b'TXT content', 'name': 'text.txt'}
        ]

        result = await email_service.send_newsletter_email(
            to_email="multi@test.com",
            to_name="Multi User",
            subject="Multiple Attachments",
            message="Email con varios adjuntos",
            attachments=attachments
        )

        assert result is True

        call_args = mock_post.call_args
        payload = call_args[1]['json']

        assert len(payload['attachment']) == 4
        assert payload['attachment'][0]['name'] == 'doc.pdf'
        assert payload['attachment'][3]['name'] == 'text.txt'


@pytest.mark.asyncio
async def test_email_sender_configuration():
    """Test configuración correcta del remitente"""
    from backend.services.email_service import email_service

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        result = await email_service.send_newsletter_email(
            to_email="sender@test.com",
            to_name="Sender User",
            subject="Sender Test",
            message="Testing sender config"
        )

        assert result is True

        call_args = mock_post.call_args
        payload = call_args[1]['json']

        assert 'sender' in payload
        assert payload['sender']['email'] == "petruworkout@gmail.com"
        assert payload['sender']['name'] == "PetruWorkout"


@pytest.mark.asyncio
async def test_email_timeout_configuration():
    """Test configuración de timeout en requests"""
    from backend.services.email_service import email_service

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        result = await email_service.send_newsletter_email(
            to_email="timeout@test.com",
            to_name="Timeout User",
            subject="Timeout Test",
            message="Testing timeout"
        )

        assert result is True

        # Verificar que se usó timeout
        call_args = mock_post.call_args
        assert call_args[1]['timeout'] == 10