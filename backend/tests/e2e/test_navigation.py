"""Tests E2E navegación"""
import pytest
from selenium.webdriver.common.by import By
import time


def test_navigate_to_info(driver, base_url):
    """Test ir a /info"""
    driver.get(base_url)

    info_buttons = driver.find_elements(By.CLASS_NAME, "btn-info")
    if info_buttons:
        info_buttons[0].click()
        time.sleep(2)
        assert "/info" in driver.current_url


def test_responsive_mobile(driver, base_url):
    """Test responsive móvil"""
    driver.set_window_size(375, 667)
    driver.get(base_url)
    time.sleep(2)

    navbar = driver.find_element(By.TAG_NAME, "nav")
    assert navbar is not None
