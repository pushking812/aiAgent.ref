# tests/base_gui_test.py

import pytest
from unittest.mock import Mock, patch, MagicMock


class BaseGUITest:
    """Базовый класс для всех GUI тестов."""
    
    @pytest.fixture(autouse=True)
    def setup_logging(self, monkeypatch):
        """Настраивает логирование для тестов."""
        mock_logger = Mock()
        monkeypatch.setattr('gui.views.code_editor_view.logger', mock_logger)
        monkeypatch.setattr('gui.views.dialogs_view.logger', mock_logger)
        monkeypatch.setattr('gui.views.project_tree_view.logger', mock_logger)
        return mock_logger
    
    def create_mock_widget(self, widget_type="frame"):
        """Создает mock виджет."""
        mock_widget = MagicMock()
        mock_widget.pack = Mock()
        mock_widget.config = Mock()
        mock_widget.cget = Mock(return_value="normal")
        mock_widget.winfo_exists = Mock(return_value=True)
        mock_widget.winfo_children = Mock(return_value=[])
        
        if widget_type == "text":
            mock_widget.get = Mock(return_value="test content\n")
            mock_widget.delete = Mock()
            mock_widget.insert = Mock()
            mock_widget.see = Mock()
            mock_widget.update = Mock()
            mock_widget.bind = Mock()
            mock_widget.unbind = Mock()
        
        return mock_widget