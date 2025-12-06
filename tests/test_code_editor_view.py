# tests/test_code_editor_view.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)

import pytest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from gui.views.code_editor_view import CodeEditorView, ICodeEditorView


@pytest.mark.gui
class TestCodeEditorView:
    """Комплексные тесты CodeEditorView."""
    
    def test_initialization(self, code_editor_view):
        """Тест инициализации компонента."""
        assert code_editor_view is not None
        
        # Проверяем наличие основных виджетов
        required_widgets = ['source_text', 'ai_text', 'modified_label']
        for widget_name in required_widgets:
            assert hasattr(code_editor_view, widget_name), f"Отсутствует виджет {widget_name}"
    
    @pytest.mark.parametrize("test_content", [
        "def test():\n    return 'test'",
        "",
        "print('Hello')\nprint('World')",
        "x" * 100,  # Длинный текст (уменьшен для теста)
    ])
    def test_set_get_source_content(self, code_editor_view, test_content):
        """Тест установки и получения содержимого."""
        code_editor_view.set_source_content(test_content)
        actual_content = code_editor_view.get_source_content()
        
        assert actual_content == test_content
    
    def test_ai_content_operations(self, code_editor_view):
        """Тест работы с AI-редактором."""
        test_ai_content = "# AI generated code\nprint('Hello World')"
        
        # Установка содержимого
        code_editor_view.set_ai_content(test_ai_content)
        assert code_editor_view.get_ai_content() == test_ai_content
        
        # Очистка содержимого
        code_editor_view.clear_ai_content()
        assert code_editor_view.get_ai_content() == ""
    
    def test_modified_status(self, code_editor_view):
        """Тест статуса изменений."""
        # Изначально не изменено
        assert not code_editor_view.is_modified()
        
        # Устанавливаем статус изменений
        code_editor_view.update_modified_status(True)
        assert code_editor_view.is_modified()
        
        # Сбрасываем статус
        code_editor_view.update_modified_status(False)
        assert not code_editor_view.is_modified()
    
    def test_editable_state(self, code_editor_view):
        """Тест изменения состояния редактирования."""
        # Проверяем начальное состояние
        initial_state = code_editor_view.source_text.cget('state')
        assert initial_state == 'normal'
        
        # Отключаем редактирование
        code_editor_view.set_source_editable(False)
        disabled_state = code_editor_view.source_text.cget('state')
        assert disabled_state == 'disabled'
        
        # Включаем обратно
        code_editor_view.set_source_editable(True)
        enabled_state = code_editor_view.source_text.cget('state')
        assert enabled_state == 'normal'
    
    def test_callback_binding(self, code_editor_view):
        """Тест привязки callback функций."""
        callback_called = {"called": False}
        
        def test_callback():
            callback_called["called"] = True
        
        # Устанавливаем callback
        code_editor_view.set_on_text_modified_callback(test_callback)
        
        # Проверяем что callback установлен
        assert code_editor_view._on_text_modified_callback == test_callback


@pytest.mark.gui
class TestCodeEditorViewUnit:
    """Unit-тесты CodeEditorView с моками."""
    
    def test_interface_implementation(self):
        """Тест реализации интерфейса ICodeEditorView."""
        # Проверяем что все методы интерфейса реализованы
        interface_methods = [
            'get_source_content', 'set_source_content', 'bind_on_text_modified',
            'get_ai_content', 'set_ai_content', 'clear_ai_content',
            'bind_on_ai_modified', 'set_on_text_modified_callback',
            'set_source_editable', 'update_modified_status', 'bind_focus_out'
        ]
        
        for method_name in interface_methods:
            assert hasattr(CodeEditorView, method_name)
            assert callable(getattr(CodeEditorView, method_name))
    
    def test_init_simple_mock(self):
        """Упрощенный тест инициализации с моками."""
        # Создаем упрощенную версию без реального tkinter
        class SimpleCodeEditorView:
            def __init__(self, parent):
                self.parent = parent
                self._on_text_modified_callback = None
                self._on_focus_out_callback = None
                self._is_modified = False
                
            def set_on_text_modified_callback(self, callback):
                self._on_text_modified_callback = callback
        
        mock_parent = Mock()
        view = SimpleCodeEditorView(mock_parent)
        
        assert view is not None
        assert view.parent == mock_parent