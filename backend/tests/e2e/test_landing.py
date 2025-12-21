"""Tests E2E para landing"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def test_home_page_loads(driver, base_url):
    """Test que home carga"""
    driver.get(base_url)
    assert "Petru" in driver.title

    navbar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "nav"))
    )
    assert navbar is not None


def test_hero_section(driver, base_url):
    """Test sección hero"""
    driver.get(base_url)

    hero = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "hero"))
    )
    assert hero.is_displayed()


def test_calendly_button(driver, base_url):
    """Test botón Calendly"""
    driver.get(base_url)

    buttons = driver.find_elements(By.CLASS_NAME, "btn-cta")
    assert len(buttons) > 0


def test_video_section(driver, base_url):
    """Test sección video"""
    driver.get(base_url)
    driver.execute_script("window.scrollTo(0, 800)")
    time.sleep(1)

    video_section = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "video"))
    )
    assert video_section is not None


def test_results_section(driver, base_url):
    """Test sección resultados"""
    driver.get(base_url)
    driver.execute_script("window.scrollTo(0, 1500)")
    time.sleep(1)

    results = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "resultados"))
    )
    assert results is not None

