# gui/views/project_tree_view.py

from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk
import os
import re
from typing import Dict, List, Optional, Any, Callable
import logging

logger = logging.getLogger('ai_code_assistant')


class IProjectTreeView(ABC):
    def setup_tree(self): pass
    def fill_tree(self, project_structure): pass
    def get_selected_item(self): pass
    def highlight_search_results(self, items): pass
    def expand_all(self): pass
    def collapse_all(self): pass
    def bind_on_select(self, callback): pass
    def search_elements(self, search_text: str) -> List[str]: pass
    def set_on_tree_select_callback(self, callback: Callable): pass


class ProjectTreeView(ttk.Frame, IProjectTreeView):
    """
    Расширенная реализация дерева проекта с поиском по точечной нотации.
    """
    
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
        """
        Инициализация колонок и настроек отображения дерева.
        """
        self.tree.heading("#0", text="Структура проекта")
        logger.debug("Дерево проекта настроено")

    def fill_tree(self, project_structure):
        """
        Заполнить дерево проектной структурой (modules, files).
        Ожидает project_structure в виде dict/ProjectModel.
        """
        self.tree.delete(*self.tree.get_children())
        self._item_map.clear()
        self.all_tree_items = []
        
        # Пример для структуры: {"modules": [...], "files": {...}}
        modules = project_structure.get("modules", [])
        files = project_structure.get("files", {})
        
        # Сначала добавляем модули
        for module in modules:
            module_id = self.tree.insert("", "end", text=module, tags=('module',))
            self._item_map[module_id] = {"type": "module", "name": module, "path": module}
            self.all_tree_items.append(module_id)
        
        # Затем добавляем файлы
        for file_path in files:
            # Найдём модуль-родителя, если файл внутри модуля
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
            
            # Для Python файлов можно добавить элементы кода
            if file_path.endswith('.py'):
                self._add_code_elements(file_id, file_path, files[file_path])
        
        logger.debug("Дерево проекта заполнено: modules=%s, files=%s", len(modules), len(files))

    def _add_code_elements(self, parent_id: str, file_path: str, file_content: str):
        """Добавляет элементы кода к файлу в дереве (базовая реализация)"""
        # В новой архитектуре парсинг AST должен быть в сервисе
        # Здесь просто отмечаем, что файл можно парсить
        pass

    def _find_tree_item_by_name(self, name):
        for item_id, item_data in self._item_map.items():
            if item_data.get("name") == name:
                return item_id
        return ""

    def get_selected_item(self) -> Dict:
        """
        Получить выделенный элемент в дереве.
        Возвращает dict: {'id', 'type', 'name', 'path', 'full_path'}
        """
        selection = self.tree.focus()
        if selection in self._item_map:
            item_data = self._item_map[selection].copy()
            item_data['id'] = selection
            return item_data
        return {}

    def highlight_search_results(self, items: List[str]):
        """
        Подсвечивает результаты поиска.
        """
        # Сбрасываем предыдущую подсветку
        for item_id in self.all_tree_items:
            self.tree.item(item_id, tags=())
        
        # Подсвечиваем найденные элементы
        for item_id in items:
            self.tree.item(item_id, tags=('found',))
        
        self.tree.tag_configure('found', background='#e6f3ff')
        
        # Прокручиваем к первому результату
        if items:
            self._expand_to_item(items[0])

    def _expand_to_item(self, item_id):
        """Раскрывает дерево до указанного элемента"""
        parent_id = self.tree.parent(item_id)
        while parent_id:
            self.tree.item(parent_id, open=True)
            parent_id = self.tree.parent(parent_id)
        
        self.tree.selection_set(item_id)
        self.tree.focus(item_id)
        self.tree.see(item_id)

    def expand_all(self):
        """Рекурсивно раскрыть все ветки дерева."""
        for item in self.tree.get_children():
            self._expand_recursive(item)

    def _expand_recursive(self, item):
        self.tree.item(item, open=True)
        for child in self.tree.get_children(item):
            self._expand_recursive(child)

    def collapse_all(self):
        """Рекурсивно свернуть все ветки дерева."""
        for item in self.tree.get_children():
            self._collapse_recursive(item)

    def _collapse_recursive(self, item):
        self.tree.item(item, open=False)
        for child in self.tree.get_children(item):
            self._collapse_recursive(child)

    def bind_on_select(self, callback):
        """Привязать обработчик выбора элемента дерева."""
        self.tree.bind("<<TreeviewSelect>>", callback)

    def set_on_tree_select_callback(self, callback: Callable):
        """Устанавливает callback для обработки выбора в дереве"""
        self._on_tree_select_callback = callback
        self.tree.bind('<<TreeviewSelect>>', lambda e: callback())

    def search_elements(self, search_text: str) -> List[str]:
        """
        Выполняет поиск элементов в дереве с поддержкой точечной нотации.
        """
        search_text_lower = search_text.lower()
        results = []
        
        # Проверяем, использует ли запрос точечную нотацию
        if '.' in search_text_lower:
            # Используем точечную нотацию
            parts = search_text_lower.split('.')
            
            for item_id in self.all_tree_items:
                full_path = self._get_item_full_path(item_id).lower()
                if self._matches_dot_notation(full_path, parts):
                    results.append(item_id)
        else:
            # Обычный поиск
            for item_id in self.all_tree_items:
                item_text = self.tree.item(item_id, 'text').lower()
                if search_text_lower in item_text:
                    results.append(item_id)
        
        logger.debug("Поиск завершен: запрос='%s', найдено=%s", search_text, len(results))
        return results

    def _get_item_full_path(self, item_id: str) -> str:
        """Возвращает полный путь элемента в формате module.class.method"""
        path_parts = []
        current_id = item_id
        
        while current_id:
            item_text = self.tree.item(current_id, 'text')
            path_parts.append(item_text)
            current_id = self.tree.parent(current_id)
        
        path_parts.reverse()
        return '.'.join(path_parts)

    def _matches_dot_notation(self, full_path: str, search_parts: List[str]) -> bool:
        """
        Проверяет соответствие полного пути поисковому запросу с точками.
        """
        # Очищаем путь от эмодзи и форматирования
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
        """Очищает путь для поиска - убирает эмодзи и специальные символы"""
        # Убираем эмодзи и специальные символы
        cleaned = re.sub(r'[🔹📦📝⚡🏛️📋❓()]', '', path)
        # Убираем лишние пробелы и точки
        cleaned = re.sub(r'\s+', '', cleaned)
        cleaned = cleaned.strip('.')
        return cleaned.lower()

    def get_all_items(self) -> List[str]:
        """Возвращает список всех ID элементов дерева"""
        return self.all_tree_items