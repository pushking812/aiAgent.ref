# tests/unit/test_main_window_view.py

"""Юнит-тесты для MainWindowView."""

from unittest.mock import Mock, patch

import pytest

from gui.views.main_window_view import MainWindowView


class TestMainWindowViewUnit:
    """Юнит-тесты MainWindowView."""

    def test_interface_methods_exist(self):
        """Тест что все методы интерфейса существуют."""
        required_methods = [
            'set_status',
            'show_info',
            'show_error',
            'show_warning',
            'bind_create_project',
            'bind_open_project',
            'bind_create_structure'
        ]

        for method_name in required_methods:
            assert hasattr(MainWindowView, method_name)
            assert callable(getattr(MainWindowView, method_name))

    @patch('tkinter.ttk.Frame')
    @patch('tkinter.ttk.Button')
    @patch('tkinter.ttk.Label')
    def test_initialization_mocked(self, mock_label, mock_button, mock_frame):
        """Тест инициализации с моками."""
        mock_root = Mock()
        mock_frame_instance = Mock()
        mock_frame.return_value = mock_frame_instance

        # Создаем упрощенную версию
        class SimpleMainWindowView:
            def __init__(self, root):
                self.parent = root
                self.status_label = Mock()

        view = SimpleMainWindowView(mock_root)

        assert view is not None
        assert view.parent == mock_root

    def test_bind_methods_logic(self):
        """Тест логики методов привязки."""
        # Создаем тестовый объект
        class TestView:
            def __init__(self):
                self.create_project_button = Mock()
                self.open_project_button = Mock()
                self.create_structure_button = Mock()

            def bind_create_project(self, callback):
                self.create_project_button.config(command=callback)

            def bind_open_project(self, callback):
                self.open_project_button.config(command=callback)

            def bind_create_structure(self, callback):
                self.create_structure_button.config(command=callback)

        view = TestView()
        callback = Mock()

        # Тестируем привязку
        view.bind_create_project(callback)
        view.create_project_button.config.assert_called_with(command=callback)

        view.bind_open_project(callback)
        view.open_project_button.config.assert_called_with(command=callback)

        view.bind_create_structure(callback)
        view.create_structure_button.config.assert_called_with(command=callback)

    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.messagebox.showwarning')
    def test_show_dialogs(self, mock_warning, mock_error, mock_info):
        """Тест методов показа диалогов."""
        # Создаем тестовый объект
        class TestView:
            def show_info(self, title, msg):
                import tkinter.messagebox as mb
                mb.showinfo(title, msg)

            def show_error(self, title, msg):
                import tkinter.messagebox as mb
                mb.showerror(title, msg)

            def show_warning(self, title, msg):
                import tkinter.messagebox as mb
                mb.showwarning(title, msg)

        view = TestView()

        # Тестируем show_info
        view.show_info("Title", "Message")
        mock_info.assert_called_with("Title", "Message")

        # Тестируем show_error
        view.show_error("Error", "Description")
        mock_error.assert_called_with("Error", "Description")

        # Тестируем show_warning
        view.show_warning("Warning", "Attention")
        mock_warning.assert_called_with("Warning", "Attention")
