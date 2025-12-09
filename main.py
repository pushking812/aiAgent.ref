# main_simple.py - Упрощенная версия с использованием фабрики

import tkinter as tk
import logging

from gui.views.main_window_view import MainWindowView
from gui.views.project_tree_view import ProjectTreeView
from gui.views.code_editor_view import CodeEditorView
from gui.views.dialogs_view import DialogsView
from gui.views.analysis_view import AnalysisView
from gui.controller.main_controller import MainController

from core.factory import AppFactory

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Точка входа с использованием фабрики."""
    root = tk.Tk()
    root.title("AI Code Assistant v1.0 (с реальными сервисами)")
    root.geometry("1200x800")
    
    try:
        # Создание представлений
        main_window_view = MainWindowView(root)
        project_tree_view = ProjectTreeView(root)
        code_editor_view = CodeEditorView(root)
        dialogs_view = DialogsView(root)
        analysis_view = AnalysisView(root)
        
        # Создание всех сервисов через фабрику
        services = AppFactory.create_for_main()
        
        # Создание контроллера
        controller = MainController(
            main_window_view=main_window_view,
            code_editor_view=code_editor_view,
            project_tree_view=project_tree_view,
            dialogs_view=dialogs_view,
            analysis_view=analysis_view,
            project_service=services['project_service'],
            code_service=services['code_service'],
            analysis_service=services['analysis_service']
        )
        
        # Настраиваем дополнительные зависимости контроллера
        controller.ast_service = services['ast_service']
        controller.code_manager = services['code_manager']
        controller.change_manager = services['change_manager']
        controller.diff_engine = services['diff_engine']
        controller.project_creator = services['project_creator']
        controller.schema_parser = services['schema_parser']
        
        root.mainloop()
        
    except Exception as e:
        logging.error(f"Ошибка при запуске приложения: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()