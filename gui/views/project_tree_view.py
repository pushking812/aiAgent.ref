# gui/views/project_tree_view.py

import logging
import os
import re
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple

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
    def find_next(self): pass
    def setup_search_panel(self, parent): pass
    def setup_tree_buttons(self, parent): pass
    def _get_display_info(self, node) -> Tuple[str, str]: pass
    def _get_directory_structure(self, directory: str) -> Dict: pass
    def load_project_structure(self, directory: str): pass
    def get_tree_widget(self) -> ttk.Treeview: pass


class ProjectTreeView(ttk.Frame, IProjectTreeView):
    """Реализация дерева проекта с точной структурой как в старом коде."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)  # Заполняем весь родительский контейнер
        
        # Основной контейнер для дерева (левая панель)
        self.tree_container = ttk.Frame(self, width=300)  # Фиксированная ширина 300px как в старом коде
        self.tree_container.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))  # Отступ справа 5px
        self.tree_container.pack_propagate(False)  # Фиксируем ширину
        
        # Инициализация
        self.search_results: List[str] = []
        self.current_search_index = -1
        self._item_map: Dict[str, Dict] = {}
        self._on_tree_select_callback: Optional[Callable] = None
        self.all_tree_items: List[str] = []
        
        logger.debug("ProjectTreeView инициализирован")

    def setup_search_panel(self, parent):
        """Создает панель поиска как в старом коде."""
        search_frame = ttk.LabelFrame(parent, text="Быстрый поиск")
        search_frame.pack(fill=tk.X, pady=(0, 5))  # Отступ снизу 5px
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)  # Внутренние отступы
        
        self.search_hint = ttk.Label(
            search_frame, 
            text="Введите имя элемента (module.function, module.class.method)", 
            foreground="gray", 
            font=('Arial', 8)
        )
        self.search_hint.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Привязка событий поиска
        self.search_entry.bind('<KeyRelease>', self._on_search_changed)

    def setup_tree_buttons(self, parent):
        """Создает кнопки управления деревом как в старом коде."""
        tree_buttons_config = [
            {'text': '👁️', 'tooltip': 'Раскрыть все ветки', 'square': True},
            {'text': '🙈', 'tooltip': 'Свернуть все ветки', 'square': True},
            {'text': '🔍', 'tooltip': 'Следующий результат', 'square': True},
        ]
        
        tree_buttons_frame = ttk.LabelFrame(parent, text="Дерево")
        tree_buttons_frame.pack(fill=tk.X, pady=(0, 5))  # Отступ снизу 5px
        
        # Создаем кнопки
        self.expand_all_button = ttk.Button(tree_buttons_frame, text="👁️", width=3)
        self.expand_all_button.pack(side=tk.LEFT, padx=2)
        
        self.collapse_all_button = ttk.Button(tree_buttons_frame, text="🙈", width=3)
        self.collapse_all_button.pack(side=tk.LEFT, padx=2)
        
        self.find_next_button = ttk.Button(tree_buttons_frame, text="🔍", width=3)
        self.find_next_button.pack(side=tk.LEFT, padx=2)

    def setup_tree(self):
        """Создает само дерево проекта как в старом коде."""
        tree_frame = ttk.LabelFrame(self.tree_container, text="Структура проекта")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Создаем Treeview с колонками как в старом коде
        self.tree = ttk.Treeview(tree_container, show='tree', columns=('path', 'type'))
        
        # Настраиваем колонки
        self.tree.heading("#0", text="Структура проекта")
        self.tree.column("#0", width=250, minwidth=150)  # Ширина как в старом коде
        self.tree.column("path", width=0, stretch=False)  # Скрытая колонка
        self.tree.column("type", width=0, stretch=False)  # Скрытая колонка
        
        # Полоса прокрутки
        tree_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Размещение
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Настройка тегов для подсветки
        self.tree.tag_configure('found', background='#e6f3ff')
        self.tree.tag_configure('module', foreground='blue')
        self.tree.tag_configure('file', foreground='green')
        self.tree.tag_configure('directory', foreground='#8B4513')  # Коричневый для директорий
        
    def _on_search_changed(self, event):
        """Обработчик изменения текста в поле поиска."""
        search_text = self.search_var.get().strip()
        
        if not search_text:
            self.search_hint.config(
                text="Введите имя элемента (module.function, module.class.method)", 
                foreground="gray")
            self.highlight_search_results([])
            self.search_results = []
            return
        
        self.search_results = self.search_elements(search_text)
        
        if self.search_results:
            self.search_hint.config(
                text=f"Найдено элементов: {len(self.search_results)}", 
                foreground="green")
            self.highlight_search_results(self.search_results)
            self.current_search_index = 0
        else:
            self.search_hint.config(
                text="Элементы не найдены", 
                foreground="red")
            self.highlight_search_results([])
            self.current_search_index = -1

    def find_next(self):
        """Переходит к следующему результату поиска."""
        if not self.search_results:
            return
        
        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        next_item = self.search_results[self.current_search_index]
        self._expand_to_item(next_item)

    def fill_tree(self, project_structure: Dict[str, Any]):
        """Заполняет дерево структурой проекта с эмодзи как в старом коде."""
        self.tree.delete(*self.tree.get_children())
        self._item_map.clear()
        self.all_tree_items = []

        # Получаем данные
        modules = project_structure.get("modules", [])
        files = project_structure.get("files", {})
        directories = project_structure.get("directories", [])

        # Функция для добавления элементов с эмодзи
        def add_item(parent, name, item_type, path, full_path, emoji):
            item_id = self.tree.insert(parent, "end", text=f"{emoji} {name}", tags=(item_type,))
            self._item_map[item_id] = {
                "type": item_type,
                "name": name,
                "path": path,
                "full_path": full_path,
                "display_name": f"{emoji} {name}"
            }
            self.all_tree_items.append(item_id)
            return item_id

        # Добавляем директории
        for directory in directories:
            add_item("", directory, 'directory', directory, directory, '📁')

        # Добавляем модули
        for module in modules:
            add_item("", module, 'module', module, module, '📦')

        # Добавляем файлы
        for file_path in files:
            file_info = files[file_path]
            module_name = file_info.get("module", "")
            
            # Находим родителя (модуль)
            parent_id = ""
            for item_id, item_data in self._item_map.items():
                if item_data.get("type") == "module" and item_data.get("name") == module_name:
                    parent_id = item_id
                    break
            
            # Создаем элемент файла
            file_name = os.path.basename(file_path)
            file_id = add_item(parent_id, file_name, 'file', file_path, file_path, '📄')
            
            # Добавляем информацию о модуле
            self._item_map[file_id]['module'] = module_name

        logger.debug("Дерево заполнено: modules=%s, files=%s, directories=%s", 
                    len(modules), len(files), len(directories))

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
            # Извлекаем чистые данные (без эмодзи)
            if 'display_name' in item_data:
                display_text = item_data['display_name']
                # Убираем эмодзи для чистого имени
                clean_name = re.sub(r'[🔹📦📝⚡🏛️📋❓📁📄()]', '', display_text).strip()
                item_data['clean_name'] = clean_name
            return item_data
        return {}

    def highlight_search_results(self, items: List[str]):
        """Подсвечивает результаты поиска."""
        # Сбрасываем подсветку
        for item_id in self.all_tree_items:
            self.tree.item(item_id, tags=(self._item_map[item_id].get('type'),))

        # Подсвечиваем найденные элементы
        for item_id in items:
            current_tags = list(self.tree.item(item_id, 'tags'))
            if 'found' not in current_tags:
                current_tags.append('found')
            self.tree.item(item_id, tags=tuple(current_tags))

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
        self.tree.bind("<<TreeviewSelect>>", lambda e: callback())

    def search_elements(self, search_text: str) -> List[str]:
        """Ищет элементы в дереве с поддержкой точечной нотации."""
        search_lower = search_text.lower()
        results = []

        # Поиск по точечной нотации
        if '.' in search_lower:
            parts = search_lower.split('.')
            for item_id in self.all_tree_items:
                item_data = self._item_map[item_id]
                item_name = item_data.get('name', '').lower()
                item_type = item_data.get('type', '')
                
                # Для файлов ищем по полному пути
                if item_type == 'file':
                    full_path = item_data.get('full_path', '').lower()
                    if self._matches_dot_notation(full_path, parts):
                        results.append(item_id)
                else:
                    # Для других элементов ищем по имени
                    if self._matches_dot_notation(item_name, parts):
                        results.append(item_id)
        else:
            # Обычный поиск
            for item_id in self.all_tree_items:
                item_text = self.tree.item(item_id, 'text').lower()
                clean_text = self._clean_search_text(item_text)
                if search_lower in clean_text:
                    results.append(item_id)

        return results

    def _clean_search_text(self, text: str) -> str:
        """Очищает текст для поиска от эмодзи и специальных символов."""
        cleaned = re.sub(r'[🔹📦📝⚡🏛️📋❓📁📄()]', '', text)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        return cleaned.lower()

    def _matches_dot_notation(self, text: str, search_parts: List[str]) -> bool:
        """Проверяет соответствие точечной нотации."""
        # Преобразуем путь в формат для поиска
        search_text = text.replace(os.sep, '.').replace('/', '.').replace('\\', '.')
        search_text = search_text.lower()
        
        # Ищем все части последовательно
        for i in range(len(search_text) - len('.'.join(search_parts)) + 1):
            match = True
            combined_search = '.'.join(search_parts)
            if combined_search in search_text:
                return True
        
        return False

    def set_on_tree_select_callback(self, callback: Callable):
        """Устанавливает callback для выбора."""
        self._on_tree_select_callback = callback
        self.tree.bind('<<TreeviewSelect>>', lambda e: callback())

    def get_all_items(self) -> List[str]:
        """Возвращает все элементы дерева."""
        return self.all_tree_items

    def _get_display_info(self, node) -> Tuple[str, str]:
        """Возвращает отображаемое имя и тип для узла."""
        node_type = node.get('type', 'unknown')
        node_name = node.get('name', '')
        
        type_emojis = {
            'module': '📦',
            'file': '📄',
            'directory': '📁',
            'class': '🏛️',
            'function': '⚡',
            'method': '🔹',
            'global_section': '📋',
            'import_section': '📥',
            'async_function': '⚡'
        }
        
        emoji = type_emojis.get(node_type, '❓')
        
        if node_type in ['function', 'method', 'async_function']:
            display_name = f"{emoji} {node_name}()"
        else:
            display_name = f"{emoji} {node_name}"
        
        return display_name, node_type

    def _get_directory_structure(self, directory: str) -> Dict:
        """Получает структуру директории."""
        structure = {'files': [], 'directories': []}
        
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    structure['directories'].append(item)
                else:
                    if item.endswith('.py'):
                        structure['files'].append(item)
        except Exception as e:
            logger.error(f"Ошибка чтения директории {directory}: {e}")
        
        return structure

    def load_project_structure(self, directory: str):
        """Загружает структуру проекта из директории."""
        if not os.path.exists(directory):
            logger.error(f"Директория не существует: {directory}")
            return
        
        structure = {
            'modules': [],
            'files': {},
            'directories': []
        }
        
        # Рекурсивно обходим директорию
        for root, dirs, files in os.walk(directory):
            # Пропускаем скрытые директории
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            rel_root = os.path.relpath(root, directory)
            if rel_root == '.':
                module_name = ''
            else:
                module_name = rel_root.replace(os.sep, '.')
                if module_name not in structure['modules']:
                    structure['modules'].append(module_name)
            
            # Добавляем поддиректории
            for dir_name in dirs:
                structure['directories'].append(os.path.join(rel_root, dir_name))
            
            # Добавляем файлы
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory)
                    structure['files'][rel_path] = {
                        'path': file_path,
                        'module': module_name,
                        'name': file
                    }
        
        self.fill_tree(structure)

    def get_tree_widget(self) -> ttk.Treeview:
        """Возвращает виджет дерева."""
        return self.tree