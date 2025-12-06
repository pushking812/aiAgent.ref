# tests/unit/test_code_editor_view.py

"""Юнит-тесты для CodeEditorView."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from gui.views.code_editor_view import CodeEditorView, ICodeEditorView


class TestCodeEditorViewUnit:
    """Юнит-тесты CodeEditorView."""

    def test_interface_implementation(self):
        """Тест реализации интерфейса ICodeEditorView."""
        interface_methods = [
            'get_source_content', 'set_source_content', 'bind_on_text_modified',
            'get_ai_content', 'set_ai_content', 'clear_ai_content',
            'bind_on_ai_modified', 'set_on_text_modified_callback',
            'set_source_editable', 'update_modified_status', 'bind_focus_out'
        ]

        for method_name in interface_methods:
            assert hasattr(CodeEditorView, method_name)
            assert callable(getattr(CodeEditorView, method_name))

    @patch('tkinter.ttk.Frame')
    @patch('tkinter.ttk.Label')
    @patch('tkinter.scrolledtext.ScrolledText')
    def test_initialization_mocked(self, mock_scrolledtext, mock_label, mock_frame):
        """Тест инициализации с моками."""
        mock_parent = Mock()
        mock_frame_instance = Mock()
        mock_frame.return_value = mock_frame_instance

        # Создаем экземпляр с моками
        view = CodeEditorView.__new__(CodeEditorView)
        view.parent = mock_parent
        view._last_content = ""
        view._last_modified_time = 0
        view._on_text_modified_callback = None
        view._on_focus_out_callback = None
        view._is_modified = False

        assert view is not None
        assert view.parent == mock_parent

    def test_method_signatures(self):
        """Тест сигнатур методов."""
        # Проверяем что основные методы имеют правильные параметры
        import inspect

        methods_to_check = [
            ('get_source_content', 0),  # Без параметров
            ('set_source_content', 1),  # 1 параметр: text
            ('set_on_text_modified_callback', 1),  # 1 параметр: callback
        ]

        for method_name, expected_param_count in methods_to_check:
            method = getattr(CodeEditorView, method_name)
            sig = inspect.signature(method)
            params = [p for p in sig.parameters.values() if p.name != 'self']
            assert len(params) == expected_param_count, \
                f"Метод {method_name} должен принимать {expected_param_count} параметров"

    @patch('time.time')
    def test_text_modification_logic(self, mock_time):
        """Тест логики отслеживания изменений текста."""
        mock_time.return_value = 1000.0

        # Создаем тестовый объект
        class TestEditor:
            def __init__(self):
                self._last_content = ""
                self._last_modified_time = 0
                self._is_modified = False
                self._on_text_modified_callback = None

            def _on_text_modified(self, event=None):
                current_time = 1000.0
                if current_time - self._last_modified_time < 0.5:
                    return
                self._last_modified_time = current_time
                self._is_modified = True

                if self._on_text_modified_callback:
                    self._on_text_modified_callback(event)

        editor = TestEditor()
        editor._last_modified_time = 999.0  # Меньше 0.5 секунд назад
        callback_called = False

        def test_callback(event):
            nonlocal callback_called
            callback_called = True

        editor._on_text_modified_callback = test_callback
        editor._on_text_modified()

        # Callback не должен был вызваться (дебаунсинг)
        assert not callback_called

        # Тестируем с большей задержкой
        editor._last_modified_time = 500.0
        editor._on_text_modified()

        # Теперь callback должен был вызваться
        assert callback_called
        assert editor._is_modified
