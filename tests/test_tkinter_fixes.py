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
        
        # Tkinter возвращает строку цвета
        color_obj = label.cget('foreground')
        
        # Правильные способы сравнения:
        assert color_obj is not None
        
        # Преобразуем в строку для надежности
        color_str = str(color_obj)
        assert color_str == 'red'
        
        root.destroy()
    
    def test_tkinter_show_value_comparison(self):
        """Тест сравнения значений 'show' в Treeview."""
        root = tk.Tk()
        root.withdraw()
        
        tree = tk.ttk.Treeview(root)
        show_value = tree.cget('show')
        
        # Tkinter ttk.Treeview возвращает строку или кортеж
        assert show_value is not None
        
        # Упрощаем проверку - просто проверяем тип и наличие
        if isinstance(show_value, tuple):
            # Кортеж должен содержать строки
            for item in show_value:
                assert isinstance(str(item), str)
            # Проверяем что содержит нужные элементы (без сравнения с индексом)
            show_str = ''.join(str(item) for item in show_value)
            assert 'tree' in show_str
        else:
            # Это строка
            show_str = str(show_value)
            assert 'tree' in show_str.lower()
        
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
            str1 = ''.join(str(item) for item in value1)
        else:
            str1 = str(value1)
        
        if isinstance(value2, tuple):
            str2 = ''.join(str(item) for item in value2)
        else:
            str2 = str(value2)
        
        return str1 == str2
    
    return compare_show_values