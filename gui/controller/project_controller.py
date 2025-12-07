# gui/controller/project_controller.py

import tkinter as tk
from tkinter import ttk

from gui.views.main_window_view import IMainWindowView
from gui.views.project_tree_view import IProjectTreeView
from gui.views.dialogs_view import DialogsView
from core.business.project_service import IProjectService
from core.models.project_model import ProjectModel

class ProjectController:
    """
    Контроллер управления проектом:
    действия над жизненным циклом проекта, структурой, синхронизацией.
    """
    def __init__(
        self,
        main_window_view: IMainWindowView,
        project_tree_view: IProjectTreeView,
        dialogs_view: DialogsView,
        project_service: IProjectService,
    ):
        self.main_window_view = main_window_view
        self.project_tree_view = project_tree_view
        self.dialogs_view = dialogs_view
        self.project_service = project_service

        # Привязка событий дерева проекта
        self.project_tree_view.bind_on_select(self.on_tree_item_selected)

    def on_create_project(self, path: str, name: str):
        """
        Создать новый проект и отобразить в дереве.
        """
        success = self.project_service.create_project(path, name)
        if success:
            self.main_window_view.set_status(f"Проект создан: {name}")
            self._refresh_project_tree()
            self.main_window_view.show_info("Успех", f"Проект '{name}' успешно создан!")
        else:
            self.main_window_view.show_error("Ошибка", "Не удалось создать проект!")

    def on_open_project(self, path: str):
        """
        Открыть проект по указанному пути.
        """
        success = self.project_service.open_project(path)
        if success:
            self.main_window_view.set_status(f"Открыт проект: {path}")
            self._refresh_project_tree()
        else:
            self.main_window_view.show_error("Ошибка", "Не удалось открыть проект!")

    def on_save_project(self):
        """
        Сохранить проект (может быть вызван при выходе/автосохранении).
        """
        success = self.project_service.save_project()
        if success:
            self.main_window_view.set_status("Проект сохранён")
        else:
            self.main_window_view.show_error("Ошибка", "Не удалось сохранить проект!")

    def on_close_project(self):
        """
        Закрыть текущий проект.
        """
        success = self.project_service.close_project()
        if success:
            self.main_window_view.set_status("Проект закрыт")
            self.project_tree_view.setup_tree()
        else:
            self.main_window_view.show_error("Ошибка", "Не удалось закрыть проект.")

    def on_create_structure_from_ai(self, schema: str):
        """
        Сгенерировать структуру проекта из AI-схемы.
        """
        success = self.project_service.create_structure_from_ai(schema)
        if success:
            self.main_window_view.show_info("Структура проекта", "Структура успешно создана!")
            self._refresh_project_tree()
        else:
            self.main_window_view.show_error("Ошибка", "Ошибка создания структуры.")

    def on_tree_item_selected(self, event=None):
        """
        Обработка выбора элемента в дереве проекта.
        """
        item = self.project_tree_view.get_selected_item()
        item_type = item.get("type")
        item_name = item.get("name")
        if item_type == "file":
            self.main_window_view.set_status(f"Выбран файл: {item_name}")
        elif item_type == "module":
            self.main_window_view.set_status(f"Выбран модуль: {item_name}")

    def on_highlight_search(self, search_results):
        """
        Подсветить найденные элементы дерева.
        """
        self.project_tree_view.highlight_search_results(search_results)

    def _refresh_project_tree(self):
        """
        Перечитать структуру проекта и обновить дерево.
        """
        structure = self.project_service.repository.get_project_structure()
        self.project_tree_view.fill_tree(structure)