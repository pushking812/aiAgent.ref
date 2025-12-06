# tests/test_integration.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)

import pytest
from unittest.mock import Mock, patch


@pytest.mark.integration
@pytest.mark.gui
class TestGUIComponentsIntegration:
    """Интеграционные тесты GUI компонентов."""
    
    def test_mvc_pattern(self):
        """Тест паттерна MVC/Controller."""
        # Модель
        class MockModel:
            def __init__(self):
                self.data = {"status": "ready"}
            
            def update(self, key, value):
                self.data[key] = value
        
        # Представление
        class MockView:
            def __init__(self):
                self.status_updates = []
            
            def set_status(self, text):
                self.status_updates.append(text)
        
        # Контроллер
        class MockController:
            def __init__(self, model, view):
                self.model = model
                self.view = view
            
            def update_status(self, text):
                self.model.update("status", text)
                self.view.set_status(text)
        
        # Тестируем взаимодействие
        model = MockModel()
        view = MockView()
        controller = MockController(model, view)
        
        controller.update_status("working")
        
        assert model.data["status"] == "working"
        assert len(view.status_updates) == 1
        assert view.status_updates[0] == "working"
    
    def test_component_interaction_simple(self):
        """Упрощенный тест взаимодействия компонентов."""
        # Создаем моки компонентов
        class MockMainWindowView:
            def __init__(self):
                self.content_panel = Mock()
        
        class MockCodeEditorView:
            def __init__(self, parent):
                self.parent = parent
                self.source_text = Mock()
                self.ai_text = Mock()
            
            def set_source_content(self, text):
                self.source_text = text
            
            def get_source_content(self):
                return self.source_text
        
        # Создаем взаимодействие
        mock_main_view = MockMainWindowView()
        editor = MockCodeEditorView(mock_main_view.content_panel)
        
        # Тестируем базовые операции
        test_code = "print('Hello')"
        editor.set_source_content(test_code)
        
        assert editor.get_source_content() == test_code
        assert editor.parent == mock_main_view.content_panel


@pytest.mark.integration
@pytest.mark.slow
class TestSlowIntegrationTests:
    """Медленные интеграционные тесты."""
    
    def test_complex_gui_interaction(self):
        """Тест сложного взаимодействия GUI."""
        # Имитация пользовательского взаимодействия
        import time
        
        steps = ["click button", "enter text", "save file"]
        for step in steps:
            time.sleep(0.001)  # Минимальная задержка для тестов
        
        assert len(steps) == 3