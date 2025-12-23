"""Configuración Selenium para tests E2E"""
import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def driver():
    """Chrome configurado para tests E2E (headless en CI)"""
    chrome_options = Options()

    # Siempre usar headless en GitHub Actions
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")

    # Configurar para CI
    if os.getenv("CI"):
        chrome_options.add_argument("--remote-debugging-port=9222")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(30)

    yield driver

    driver.quit()


@pytest.fixture
def base_url():
    """URL base del frontend"""
    return "http://localhost:5173"