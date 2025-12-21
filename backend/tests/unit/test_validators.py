# ==========================================
# backend/tests/unit/test_validators.py
# ==========================================
"""Tests para validadores"""
import pytest
from backend.utils.validators import (
    validar_email,
    validar_password,
    validar_nombre
)


def test_validar_email():
    assert validar_email("test@example.com") is True
    assert validar_email("invalid") is False


def test_validar_password():
    assert validar_password("password123") is True
    assert validar_password("123") is False


def test_validar_nombre():
    assert validar_nombre("Ana Sesena") is True
    assert validar_nombre("A") is False

