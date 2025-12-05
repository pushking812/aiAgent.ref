# tests/test_code_editor_view.py

import tkinter as tk
import pytest
from unittest.mock import Mock, patch
from gui.views.code_editor_view import CodeEditorView


class TestCodeEditorView:
    """Тесты для CodeEditorView"""
    
    @pytest.fixture
    def root(self):
        """Создает корневое окно для тестов."""
        return tk.Tk()
    
    @pytest.fixture
    def editor(self, root):
        """Создает экземпляр CodeEditorView."""
        return CodeEditorView(root)
    
    def test_initialization(self, editor):
        """Тест инициализации редактора."""
        assert editor is not None
        assert hasattr(editor, 'source_text')
        assert hasattr(editor, 'ai_text')
        assert hasattr(editor, 'modified_label')
    
    def test_get_set_source_content(self, editor):
        """Тест установки и получения содержимого исходного кода."""
        test_content = "def test():\n    return 'test'"
        
        # Устанавливаем содержимое
        editor.set_source_content(test_content)
        
        # Получаем содержимое
        content = editor.get_source_content()
        
        assert content == test_content
        assert editor._last_content == test_content
    
    def test_get_set_ai_content(self, editor):
        """Тест установки и получения AI-кода."""
        test_content = "# AI generated code\nprint('Hello')"
        
        editor.set_ai_content(test_content)
        content = editor.get_ai_content()
        
        assert content == test_content
    
    def test_clear_ai_content(self, editor):
        """Тест очистки AI-редактора."""
        editor.set_ai_content("test content")
        editor.clear_ai_content()
        
        content = editor.get_ai_content()
        assert content == ""
    
    def test_modified_status(self, editor):
        """Тест обновления статуса изменений."""
        # Изначально не изменено
        assert not editor.is_modified()
        
        # Симулируем изменение
        editor.update_modified_status(True)
        assert editor.is_modified()
        
        # Сбрасываем статус
        editor.update_modified_status(False)
        assert not editor.is_modified()
    
    def test_set_source_editable(self, editor):
        """Тест включения/выключения редактирования."""
        # Проверяем, что редактор по умолчанию редактируемый
        state = editor.source_text.cget('state')
        assert state == 'normal'
        
        # Выключаем редактирование
        editor.set_source_editable(False)
        state = editor.source_text.cget('state')
        assert state == 'disabled'
        
        # Включаем обратно
        editor.set_source_editable(True)
        state = editor.source_text.cget('state')
        assert state == 'normal'
    
    def test_text_modified_callback(self, editor):
        """Тест callback при изменении текста."""
        callback_mock = Mock()
        editor.set_on_text_modified_callback(callback_mock)
        
        # Симулируем изменение текста
        editor.set_source_content("test")
        
        # Проверяем, что callback не вызвался при программной установке
        callback_mock.assert_not_called()
        
        # Тестируем обработчик изменений
        editor._on_text_modified()
        callback_mock.assert_called_once()
    
    def test_focus_out_binding(self, editor):
        """Тест привязки обработчика потери фокуса."""
        callback_mock = Mock()
        editor.bind_focus_out(callback_mock)
        
        assert editor._on_focus_out_callback == callback_mock
    
    @patch('gui.views.code_editor_view.time.time')
    def test_text_change_throttling(self, mock_time, editor):
        """Тест троттлинга изменений текста."""
        mock_time.side_effect = [0.0, 0.1, 0.7]  # Время изменяется
        
        callback_mock = Mock()
        editor.set_on_text_modified_callback(callback_mock)
        
        # Первое изменение
        editor._last_content = ""
        editor._on_text_modified()
        callback_mock.assert_called_once()
        callback_mock.reset_mock()
        
        # Второе изменение слишком быстро - должно быть проигнорировано
        editor._on_text_modified()
        callback_mock.assert_not_called()
    
    def test_text_widget_configuration(self, editor):
        """Тест конфигурации текстовых виджетов."""
        # Проверяем, что табуляция настроена
        tabs = editor.source_text.cget('tabs')
        assert tabs is not None
        
        # Проверяем оба редактора
        assert editor.source_text is not None
        assert editor.ai_text is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])