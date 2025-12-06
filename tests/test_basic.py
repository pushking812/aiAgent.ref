# tests/test_basic.py

import pytest


# Простые тесты без зависимостей
def test_basic():
    """Базовый тест."""
    assert 1 + 1 == 2


@pytest.mark.unit
def test_unit():
    """Unit-тест."""
    result = "test".upper()
    assert result == "TEST"


@pytest.mark.gui
def test_gui_marker():
    """Тест с маркером gui."""
    # Простой тест без реального GUI
    assert True


@pytest.mark.slow
def test_slow():
    """Медленный тест (будет пропущен по умолчанию)."""
    # Этот тест будет пропущен если не указать --runslow
    assert True


class TestClass:
    """Тестовый класс."""
    
    @pytest.mark.unit
    def test_class_method(self):
        """Метод класса."""
        assert "hello".capitalize() == "Hello"
    
    @pytest.mark.gui
    def test_gui_in_class(self):
        """GUI тест в классе."""
        assert len("test") == 4