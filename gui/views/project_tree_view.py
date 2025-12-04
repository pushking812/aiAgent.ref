# gui/views/project_tree_view.py

from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk

class IProjectTreeView(ABC):
    def setup_tree(self): pass
    def fill_tree(self, project_structure): pass
    def get_selected_item(self): pass
    def highlight_search_results(self, items): pass
    def expand_all(self): pass
    def collapse_all(self): pass
    def bind_on_select(self, callback): pass

class ProjectTreeView(ttk.Frame, IProjectTreeView):
    """
    Реализация дерева проекта: визуализация и взаимодействие.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(self)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.heading("#0", text="Структура проекта")
        self._item_map = {}  # Сопоставление ID → данных, для быстрого доступа

    def setup_tree(self):
        """
        Инициализация колонок и настроек отображения дерева
        (можно расширить для доп. столбцов).
        """
        self.tree.heading("#0", text="Структура проекта")
        # self.tree["columns"] = ("type",) — если нужны ещё столбцы

    def fill_tree(self, project_structure):
        """
        Заполнить дерево проектной структурой (modules, files).
        Ожидает project_structure в виде dict/ProjectModel.
        """
        self.tree.delete(*self.tree.get_children())
        self._item_map.clear()
        # Пример для структуры: {"modules": [...], "files": {...}}
        modules = project_structure.get("modules", [])
        files = project_structure.get("files", {})

        for module in modules:
            module_id = self.tree.insert("", "end", text=module)
            self._item_map[module_id] = {"type": "module", "name": module}

        for file_path in files:
            # Найдём модуль-родителя, если файл внутри модуля
            parent_id = ""
            for module in modules:
                if file_path.startswith(module):
                    parent_id = self._find_tree_item_by_name(module)
            file_id = self.tree.insert(parent_id, "end", text=file_path)
            self._item_map[file_id] = {"type": "file", "name": file_path}

    def _find_tree_item_by_name(self, name):
        for item_id, item_data in self._item_map.items():
            if item_data.get("name") == name:
                return item_id
        return ""

    def get_selected_item(self):
        """
        Получить выделенный элемент в дереве (dict: type, name).
        """
        selection = self.tree.focus()
        return self._item_map.get(selection, {})

    def highlight_search_results(self, items):
        """
        Подсветить или раскрыть найденные элементы (по имени/пути).
        """
        for item_id, item_data in self._item_map.items():
            if item_data.get("name") in items:
                self.tree.see(item_id)
                self.tree.selection_set(item_id)

    def expand_all(self):
        """
        Рекурсивно раскрыть все ветки дерева.
        """
        for item in self.tree.get_children():
            self._expand_recursive(item)

    def _expand_recursive(self, item):
        self.tree.item(item, open=True)
        for child in self.tree.get_children(item):
            self._expand_recursive(child)

    def collapse_all(self):
        """
        Рекурсивно свернуть все ветки дерева.
        """
        for item in self.tree.get_children():
            self._collapse_recursive(item)

    def _collapse_recursive(self, item):
        self.tree.item(item, open=False)
        for child in self.tree.get_children(item):
            self._collapse_recursive(child)

    def bind_on_select(self, callback):
        """
        Привязать обработчик выбора элемента дерева.
        """
        self.tree.bind("<<TreeviewSelect>>", callback)