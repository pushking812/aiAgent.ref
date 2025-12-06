# tests/base_gui_test.py

"""Базовый класс для всех GUI тестов."""

from unittest.mock import MagicMock, Mock, patch

import pytest


class BaseGUITest:
    """Базовый класс для всех GUI тестов."""

    @pytest.fixture(autouse=True)
    def setup_logging(self, monkeypatch):
        """Настраивает логирование для тестов."""
        mock_logger = Mock()
        # Патчим логгеры во всех модулях views
        modules_to_patch = [
            'gui.views.code_editor_view.logger',
            'gui.views.dialogs_view.logger',
            'gui.views.project_tree_view.logger',
            'gui.views.main_window_view.logger'
        ]

        for module_path in modules_to_patch:
            monkeypatch.setattr(module_path, mock_logger)

        return mock_logger

    @pytest.fixture
    def mock_tk_parent(self):
        """Создает mock родительского окна."""
        parent = Mock()
        parent.winfo_x = Mock(return_value=100)
        parent.winfo_y = Mock(return_value=100)
        parent.winfo_width = Mock(return_value=800)
        parent.winfo_height = Mock(return_value=600)
        parent.winfo_exists = Mock(return_value=True)
        return parent

    @pytest.fixture
    def mock_project_manager(self):
        """Создает mock менеджера проектов."""
        return Mock()
