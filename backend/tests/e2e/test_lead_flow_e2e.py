# ==========================================
# backend/tests/e2e/test_lead_flow_e2e.py
# ==========================================
"""Tests E2E para el flujo de registro de leads"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


@pytest.mark.e2e
def test_hero_gift_button_opens_modal(driver, base_url):
    """Test que el botón de regalo abre el modal"""
    driver.get(base_url)

    # Esperar a que cargue el hero
    hero = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "hero"))
    )

    # Buscar y hacer click en el botón de regalo
    gift_button = driver.find_element(By.CLASS_NAME, "btn-gift")
    driver.execute_script("arguments[0].scrollIntoView(true);", gift_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", gift_button)

    # Esperar a que aparezca el modal
    modal = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "modal-content"))
    )

    assert modal.is_displayed()


@pytest.mark.e2e
def test_lead_registration_form_validation(driver, base_url):
    """Test validación del formulario de registro"""
    driver.get(base_url)

    # Abrir modal
    gift_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-gift"))
    )
    driver.execute_script("arguments[0].click();", gift_button)

    time.sleep(1)

    # Intentar enviar sin email
    submit_button = driver.find_element(By.CLASS_NAME, "btn-submit")
    driver.execute_script("arguments[0].click();", submit_button)

    # Debería mostrar validación del navegador
    email_input = driver.find_element(By.CLASS_NAME, "email-input")
    validation_message = email_input.get_attribute("validationMessage")

    assert validation_message != ""  # Hay mensaje de validación


@pytest.mark.e2e
def test_lead_registration_invalid_email(driver, base_url):
    """Test registro con email inválido"""
    driver.get(base_url)

    # Abrir modal
    gift_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-gift"))
    )
    driver.execute_script("arguments[0].click();", gift_button)

    time.sleep(1)

    # Ingresar email inválido
    email_input = driver.find_element(By.CLASS_NAME, "email-input")
    email_input.send_keys("email-invalido")

    # Aceptar privacidad
    privacy_checkbox = driver.find_element(By.ID, "privacy")
    driver.execute_script("arguments[0].click();", privacy_checkbox)

    # Intentar enviar
    submit_button = driver.find_element(By.CLASS_NAME, "btn-submit")
    driver.execute_script("arguments[0].click();", submit_button)

    time.sleep(2)

    # Debería mostrar mensaje de error
    try:
        error_message = driver.find_element(By.CLASS_NAME, "error-text")
        assert error_message.is_displayed()
    except:
        # O validación HTML5
        validation_message = email_input.get_attribute("validationMessage")
        assert validation_message != ""


@pytest.mark.e2e
def test_lead_registration_privacy_required(driver, base_url):
    """Test que la política de privacidad es obligatoria"""
    driver.get(base_url)

    # Abrir modal
    gift_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-gift"))
    )
    driver.execute_script("arguments[0].click();", gift_button)

    time.sleep(1)

    # Ingresar email válido
    email_input = driver.find_element(By.CLASS_NAME, "email-input")
    email_input.send_keys("test@example.com")

    # NO marcar el checkbox de privacidad

    # Intentar enviar
    submit_button = driver.find_element(By.CLASS_NAME, "btn-submit")
    driver.execute_script("arguments[0].click();", submit_button)

    time.sleep(1)

    # El formulario no debería enviarse
    modal = driver.find_element(By.CLASS_NAME, "modal-content")
    assert modal.is_displayed()  # Modal sigue abierto


@pytest.mark.e2e
def test_modal_close_button(driver, base_url):
    """Test que el botón cerrar funciona"""
    driver.get(base_url)

    # Abrir modal
    gift_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-gift"))
    )
    driver.execute_script("arguments[0].click();", gift_button)

    time.sleep(1)

    # Cerrar modal
    close_button = driver.find_element(By.CLASS_NAME, "modal-close")
    driver.execute_script("arguments[0].click();", close_button)

    time.sleep(1)

    # Modal no debería estar visible
    modals = driver.find_elements(By.CLASS_NAME, "modal-overlay")
    if modals:
        assert not modals[0].is_displayed()


@pytest.mark.e2e
def test_privacy_link_opens_policy(driver, base_url):
    """Test que el link de privacidad abre la política"""
    driver.get(base_url)

    # Abrir modal
    gift_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-gift"))
    )
    driver.execute_script("arguments[0].click();", gift_button)

    time.sleep(1)

    # Hacer click en el link de política de privacidad
    privacy_link = driver.find_element(By.CLASS_NAME, "link-button")
    driver.execute_script("arguments[0].click();", privacy_link)

    time.sleep(2)

    # Debería navegar a /info?legal=privacy
    assert "info" in driver.current_url
    assert "legal=privacy" in driver.current_url or "Privacidad" in driver.page_source


@pytest.mark.e2e
def test_responsive_modal_mobile(driver, base_url):
    """Test modal en vista móvil"""
    driver.set_window_size(375, 667)  # iPhone SE
    driver.get(base_url)

    # Abrir modal
    gift_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-gift"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", gift_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", gift_button)

    time.sleep(1)

    # Modal debería ser visible y adaptado
    modal = driver.find_element(By.CLASS_NAME, "modal-content")
    assert modal.is_displayed()

    # El formulario debería ser accesible
    email_input = driver.find_element(By.CLASS_NAME, "email-input")
    assert email_input.is_displayed()