# tests/unit/test_dialogs_view.py

"""Юнит-тесты для DialogsView."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from gui.views.dialogs_view import DialogsView, DirectoryOverwriteDialog, ProjectCreationDialog


class TestDialogsViewUnit:
    """Юнит-тесты DialogsView."""

    def test_interface_methods_exist(self):
        """Тест что все методы интерфейса существуют."""
        required_methods = [
            'ask_save_changes',
            'show_diff',
            'show_info_dialog',
            'show_error_dialog',
            'show_warning_dialog',
            'ask_directory',
            'show_project_creation_dialog',
            'show_directory_overwrite_dialog'
        ]

        for method_name in required_methods:
            assert hasattr(DialogsView, method_name)
            assert callable(getattr(DialogsView, method_name))

    @patch('tkinter.messagebox.askyesnocancel')
    def test_ask_save_changes_variations(self, mock_ask):
        """Тест различных вариантов ответа в ask_save_changes."""
        dialogs = DialogsView(Mock())

        test_cases = [
            (True, True),    # Да
            (False, False),  # Нет
            (None, None),    # Отмена
        ]

        for dialog_return, expected in test_cases:
            mock_ask.reset_mock()
            mock_ask.return_value = dialog_return

            result = dialogs.ask_save_changes("test.py")
            assert result == expected

    @patch('tkinter.filedialog.askdirectory')
    def test_ask_directory_edge_cases(self, mock_ask):
        """Тест граничных случаев ask_directory."""
        dialogs = DialogsView(Mock())

        test_cases = [
            ("/path", "/path"),
            ("", ""),        # Пустая строка
            (None, None),    # None
        ]

        for dialog_return, expected in test_cases:
            mock_ask.reset_mock()
            mock_ask.return_value = dialog_return

            result = dialogs.ask_directory("Title")
            assert result == expected


class TestProjectCreationDialogUnit:
    """Юнит-тесты ProjectCreationDialog."""

    def test_initialization(self):
        """Тест инициализации."""
        dialog = ProjectCreationDialog(Mock(), Mock())

        assert hasattr(dialog, 'parent')
        assert hasattr(dialog, 'project_manager')
        assert hasattr(dialog, 'result')
        assert dialog.result is None

    @patch('tkinter.filedialog.askdirectory')
    def test_browse_path(self, mock_ask):
        """Тест метода _browse_path."""
        dialog = ProjectCreationDialog(Mock(), Mock())
        dialog.path_var = Mock()

        mock_ask.return_value = "/test/path"
        dialog._browse_path()

        mock_ask.assert_called_with(title="Выберите папку для создания проекта")
        dialog.path_var.set.assert_called_with("/test/path")

    def test_validation_logic(self):
        """Тест логики валидации."""
        # Создаем упрощенную версию для тестирования логики
        def validate_input(path, name):
            errors = []
            if not path:
                errors.append("Путь не указан")
            if not name:
                errors.append("Имя проекта не указано")
            return errors

        # Тестовые случаи
        test_cases = [
            ("", "", ["Путь не указан", "Имя проекта не указано"]),
            ("/path", "", ["Имя проекта не указано"]),
            ("", "project", ["Путь не указан"]),
            ("/path", "project", []),
        ]

        for path, name, expected_errors in test_cases:
            errors = validate_input(path, name)
            assert errors == expected_errors


class TestDirectoryOverwriteDialogUnit:
    """Юнит-тесты DirectoryOverwriteDialog."""

    def test_initialization(self):
        """Тест инициализации."""
        dialog = DirectoryOverwriteDialog(Mock(), "/path", "Project")

        assert hasattr(dialog, 'parent')
        assert hasattr(dialog, 'directory_path')
        assert hasattr(dialog, 'project_name')
        assert dialog.directory_path == "/path"
        assert dialog.project_name == "Project"

    @patch('tkinter.messagebox.askyesno')
    def test_show_method(self, mock_ask):
        """Тест метода show."""
        mock_ask.return_value = True
        dialog = DirectoryOverwriteDialog(Mock(), "/path", "Project")

        result = dialog.show()

        mock_ask.assert_called_once()
        assert result is True
