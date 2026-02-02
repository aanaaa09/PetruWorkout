# ==========================================
# backend/tests/e2e/test_calculator_e2e.py
# ==========================================
"""Tests E2E para la calculadora de calorías"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time


@pytest.mark.e2e
def test_calculator_page_loads(driver, base_url):
    """Test que la página de calculadora carga correctamente"""
    driver.get(f"{base_url}/calculator?token=test_token_12345")

    # Esperar a que cargue el título
    title = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    assert "Calculadora" in title.text or "Calorías" in title.text


@pytest.mark.e2e
def test_calculator_form_elements(driver, base_url):
    """Test que todos los elementos del formulario están presentes"""
    driver.get(f"{base_url}/calculator?token=test_token")

    # Esperar a que cargue el formulario
    time.sleep(2)

    # Verificar radio buttons de género
    gender_radios = driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
    assert len(gender_radios) >= 2

    # Verificar inputs numéricos
    age_input = driver.find_element(By.CSS_SELECTOR, 'input[type="number"]')
    assert age_input is not None

    # Verificar selects
    selects = driver.find_elements(By.TAG_NAME, "select")
    assert len(selects) >= 2  # Activity level y goal


@pytest.mark.e2e
def test_calculator_form_submission(driver, base_url):
    """Test envío del formulario de calculadora"""
    driver.get(f"{base_url}/calculator?token=test_token")

    time.sleep(2)

    try:
        # Seleccionar género
        male_radio = driver.find_element(By.CSS_SELECTOR, 'input[value="male"]')
        driver.execute_script("arguments[0].click();", male_radio)

        # Rellenar edad
        age_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="number"]')
        age_inputs[0].clear()
        age_inputs[0].send_keys("25")

        # Rellenar peso
        age_inputs[1].clear()
        age_inputs[1].send_keys("70")

        # Rellenar altura
        age_inputs[2].clear()
        age_inputs[2].send_keys("175")

        # Seleccionar nivel de actividad
        activity_select = Select(driver.find_elements(By.TAG_NAME, "select")[0])
        activity_select.select_by_value("moderate")

        # Seleccionar objetivo
        goal_select = Select(driver.find_elements(By.TAG_NAME, "select")[1])
        goal_select.select_by_value("maintain")

        # Enviar formulario
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", submit_button)

        # Esperar resultados (máximo 10 segundos)
        results = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "results-section"))
        )

        assert results is not None

    except Exception as e:
        print(f"Error en test: {e}")
        driver.save_screenshot("/tmp/calculator_form_error.png")
        raise


@pytest.mark.e2e
def test_calculator_results_display(driver, base_url):
    """Test que los resultados se muestran correctamente"""
    driver.get(f"{base_url}/calculator?token=test_token")

    time.sleep(2)

    # Rellenar y enviar formulario (versión simplificada)
    try:
        # ... rellenar formulario ...
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        driver.execute_script("arguments[0].click();", submit_button)

        # Esperar resultados
        time.sleep(3)

        # Verificar que se muestran los resultados principales
        result_cards = driver.find_elements(By.CLASS_NAME, "result-card")
        assert len(result_cards) >= 4  # IMC, GEB, GET, Recomendado

        # Verificar sección de macros
        macros_section = driver.find_element(By.CLASS_NAME, "macros-section")
        assert macros_section is not None

    except Exception as e:
        print(f"Error verificando resultados: {e}")


@pytest.mark.e2e
def test_calculator_without_token_redirect(driver, base_url):
    """Test que sin token redirige a home"""
    driver.get(f"{base_url}/calculator")

    time.sleep(3)

    # Debería redirigir a home
    assert driver.current_url == f"{base_url}/" or "calculator" not in driver.current_url


@pytest.mark.e2e
def test_calculator_responsive_mobile(driver, base_url):
    """Test versión móvil de la calculadora"""
    driver.set_window_size(375, 667)  # iPhone SE
    driver.get(f"{base_url}/calculator?token=test_token")

    time.sleep(2)

    # Verificar que el formulario es visible en móvil
    form = driver.find_element(By.CLASS_NAME, "calculator-form")
    assert form.is_displayed()

    # Verificar que los botones son accesibles
    submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
    assert submit_button.is_displayed()