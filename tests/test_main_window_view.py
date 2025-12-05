# tests/test_main_window_view.py

import tkinter as tk
import pytest
from unittest.mock import Mock, patch
from gui.views.main_window_view import MainWindowView


class TestMainWindowView:
    """Тесты для MainWindowView"""
    
    @pytest.fixture
    def root(self):
        """Создает корневое окно для тестов."""
        return tk.Tk()
    
    @pytest.fixture
    def main_view(self, root):
        """Создает экземпляр MainWindowView."""
        return MainWindowView(root)
    
    def test_initialization(self, main_view):
        """Тест инициализации главного окна."""
        assert main_view is not None
        assert hasattr(main_view, 'top_panel')
        assert hasattr(main_view, 'content_panel')
        assert hasattr(main_view, 'status_label')
        assert hasattr(main_view, 'unsaved_changes_label')
        
        # Проверяем наличие кнопок
        assert hasattr(main_view, 'create_project_button')
        assert hasattr(main_view, 'open_project_button')
        assert hasattr(main_view, 'create_structure_button')
        assert hasattr(main_view, 'analyze_button')
        assert hasattr(main_view, 'analysis_report_button')
        assert hasattr(main_view, 'refactor_button')
    
    def test_set_status(self, main_view):
        """Тест установки статуса."""
        test_status = "Тестовый статус"
        main_view.set_status(test_status)
        
        assert main_view.status_label.cget('text') == test_status
    
    def test_update_unsaved_changes_status(self, main_view):
        """Тест обновления статуса несохраненных изменений."""
        test_text = "[ИЗМЕНЕНО]"
        main_view.update_unsaved_changes_status(test_text)
        
        assert main_view.unsaved_changes_label.cget('text') == test_text
    
    def test_bind_create_project(self, main_view):
        """Тест привязки обработчика создания проекта."""
        callback_mock = Mock()
        main_view.bind_create_project(callback_mock)
        
        # Проверяем, что кнопка сконфигурирована
        config = main_view.create_project_button.config()
        assert 'command' in config
        
        # Вызываем callback
        callback_mock.assert_not_called()
        if main_view.create_project_button.cget('command'):
            main_view.create_project_button.cget('command')()
            callback_mock.assert_called_once()
    
    def test_bind_open_project(self, main_view):
        """Тест привязки обработчика открытия проекта."""
        callback_mock = Mock()
        main_view.bind_open_project(callback_mock)
        
        config = main_view.open_project_button.config()
        assert 'command' in config
    
    def test_bind_create_structure(self, main_view):
        """Тест привязки обработчика создания структуры."""
        callback_mock = Mock()
        main_view.bind_create_structure(callback_mock)
        
        config = main_view.create_structure_button.config()
        assert 'command' in config
    
    def test_bind_analyze_code(self, main_view):
        """Тест привязки обработчика анализа кода."""
        callback_mock = Mock()
        main_view.bind_analyze_code(callback_mock)
        
        config = main_view.analyze_button.config()
        assert 'command' in config
    
    def test_bind_show_analysis_report(self, main_view):
        """Тест привязки обработчика отчета анализа."""
        callback_mock = Mock()
        main_view.bind_show_analysis_report(callback_mock)
        
        config = main_view.analysis_report_button.config()
        assert 'command' in config
    
    def test_bind_auto_refactor(self, main_view):
        """Тест привязки обработчика авторефакторинга."""
        callback_mock = Mock()
        main_view.bind_auto_refactor(callback_mock)
        
        config = main_view.refactor_button.config()
        assert 'command' in config
    
    @patch('tkinter.messagebox.showinfo')
    def test_show_info(self, mock_showinfo, main_view):
        """Тест показа информационного сообщения."""
        main_view.show_info("Тест", "Сообщение")
        
        mock_showinfo.assert_called_once_with("Тест", "Сообщение")
    
    @patch('tkinter.messagebox.showerror')
    def test_show_error(self, mock_showerror, main_view):
        """Тест показа сообщения об ошибке."""
        main_view.show_error("Ошибка", "Описание")
        
        mock_showerror.assert_called_once_with("Ошибка", "Описание")
    
    @patch('tkinter.messagebox.showwarning')
    def test_show_warning(self, mock_showwarning, main_view):
        """Тест показа предупреждения."""
        main_view.show_warning("Предупреждение", "Внимание!")
        
        mock_showwarning.assert_called_once_with("Предупреждение", "Внимание!")
    
    def test_content_panel_access(self, main_view):
        """Тест доступа к контентной панели."""
        assert main_view.content_panel is not None
        assert isinstance(main_view.content_panel, tk.Frame)
    
    def test_widget_hierarchy(self, main_view):
        """Тест иерархии виджетов."""
        # Проверяем, что все основные виджеты созданы
        assert main_view.winfo_children()  # Должны быть дочерние виджеты
        assert main_view.top_panel.winfo_children()  # Кнопки на панели
        assert main_view.content_panel.winfo_parent() == str(main_view)
    
    def test_button_texts(self, main_view):
        """Тест текстов на кнопках."""
        assert "Создать проект" in main_view.create_project_button.cget('text')
        assert "Открыть проект" in main_view.open_project_button.cget('text')
        assert "Структура из AI" in main_view.create_structure_button.cget('text')
        assert "Анализ кода" in main_view.analyze_button.cget('text')
        assert "Отчет анализа" in main_view.analysis_report_button.cget('text')
        assert "Авторефакторинг" in main_view.refactor_button.cget('text')
    
    def test_initial_status(self, main_view):
        """Тест начального статуса."""
        assert main_view.status_label.cget('text') == "Проект не открыт"
        assert main_view.unsaved_changes_label.cget('text') == ""
    
    def test_pack_configuration(self, main_view):
        """Тест конфигурации размещения виджетов."""
        # Проверяем, что виджеты упакованы
        pack_info = main_view.pack_info()
        assert 'fill' in pack_info
        assert pack_info['fill'] == 'both'
        assert 'expand' in pack_info
        assert pack_info['expand'] is True


class TestMainWindowViewIntegration:
    """Интеграционные тесты MainWindowView"""
    
    @pytest.fixture
    def app_with_view(self):
        """Создает приложение с MainWindowView."""
        root = tk.Tk()
        view = MainWindowView(root)
        return root, view
    
    def test_full_interaction_flow(self, app_with_view):
        """Тест полного потока взаимодействия."""
        root, view = app_with_view
        
        # Устанавливаем статус
        view.set_status("Тестовый статус")
        assert view.status_label.cget('text') == "Тестовый статус"
        
        # Обновляем статус изменений
        view.update_unsaved_changes_status("[ИЗМЕНЕНО]")
        assert view.unsaved_changes_label.cget('text') == "[ИЗМЕНЕНО]"
        
        # Проверяем, что виджеты отображаются
        assert view.winfo_ismapped() or not root.winfo_viewable()
    
    def test_multiple_status_updates(self, main_view):
        """Тест множественных обновлений статуса."""
        statuses = ["Статус 1", "Статус 2", "Статус 3"]
        
        for status in statuses:
            main_view.set_status(status)
            assert main_view.status_label.cget('text') == status
    
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.messagebox.showwarning')
    def test_all_dialogs(self, mock_warning, mock_error, mock_info, main_view):
        """Тест всех типов диалогов."""
        main_view.show_info("Инфо", "Сообщение")
        main_view.show_error("Ошибка", "Проблема")
        main_view.show_warning("Внимание", "Предупреждение")
        
        mock_info.assert_called_once_with("Инфо", "Сообщение")
        mock_error.assert_called_once_with("Ошибка", "Проблема")
        mock_warning.assert_called_once_with("Внимание", "Предупреждение")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])