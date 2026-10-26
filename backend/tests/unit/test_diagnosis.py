# ==========================================
# backend/tests/unit/test_diagnosis.py
# ==========================================
"""Tests del formulario de diagnóstico: guardado en BD + aviso por Telegram"""
import pytest
import requests
from unittest.mock import patch, MagicMock

from backend.models.diagnostico_lead import DiagnosticoLead

TOKEN = "123456:SECRET-TOKEN"


def payload(**overrides):
    data = {
        "name": "Luis Prueba",
        "phone": "+34612345678",
        "age": "+35",
        "level": "Llevo tiempo sin entrenar",
        "goal": "Fuerza funcional para el día a día",
        "block": "Molestias o miedo a lesionarme",
        "solution": "Quiero ver mi diagnóstico y conocer los precios de tu asesoría.",
    }
    data.update(overrides)
    return data


def fake_response(status=200):
    res = MagicMock()
    res.status_code = status

    def raise_for_status():
        if status >= 400:
            raise requests.HTTPError(f"{status} Error for url: https://api.telegram.org/bot{TOKEN}/sendMessage")

    res.raise_for_status = raise_for_status
    return res


@pytest.fixture(autouse=True)
def telegram_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TOKEN)
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "999")


def test_diagnosis_saves_lead_and_sends_telegram(client, db):
    with patch("backend.routers.leads.requests.post", return_value=fake_response(200)) as post:
        response = client.post("/api/lead/diagnosis", json=payload())

    assert response.status_code == 200
    assert response.json()["status"] == "success"

    lead = db.query(DiagnosticoLead).one()
    assert lead.nombre == "Luis Prueba"
    assert lead.objetivo == "Fuerza funcional para el día a día"
    assert lead.telegram_enviado is True
    assert lead.telegram_error is None

    assert post.call_count == 1
    url = post.call_args.args[0]
    sent = post.call_args.kwargs["json"]
    assert TOKEN in url
    assert sent["chat_id"] == "999"
    assert sent["parse_mode"] == "HTML"
    assert "Luis Prueba" in sent["text"]
    assert "https://wa.me/34612345678" in sent["text"]
    assert post.call_args.kwargs["timeout"] > 0


@pytest.mark.parametrize("campo,valor", [
    ("goal", "Fuerza funcional para el día a día"),
    ("goal", "Mejorar físico (Ganar masa, bajar grasa...)"),
    ("goal", "Aprender habilidades (L-sit, pino, muscle-up)"),
    ("age", "18-25"),
    ("age", "26-34"),
    ("age", "+35"),
    ("level", "Llevo tiempo sin entrenar"),
    ("block", "Molestias o miedo a lesionarme"),
    ("block", "No tengo tiempo"),
])
def test_diagnosis_new_form_options_reach_telegram(client, db, campo, valor):
    with patch("backend.routers.leads.requests.post", return_value=fake_response(200)) as post:
        response = client.post("/api/lead/diagnosis", json=payload(**{campo: valor}))

    assert response.status_code == 200
    assert valor in post.call_args.kwargs["json"]["text"]


def test_diagnosis_escapes_html_symbols_in_name(client, db):
    with patch("backend.routers.leads.requests.post", return_value=fake_response(200)) as post:
        response = client.post("/api/lead/diagnosis", json=payload(name="Ana & <b>Co</b> <3"))

    assert response.status_code == 200
    text = post.call_args.kwargs["json"]["text"]
    assert "Ana &amp; &lt;b&gt;Co&lt;/b&gt; &lt;3" in text
    assert "<3" not in text

    # En la BD se guarda el texto original, sin escapar
    assert db.query(DiagnosticoLead).one().nombre == "Ana & <b>Co</b> <3"


def test_diagnosis_retries_in_plain_text_when_telegram_rejects_format(client, db):
    with patch("backend.routers.leads.requests.post",
               side_effect=[fake_response(400), fake_response(200)]) as post:
        response = client.post("/api/lead/diagnosis", json=payload(name="Ana & Co"))

    assert response.status_code == 200
    assert post.call_count == 2
    first, second = post.call_args_list[0].kwargs["json"], post.call_args_list[1].kwargs["json"]
    assert first["parse_mode"] == "HTML"
    assert "parse_mode" not in second
    assert "<b>" not in second["text"]
    assert "Ana & Co" in second["text"]
    assert db.query(DiagnosticoLead).one().telegram_enviado is True


def test_diagnosis_telegram_down_keeps_the_lead(client, db):
    error = requests.ConnectionError(f"HTTPSConnectionPool: url /bot{TOKEN}/sendMessage timed out")
    with patch("backend.routers.leads.requests.post", side_effect=error):
        response = client.post("/api/lead/diagnosis", json=payload())

    assert response.status_code == 200  # el visitante ve éxito: su contacto está guardado
    lead = db.query(DiagnosticoLead).one()
    assert lead.telegram_enviado is False
    assert lead.telegram_error
    assert TOKEN not in lead.telegram_error  # el token nunca se guarda


def test_diagnosis_telegram_http_error_keeps_the_lead(client, db):
    with patch("backend.routers.leads.requests.post", return_value=fake_response(500)):
        response = client.post("/api/lead/diagnosis", json=payload())

    assert response.status_code == 200
    lead = db.query(DiagnosticoLead).one()
    assert lead.telegram_enviado is False
    assert TOKEN not in lead.telegram_error


def test_diagnosis_without_telegram_credentials_keeps_the_lead(client, db, monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN")
    monkeypatch.delenv("TELEGRAM_CHAT_ID")

    with patch("backend.routers.leads.requests.post") as post:
        response = client.post("/api/lead/diagnosis", json=payload())

    assert response.status_code == 200
    post.assert_not_called()
    lead = db.query(DiagnosticoLead).one()
    assert lead.telegram_enviado is False
    assert "credenciales" in lead.telegram_error


def test_diagnosis_db_failure_still_notifies_telegram(client, db):
    with patch("backend.routers.leads.DiagnosticoLead", side_effect=Exception("BD caída")), \
         patch("backend.routers.leads.requests.post", return_value=fake_response(200)) as post:
        response = client.post("/api/lead/diagnosis", json=payload())

    assert response.status_code == 200
    assert post.call_count == 1  # al menos llega el aviso


def test_diagnosis_fails_loudly_only_when_db_and_telegram_both_fail(client, db):
    with patch("backend.routers.leads.DiagnosticoLead", side_effect=Exception("BD caída")), \
         patch("backend.routers.leads.requests.post", side_effect=requests.ConnectionError("sin red")):
        response = client.post("/api/lead/diagnosis", json=payload())

    assert response.status_code == 500


def test_diagnosis_validation(client, db):
    with patch("backend.routers.leads.requests.post") as post:
        missing = payload()
        del missing["goal"]
        assert client.post("/api/lead/diagnosis", json=missing).status_code == 422
        assert client.post("/api/lead/diagnosis", json=payload(name="x" * 201)).status_code == 422
        assert client.post("/api/lead/diagnosis", json=payload(name="")).status_code == 422

    post.assert_not_called()
    assert db.query(DiagnosticoLead).count() == 0
