#!/usr/bin/env python3
"""
Главный модуль AI Code Assistant.
Использует обновленную архитектуру с AppContext.
"""

import tkinter as tk
import logging
from tkinter import ttk

from core.app_context import init_app_context, get_app_context
from gui.views.main_window_view import MainWindowView
from gui.views.code_editor_view import CodeEditorView
from gui.views.project_tree_view import ProjectTreeView
from gui.views.dialogs_view import DialogsView
from gui.views.analysis_view import AnalysisView
from gui.controller.main_controller import MainController
from gui.utils.ui_factory import ui_factory

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai_code_assistant')


class AIApp:
    """Главное приложение AI Code Assistant с обновленной архитектурой."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Code Assistant")
        self.root.geometry("1200x800")
        
        # Инициализация контекста приложения
        if not init_app_context():
            logger.error("Не удалось инициализировать AppContext")
            raise RuntimeError("Ошибка инициализации приложения")
        
        # Получение сервисов из контекста
        self.context = get_app_context()
        self._setup_ui()
        self._setup_controllers()
        
        logger.info("AI Code Assistant инициализирован с новой архитектурой")
    
    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        # Настраиваем стили
        ui_factory.setup_default_styles()
        
        # Создаем главное представление
        self.main_window_view = MainWindowView(self.root)
        
        # Создаем дочерние представления
        self.code_editor_view = CodeEditorView(None)  # Будет размещено в контроллере
        self.project_tree_view = ProjectTreeView(None)  # Будет размещено в контроллере
        self.dialogs_view = DialogsView(self.root)
        self.analysis_view = AnalysisView(None)  # Будет размещено в контроллере
        
        logger.debug("Представления созданы")
    
    def _setup_controllers(self):
        """Настраивает контроллеры с сервисами из контекста."""
        # Получаем сервисы из контекста
        project_service = self.context.get_project_service()
        code_service = self.context.get_code_service()
        analysis_service = self.context.get_analysis_service()
        
        # Создаем главный контроллер
        self.main_controller = MainController(
            main_window_view=self.main_window_view,
            code_editor_view=self.code_editor_view,
            project_tree_view=self.project_tree_view,
            dialogs_view=self.dialogs_view,
            analysis_view=self.analysis_view,
            project_service=project_service,
            code_service=code_service,
            analysis_service=analysis_service
        )
        
        logger.info("Контроллеры настроены с сервисами из AppContext")
    
    def run(self):
        """Запускает главный цикл приложения."""
        logger.info("Запуск AI Code Assistant...")
        
        # Центрируем окно
        self.root.eval('tk::PlaceWindow . center')
        
        # Запускаем главный цикл
        self.root.mainloop()
        
        logger.info("AI Code Assistant завершен")
    
    def show_context_info(self):
        """Показывает информацию о контексте приложения (для отладки)."""
        services = self.context.get_all_services()
        info = "=== Контекст приложения ===\n"
        for name, service in services.items():
            info += f"{name}: {type(service).__name__}\n"
        
        logger.info(info)
        return info


def main():
    """Точка входа в приложение."""
    try:
        app = AIApp()
        app.show_context_info()  # Для отладки
        app.run()
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()