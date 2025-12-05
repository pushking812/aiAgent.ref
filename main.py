# main.py

import tkinter as tk
import logging

from gui.views.main_window_view import MainWindowView
from gui.views.code_editor_view import CodeEditorView
from gui.views.project_tree_view import ProjectTreeView
from gui.views.dialogs_view import DialogsView
from gui.controller.main_controller import MainController

from core.business.project_service import ProjectService
from core.business.code_service import CodeService
from core.business.analysis_service import AnalysisService
from core.data.project_repository import ProjectRepository
from core.data.ai_schema_parser import AISchemaParser

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai_code_assistant')


def setup_dependencies():
    """Настраивает зависимости приложения (Dependency Injection)."""
    # Репозитории и парсеры
    repository = ProjectRepository()
    schema_parser = AISchemaParser()
    
    # Сервисы
    project_service = ProjectService(repository, schema_parser)
    code_service = CodeService(repository)
    
    # Анализатор кода (заглушка - нужно реализовать)
    from core.business.analysis_service import IAnalysisService
    class SimpleAnalyzer:
        def run_analysis(self, project_path): return True
        def get_latest_report(self, project_path): return "Отчет анализа"
        def run_auto_refactor(self, project_path): return True
    
    analyzer = SimpleAnalyzer()
    analysis_service = AnalysisService(analyzer)
    
    return repository, project_service, code_service, analysis_service


def create_main_window(root):
    """Создает главное окно приложения со всеми компонентами."""
    # Создаем View компоненты
    main_view = MainWindowView(root)
    code_editor_view = CodeEditorView(main_view.content_panel)
    project_tree_view = ProjectTreeView(main_view.content_panel)
    dialogs_view = DialogsView(root)
    
    # Настраиваем layout
    main_view.pack(fill=tk.BOTH, expand=True)
    
    # Размещаем дерево проекта и редактор
    project_tree_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    code_editor_view.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # Настраиваем зависимости
    repository, project_service, code_service, analysis_service = setup_dependencies()
    
    # Создаем контроллер
    controller = MainController(
        main_window_view=main_view,
        code_editor_view=code_editor_view,
        project_tree_view=project_tree_view,
        dialogs_view=dialogs_view,
        project_service=project_service,
        code_service=code_service,
        analysis_service=analysis_service
    )
    
    return controller


def run_app():
    """Запускает приложение."""
    logger.info("Запуск AI Code Assistant")
    
    root = tk.Tk()
    root.title("AI Code Assistant")
    root.geometry("1200x800")
    
    try:
        controller = create_main_window(root)
        logger.info("Приложение успешно инициализировано")
    except Exception as e:
        logger.error("Ошибка инициализации приложения: %s", e)
        raise
    
    root.mainloop()
    logger.info("Приложение закрыто")


if __name__ == "__main__":
    run_app()