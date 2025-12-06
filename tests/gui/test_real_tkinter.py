# tests/gui/test_real_tkinter.py

"""Тесты с реальным Tkinter (только если доступен)."""

import pytest


@pytest.mark.tkinter
@pytest.mark.gui
class TestRealTkinter:
    """Тесты с реальным tkinter."""

    @pytest.fixture
    def tk_root(self):
        """Создает корневое окно tkinter."""
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        yield root
        try:
            root.destroy()
        except:
            pass

    def test_tkinter_available(self, tk_root):
        """Тест доступности tkinter."""
        import tkinter as tk
        assert tk_root is not None
        assert tk_root.winfo_exists()

    def test_create_basic_widgets(self, tk_root):
        """Тест создания базовых виджетов."""
        import tkinter as tk
        from tkinter import ttk

        # Создаем различные виджеты
        frame = tk.Frame(tk_root)
        ttk_frame = ttk.Frame(tk_root)
        label = tk.Label(frame, text="Test Label")
        button = tk.Button(frame, text="Test Button")
        entry = tk.Entry(frame)

        # Проверяем создание
        assert isinstance(frame, tk.Frame)
        assert isinstance(ttk_frame, ttk.Frame)
        assert isinstance(label, tk.Label)
        assert isinstance(button, tk.Button)
        assert isinstance(entry, tk.Entry)

    def test_widget_properties(self, tk_root):
        """Тест свойств виджетов."""
        import tkinter as tk

        # Создаем виджет
        label = tk.Label(tk_root, text="Hello", foreground="red")

        # Проверяем свойства
        assert label.cget('text') == "Hello"
        assert label.cget('foreground') == "red"

        # Изменяем свойства
        label.config(text="World", foreground="blue")
        assert label.cget('text') == "World"
        assert label.cget('foreground') == "blue"

    def test_widget_packing(self, tk_root):
        """Тест упаковки виджетов."""
        import tkinter as tk

        # Создаем контейнеры
        main_frame = tk.Frame(tk_root)
        inner_frame = tk.Frame(main_frame)

        # Создаем виджеты
        label1 = tk.Label(inner_frame, text="Label 1")
        label2 = tk.Label(inner_frame, text="Label 2")
        button = tk.Button(inner_frame, text="Button")

        # Упаковываем
        main_frame.pack(fill=tk.BOTH, expand=True)
        inner_frame.pack(fill=tk.X, padx=10, pady=10)
        label1.pack(side=tk.LEFT, padx=5)
        label2.pack(side=tk.LEFT, padx=5)
        button.pack(side=tk.RIGHT, padx=5)

        # Проверяем что виджеты созданы
        children = inner_frame.winfo_children()
        assert len(children) == 3
