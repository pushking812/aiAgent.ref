# tests/test_tkinter_fixes.py

"""
Исправления для тестов с Tkinter объектами.
"""

import pytest
import tkinter as tk


class TestTkinterComparisons:
    """Тесты для правильного сравнения Tkinter объектов."""
    
    def test_tkinter_color_comparison(self):
        """Тест сравнения цветов Tkinter."""
        root = tk.Tk()
        root.withdraw()
        
        label = tk.Label(root, text="Test", foreground="red")
        
        # Tkinter возвращает объект цвета, а не строку
        color_obj = label.cget('foreground')
        
        # Правильные способы сравнения:
        assert color_obj is not None
        assert str(color_obj) == 'red'  # Можно преобразовать в строку
        
        # Или сравнить через repr
        assert repr(color_obj) == repr('red')
        
        root.destroy()
    
    def test_tkinter_show_value_comparison(self):
        """Тест сравнения значений 'show' в Treeview."""
        root = tk.Tk()
        root.withdraw()
        
        tree = tk.ttk.Treeview(root)
        show_value = tree.cget('show')
        
        # Tkinter может возвращать кортеж или строку
        assert show_value is not None
        
        if isinstance(show_value, tuple):
            # В некоторых версиях возвращает кортеж
            assert show_value == ('tree', 'headings') or show_value == ('tree',)
        else:
            # В других - строку
            assert show_value in ['tree', 'tree headings']
        
        root.destroy()


@pytest.fixture
def tk_color_comparison_helper():
    """Хелпер для сравнения цветов Tkinter."""
    
    def compare_colors(color1, color2):
        """Сравнивает два цвета Tkinter."""
        # Оба могут быть объектами или строками
        str1 = str(color1).lower().strip()
        str2 = str(color2).lower().strip()
        return str1 == str2
    
    return compare_colors


@pytest.fixture
def tk_show_value_helper():
    """Хелпер для сравнения значений 'show'."""
    
    def compare_show_values(value1, value2):
        """Сравнивает значения 'show'."""
        # Обрабатываем кортежи и строки
        if isinstance(value1, tuple):
            str1 = ''.join(value1)
        else:
            str1 = str(value1)
        
        if isinstance(value2, tuple):
            str2 = ''.join(value2)
        else:
            str2 = str(value2)
        
        return str1 == str2
    
    return compare_show_values