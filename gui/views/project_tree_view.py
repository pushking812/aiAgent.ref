# gui/views/project_tree_view.py

import logging
import os
import re
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger('ai_code_assistant')


class IProjectTreeView:
    """Интерфейс для дерева проекта."""
    def setup_tree(self): pass
    def fill_tree(self, project_structure): pass
    def get_selected_item(self) -> Dict: pass
    def highlight_search_results(self, items: List[str]): pass
    def expand_all(self): pass
    def collapse_all(self): pass
    def bind_on_select(self, callback: Callable): pass
    def search_elements(self, search_text: str) -> List[str]: pass
    def set_on_tree_select_callback(self, callback: Callable): pass


class ProjectTreeView(ttk.Frame, IProjectTreeView):
    """Реализация дерева проекта."""

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        # Создаем фрейм для дерева
        tree_frame = ttk.LabelFrame(self, text="Структура проекта")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # Создаем Treeview
        self.tree = ttk.Treeview(tree_container, show='tree')
        tree_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Инициализация
        self.search_results: List[str] = []
        self.current_search_index = -1
        self._item_map: Dict[str, Dict] = {}  # Сопоставление ID → данных
        self._on_tree_select_callback: Optional[Callable] = None
        self.all_tree_items: List[str] = []

        logger.debug("ProjectTreeView инициализирован")

    def setup_tree(self):
        """Настраивает дерево."""
        self.tree.heading("#0", text="Структура проекта")

    def fill_tree(self, project_structure: Dict[str, Any]):
        """Заполняет дерево структурой проекта."""
        self.tree.delete(*self.tree.get_children())
        self._item_map.clear()
        self.all_tree_items = []

        # Получаем данные
        modules = project_structure.get("modules", [])
        files = project_structure.get("files", {})

        # Добавляем модули
        for module in modules:
            module_id = self.tree.insert("", "end", text=module, tags=('module',))
            self._item_map[module_id] = {
                "type": "module",
                "name": module,
                "path": module,
                "full_path": module
            }
            self.all_tree_items.append(module_id)

        # Добавляем файлы
        for file_path in files:
            # Находим родителя (модуль)
            parent_id = ""
            for module in modules:
                if file_path.startswith(module):
                    parent_id = self._find_tree_item_by_name(module)

            # Создаем элемент файла
            file_name = os.path.basename(file_path)
            file_id = self.tree.insert(parent_id, "end", text=file_name, tags=('file',))
            self._item_map[file_id] = {
                "type": "file",
                "name": file_name,
                "path": file_path,
                "full_path": file_path
            }
            self.all_tree_items.append(file_id)

        logger.debug("Дерево заполнено: modules=%s, files=%s", len(modules), len(files))

    def _find_tree_item_by_name(self, name: str) -> str:
        """Находит элемент дерева по имени."""
        for item_id, item_data in self._item_map.items():
            if item_data.get("name") == name:
                return item_id
        return ""

    def get_selected_item(self) -> Dict:
        """Возвращает выбранный элемент."""
        selection = self.tree.focus()
        if selection in self._item_map:
            item_data = self._item_map[selection].copy()
            item_data['id'] = selection
            return item_data
        return {}

    def highlight_search_results(self, items: List[str]):
        """Подсвечивает результаты поиска."""
        # Сбрасываем подсветку
        for item_id in self.all_tree_items:
            self.tree.item(item_id, tags=())

        # Подсвечиваем найденные элементы
        for item_id in items:
            self.tree.item(item_id, tags=('found',))

        self.tree.tag_configure('found', background='#e6f3ff')

        # Прокручиваем к первому результату
        if items:
            self._expand_to_item(items[0])

    def _expand_to_item(self, item_id: str):
        """Раскрывает дерево до элемента."""
        parent_id = self.tree.parent(item_id)
        while parent_id:
            self.tree.item(parent_id, open=True)
            parent_id = self.tree.parent(parent_id)

        self.tree.selection_set(item_id)
        self.tree.focus(item_id)
        self.tree.see(item_id)

    def expand_all(self):
        """Раскрывает все ветки."""
        for item in self.tree.get_children():
            self._expand_recursive(item)

    def _expand_recursive(self, item: str):
        """Рекурсивно раскрывает ветку."""
        self.tree.item(item, open=True)
        for child in self.tree.get_children(item):
            self._expand_recursive(child)

    def collapse_all(self):
        """Сворачивает все ветки."""
        for item in self.tree.get_children():
            self._collapse_recursive(item)

    def _collapse_recursive(self, item: str):
        """Рекурсивно сворачивает ветку."""
        self.tree.item(item, open=False)
        for child in self.tree.get_children(item):
            self._collapse_recursive(child)

    def bind_on_select(self, callback: Callable):
        """Привязывает обработчик выбора."""
        self.tree.bind("<<TreeviewSelect>>", callback)

    def search_elements(self, search_text: str) -> List[str]:
        """Ищет элементы в дереве."""
        search_lower = search_text.lower()
        results = []

        # Поиск по точечной нотации
        if '.' in search_lower:
            parts = search_lower.split('.')
            for item_id in self.all_tree_items:
                full_path = self._get_item_full_path(item_id).lower()
                if self._matches_dot_notation(full_path, parts):
                    results.append(item_id)
        else:
            # Обычный поиск
            for item_id in self.all_tree_items:
                item_text = self.tree.item(item_id, 'text').lower()
                if search_lower in item_text:
                    results.append(item_id)

        return results

    def _get_item_full_path(self, item_id: str) -> str:
        """Возвращает полный путь элемента."""
        path_parts = []
        current_id = item_id

        while current_id:
            item_text = self.tree.item(current_id, 'text')
            path_parts.append(item_text)
            current_id = self.tree.parent(current_id)

        path_parts.reverse()
        return '.'.join(path_parts)

    def _matches_dot_notation(self, full_path: str, search_parts: List[str]) -> bool:
        """Проверяет соответствие точечной нотации."""
        clean_path = self._clean_search_path(full_path)
        path_parts = clean_path.split('.')

        if len(search_parts) > len(path_parts):
            return False

        # Ищем последовательное соответствие
        for i in range(len(path_parts) - len(search_parts) + 1):
            match = True
            for j, search_part in enumerate(search_parts):
                if i + j >= len(path_parts) or search_part not in path_parts[i + j]:
                    match = False
                    break
            if match:
                return True

        return False

    def _clean_search_path(self, path: str) -> str:
        """Очищает путь для поиска."""
        cleaned = re.sub(r'[🔹📦📝⚡🏛️📋❓()]', '', path)
        cleaned = re.sub(r'\s+', '', cleaned)
        cleaned = re.sub(r'\.{2,}', '.', cleaned)  # замена 2+ точек на одну
        cleaned = cleaned.strip('.')
        return cleaned.lower()

    def set_on_tree_select_callback(self, callback: Callable):
        """Устанавливает callback для выбора."""
        self._on_tree_select_callback = callback
        self.tree.bind('<<TreeviewSelect>>', lambda e: callback())

    def get_all_items(self) -> List[str]:
        """Возвращает все элементы дерева."""
        return self.all_tree_items
