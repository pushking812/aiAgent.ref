# tests/test_real_tkinter.py - ТОЛЬКО ЕСЛИ TKINTER ДОСТУПЕН

import pytest
import sys


# Пропускаем тест если tkinter не доступен
try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


@pytest.mark.skipif(not TKINTER_AVAILABLE, reason="tkinter не установлен")
@pytest.mark.gui
class TestRealTkinter:
    """Тесты с реальным tkinter (только если доступен)."""
    
    @pytest.fixture
    def tk_root(self):
        """Создает корневое окно tkinter."""
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        yield root
        try:
            root.destroy()
        except:
            pass
    
    def test_tkinter_available(self):
        """Тест доступности tkinter."""
        assert TKINTER_AVAILABLE
    
    def test_create_window(self, tk_root):
        """Тест создания окна."""
        tk_root.title("Test Window")
        tk_root.geometry("400x300")
        
        assert tk_root.winfo_exists()
    
    def test_create_widgets(self, tk_root):
        """Тест создания виджетов."""
        frame = tk.Frame(tk_root)
        label = tk.Label(frame, text="Test Label")
        button = tk.Button(frame, text="Test Button")
        
        frame.pack()
        label.pack()
        button.pack()
        
        # Проверяем, что виджеты созданы
        assert isinstance(frame, tk.Frame)
        assert isinstance(label, tk.Label)
        assert isinstance(button, tk.Button)