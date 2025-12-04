# main.py

import tkinter as tk
from gui.views.main_window_view import MainWindowView
from gui.views.code_editor_view import CodeEditorView
from gui.controller.main_controller import MainController
from core.business.project_service import ProjectService
from core.data.project_repository import ProjectRepository
from core.data.ai_schema_parser import AISchemaParser

def run_app():
    root = tk.Tk()
    main_view = MainWindowView(root)
    code_editor_view = CodeEditorView(main_view)
    main_view.pack(fill=tk.BOTH, expand=True)
    repository = ProjectRepository()
    parser = AISchemaParser()
    service = ProjectService(repository, parser)
    controller = MainController(main_view, code_editor_view, service)
    root.mainloop()

if __name__ == "__main__":
    run_app()