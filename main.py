# main.py - Главный файл приложения

import tkinter as tk
import logging
from tkinter import ttk

from gui.views.main_window_view import MainWindowView
from gui.views.project_tree_view import ProjectTreeView
from gui.views.code_editor_view import CodeEditorView
from gui.views.dialogs_view import DialogsView
from gui.views.analysis_view import AnalysisView
from gui.controller.main_controller import MainController

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Точка входа в приложение с точной структурой как в старом коде."""
    root = tk.Tk()
    root.title("AI Code Assistant")
    root.geometry("1200x800")  # Тот же размер окна
    
    try:
        # Создание представлений
        main_window_view = MainWindowView(root)
        project_tree_view = ProjectTreeView(root)
        code_editor_view = CodeEditorView(root)
        dialogs_view = DialogsView(root)
        analysis_view = AnalysisView(root)
        
        # Создание сервисов (заглушки)
        from core.business.project_service import IProjectService
        from core.business.code_service import ICodeService
        from core.business.analysis_service import IAnalysisService
        
        class MockProjectService(IProjectService):
            def __init__(self):
                self.project_path = None
                self.repository = type('obj', (object,), {
                    'get_project_structure': lambda: {'modules': [], 'files': {}, 'directories': []},
                    'read_file': lambda x: f"# Содержимое файла: {x}\nprint('Hello World')",
                    'current_file_path': None
                })()
            
            def create_project(self, path: str, name: str) -> bool:
                self.project_path = f"{path}/{name}"
                return True
            
            def open_project(self, path: str) -> bool:
                self.project_path = path
                return True
            
            def close_project(self) -> bool:
                self.project_path = None
                return True
            
            def create_structure_from_ai(self, schema: str) -> bool:
                return True
        
        class MockCodeService(ICodeService):
            def save_current_file(self, content: str) -> bool:
                return True
            
            def add_ai_code(self, ai_code: str) -> bool:
                return True
            
            def replace_code(self, file_path: str, node_name: str, new_code: str) -> bool:
                return True
            
            def add_code(self, file_path: str, code: str, position: str = 'end') -> bool:
                return True
            
            def delete_code(self, file_path: str, entity_name: str) -> bool:
                return True
        
        class MockAnalysisService(IAnalysisService):
            def analyze_code(self, project_path: str):
                return [
                    {'type': 'info', 'message': 'Анализ начат', 'file': '', 'line': 0},
                    {'type': 'warning', 'message': 'Неиспользуемый импорт', 'file': 'main.py', 'line': 5},
                    {'type': 'error', 'message': 'Синтаксическая ошибка', 'file': 'utils.py', 'line': 10},
                    {'type': 'success', 'message': 'Анализ завершен', 'file': '', 'line': 0}
                ]
            
            def get_report(self, project_path: str) -> str:
                return "Отчет анализа: найдено 2 проблемы"
            
            def auto_refactor(self, project_path: str) -> bool:
                return True
        
        project_service = MockProjectService()
        code_service = MockCodeService()
        analysis_service = MockAnalysisService()
        
        # Создание контроллера (он сам настроит структуру GUI)
        controller = MainController(
            main_window_view=main_window_view,
            code_editor_view=code_editor_view,
            project_tree_view=project_tree_view,
            dialogs_view=dialogs_view,
            analysis_view=analysis_view,
            project_service=project_service,
            code_service=code_service,
            analysis_service=analysis_service
        )
        
        root.mainloop()
        
    except Exception as e:
        logging.error(f"Ошибка при запуске приложения: {e}")
        raise

if __name__ == "__main__":
    main()