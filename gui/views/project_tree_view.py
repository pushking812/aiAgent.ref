# gui/views/project_tree_view.py

import logging
import os
import re
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple

from gui.utils.ui_factory import ui_factory, Tooltip
from core.business.ast_service import ASTService
from core.models.code_model import CodeNode

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
    def load_project_structure(self, directory: str): pass
    def get_tree_widget(self) -> ttk.Treeview: pass
    def get_selected_element_code(self) -> str: pass  # НОВЫЙ МЕТОД


class ProjectTreeView(ttk.Frame, IProjectTreeView):
    """Реализация дерева проекта с использованием фабрики UI."""
    
    def __init__(self, parent):
        super().__init__(parent)
        if parent:
            self.pack(fill=tk.BOTH, expand=True)
        
        # Основной контейнер для дерева
        self.tree_container = None
        self.tree = None
        
        # Инициализация
        self.search_results: List[str] = []
        self.current_search_index = -1
        self._item_map: Dict[str, Dict] = {}
        self._on_tree_select_callback: Optional[Callable] = None
        self.all_tree_items: List[str] = []
        self.ast_service = ASTService()
        self.project_tree: Dict[str, CodeNode] = {}
        
        # Создаем виджеты только если родитель указан
        if parent:
            self._setup_ui()
        
        logger.debug("ProjectTreeView инициализирован")
    
    def _setup_ui(self):
        """Настраивает UI виджета."""
        if not self.tree_container:
            self.tree_container = ui_factory.create_frame(self, width=300)
            self.tree_container.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
            self.tree_container.pack_propagate(False)
            
            # Создаем дерево
            self.setup_tree()

    def setup_search_panel(self, parent):
        """Создает панель поиска с использованием фабрики."""
        search_frame = ui_factory.create_label_frame(parent, text="Быстрый поиск", padding=5)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = ui_factory.create_entry(
            search_frame,
            textvariable=self.search_var,
            tooltip="Введите текст для поиска элементов"
        )
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_hint = ui_factory.create_label(
            search_frame,
            text="Введите имя элемента (module.function, module.class.method)",
            small=True,
            foreground="gray"
        )
        self.search_hint.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Привязка событий поиска
        self.search_entry.bind('<KeyRelease>', self._on_search_changed)

    def setup_tree_buttons(self, parent):
        """Создает кнопки управления деревом с использованием фабрики."""
        tree_buttons_frame = ui_factory.create_label_frame(parent, text="Дерево", padding=5)
        tree_buttons_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Создаем кнопки через фабрику
        self.expand_all_button = ui_factory.create_button(
            tree_buttons_frame,
            text="👁️",
            square=True,
            tooltip="Раскрыть все ветки"
        )
        self.expand_all_button.pack(side=tk.LEFT, padx=2)
        
        self.collapse_all_button = ui_factory.create_button(
            tree_buttons_frame,
            text="🙈",
            square=True,
            tooltip="Свернуть все ветки"
        )
        self.collapse_all_button.pack(side=tk.LEFT, padx=2)
        
        self.find_next_button = ui_factory.create_button(
            tree_buttons_frame,
            text="🔍",
            square=True,
            tooltip="Следующий результат поиска"
        )
        self.find_next_button.pack(side=tk.LEFT, padx=2)

    def setup_tree(self):
        """Создает само дерево проекта с использованием фабрики."""
        if not self.tree_container:
            return
            
        tree_frame = ui_factory.create_label_frame(self.tree_container, text="Структура проекта")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree_container = ui_factory.create_frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Создаем Treeview через фабрику
        self.tree = ui_factory.create_treeview(
            tree_container,
            columns=('path', 'type'),
            show='tree'
        )
        
        # Настраиваем колонки
        self.tree.heading("#0", text="Структура проекта")
        self.tree.column("#0", width=250, minwidth=150)
        self.tree.column("path", width=0, stretch=False)
        self.tree.column("type", width=0, stretch=False)
        
        # Полоса прокрутки через фабрику
        tree_scrollbar = ui_factory.create_scrollbar(
            tree_container,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Размещение
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Настройка тегов для подсветки разных типов элементов
        self.tree.tag_configure('found', background='#e6f3ff')
        self.tree.tag_configure('project_root', foreground='darkblue', font=('Arial', 10, 'bold'))
        self.tree.tag_configure('directory', foreground='#8B4513')
        self.tree.tag_configure('file', foreground='green')
        self.tree.tag_configure('import_section', foreground='gray')
        self.tree.tag_configure('import', foreground='darkgray')
        self.tree.tag_configure('import_from', foreground='darkgray')
        self.tree.tag_configure('class', foreground='darkblue')
        self.tree.tag_configure('method', foreground='purple')
        self.tree.tag_configure('async_method', foreground='#8A2BE2')
        self.tree.tag_configure('function', foreground='darkgreen')
        self.tree.tag_configure('async_function', foreground='#228B22')
        self.tree.tag_configure('global_section', foreground='brown')
        self.tree.tag_configure('other_element', foreground='#8B4513')
        self.tree.tag_configure('error', foreground='red')
        self.tree.tag_configure('syntax_error', foreground='orange')
        self.tree.tag_configure('ast_error', foreground='darkred')
        self.tree.tag_configure('module_error', foreground='red')
        
        # Привязываем обработчик выбора
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

    def _on_tree_select(self, event=None):
        """Обработчик выбора элемента в дереве."""
        if self._on_tree_select_callback:
            self._on_tree_select_callback()

    def set_on_tree_select_callback(self, callback: Callable):
        """Устанавливает callback для выбора."""
        self._on_tree_select_callback = callback
        if self.tree:
            self.tree.bind('<<TreeviewSelect>>', lambda e: callback())

    def _on_search_changed(self, event):
        """Обработчик изменения текста в поле поиска."""
        search_text = self.search_var.get().strip()
        
        if not search_text:
            self.search_hint.config(
                text="Введите имя элемента (module.function, module.class.method)",
                foreground="gray"
            )
            self.highlight_search_results([])
            self.search_results = []
            return
        
        self.search_results = self.search_elements(search_text)
        
        if self.search_results:
            self.search_hint.config(
                text=f"Найдено элементов: {len(self.search_results)}",
                foreground="green"
            )
            self.highlight_search_results(self.search_results)
            self.current_search_index = 0
        else:
            self.search_hint.config(
                text="Элементы не найдены",
                foreground="red"
            )
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
        """Заполняет дерево структурой проекта с элементами кода."""
        if not self.tree:
            self.setup_tree()
            
        if not self.tree:
            return
            
        self.tree.delete(*self.tree.get_children())
        self._item_map.clear()
        self.all_tree_items = []
        
        # Парсим проект для получения AST структуры
        project_path = project_structure.get('project_path', '')
        if project_path and os.path.exists(project_path):
            try:
                self.project_tree = self.ast_service.parse_project(project_path)
                logger.info(f"AST дерево проекта получено: {len(self.project_tree)} файлов")
            except Exception as e:
                logger.error(f"Ошибка парсинга проекта: {e}")
                self.project_tree = {}
        else:
            # Используем файловую структуру из project_structure
            self._fill_tree_from_structure(project_structure)
            return

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: используем ast_tree из структуры если он есть
        ast_tree = project_structure.get('ast_tree', self.project_tree)
        self.project_tree = ast_tree
        
        # Получаем файлы из структуры
        files = project_structure.get("files", {})
        
        # Создаем корневой элемент для проекта
        project_name = os.path.basename(project_path) if project_path else "Проект"
        project_root = self.tree.insert("", "end", text=f"📁 {project_name}", tags=('project_root',))
        self._item_map[project_root] = {
            "type": "project",
            "name": project_name,
            "path": project_path,
            "display_name": f"📁 {project_name}"
        }
        self.all_tree_items.append(project_root)

        # Группируем файлы по директориям
        dir_structure = {}
        for file_rel_path, file_info in files.items():
            if isinstance(file_info, dict):
                dir_path = os.path.dirname(file_rel_path)
                if dir_path not in dir_structure:
                    dir_structure[dir_path] = []
                dir_structure[dir_path].append((file_rel_path, file_info))
            else:
                # Простая структура
                dir_path = os.path.dirname(file_rel_path)
                if dir_path not in dir_structure:
                    dir_structure[dir_path] = []
                dir_structure[dir_path].append((file_rel_path, file_info))

        # Добавляем директории из структуры проекта
        directories = project_structure.get('directories', [])
        for directory in sorted(directories):
            dir_id = self._add_directory(project_root, directory)
            
            # Добавляем файлы этой директории
            if directory in dir_structure:
                for file_rel_path, file_info in dir_structure[directory]:
                    self._add_file_with_code_structure(dir_id, file_rel_path, file_info)

        # Добавляем файлы из корневой директории
        if '' in dir_structure:
            for file_rel_path, file_info in dir_structure['']:
                self._add_file_with_code_structure(project_root, file_rel_path, file_info)

        # Проверяем файлы с ошибками
        error_files = []
        for file_path, node in ast_tree.items():
            if node and node.type == 'module_error':
                error_files.append(os.path.basename(file_path))
                logger.warning(f"Файл с синтаксической ошибкой: {file_path}")

        # Раскрываем корневой элемент
        self.tree.item(project_root, open=True)
        
        total_elements = len(self.all_tree_items)
        directories_count = len([item for item in self.all_tree_items 
                               if self._item_map.get(item, {}).get('type') == 'directory'])
        files_count = len([item for item in self.all_tree_items 
                          if self._item_map.get(item, {}).get('type') == 'file'])
        code_elements = total_elements - directories_count - files_count - 1  # -1 для project_root
        
        logger.info("Структура проекта загружена: total=%s, dirs=%s, files=%s, code=%s", 
                   total_elements, directories_count, files_count, code_elements)
        
        # Показываем предупреждение если есть файлы с ошибками
        if error_files and hasattr(self, 'parent') and self.parent:
            import tkinter.messagebox as messagebox
            
            error_count = len(error_files)
            file_list = ', '.join(error_files[:3])
            if error_count > 3:
                file_list += f" и еще {error_count - 3}"
            
            messagebox.showwarning(
                "Синтаксические ошибки",
                f"Найдено {error_count} файлов с синтаксическими ошибками:\n"
                f"{file_list}\n\n"
                f"Эти файлы отмечены значком ❌ в дереве проекта."
            )

    def _fill_tree_from_structure(self, project_structure: Dict[str, Any]):
        """Заполняет дерево из структуры проекта (без AST парсинга)."""
        # Создаем корневой элемент для проекта
        project_root = self.tree.insert("", "end", text="📁 Проект", tags=('project_root',))
        self._item_map[project_root] = {
            "type": "project",
            "name": "Проект",
            "path": "",
            "display_name": "📁 Проект"
        }
        self.all_tree_items.append(project_root)

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
            add_item(project_root, directory, 'directory', directory, directory, '📁')

        # Добавляем модули
        for module in modules:
            add_item(project_root, module, 'module', module, module, '📦')

        # Добавляем файлы
        for file_path, file_info in files.items():
            if isinstance(file_info, dict):
                module_name = file_info.get("module", "")
            else:
                module_name = ""
            
            # Находим родителя (модуль)
            parent_id = project_root
            for item_id, item_data in self._item_map.items():
                if item_data.get("type") == "module" and item_data.get("name") == module_name:
                    parent_id = item_id
                    break
            
            # Создаем элемент файла
            file_name = os.path.basename(file_path)
            file_id = add_item(parent_id, file_name, 'file', file_path, file_path, '📄')
            
            # Добавляем информацию о модуле
            self._item_map[file_id]['module'] = module_name
        
        self.tree.item(project_root, open=True)
        logger.debug("Дерево заполнено из структуры: modules=%s, files=%s, directories=%s", 
                    len(modules), len(files), len(directories))

    def _add_directory(self, parent_id, dir_path):
        """Добавляет директорию в дерево."""
        dir_name = os.path.basename(dir_path) if dir_path else "."
        dir_id = self.tree.insert(
            parent_id, 
            "end", 
            text=f"📁 {dir_name}", 
            tags=('directory',)
        )
        self._item_map[dir_id] = {
            "type": "directory",
            "name": dir_name,
            "path": dir_path,
            "display_name": f"📁 {dir_name}"
        }
        self.all_tree_items.append(dir_id)
        return dir_id

    def _add_file_with_code_structure(self, parent_id, file_rel_path, file_info):
        """Добавляет файл с его структурой кода в дерево."""
        if isinstance(file_info, dict):
            file_path = file_info.get('path', '')
            file_name = file_info.get('name', os.path.basename(file_rel_path))
            ast_node = file_info.get('ast_node')
        else:
            file_path = file_rel_path
            file_name = os.path.basename(file_rel_path)
            ast_node = None
        
        # Ищем AST узел если не передан
        if not ast_node:
            for project_file_path, node in self.project_tree.items():
                if os.path.normpath(project_file_path) == os.path.normpath(file_path):
                    ast_node = node
                    break
        
        if ast_node and ast_node.type == 'module_error':
            # Файл с ошибкой синтаксиса
            file_id = self.tree.insert(
                parent_id, 
                "end", 
                text=f"❌ {file_name}", 
                tags=('module_error',)
            )
            self._item_map[file_id] = {
                "type": "file_error",
                "name": file_name,
                "path": file_path,
                "full_path": file_path,
                "display_name": f"❌ {file_name}",
                "node": ast_node
            }
            
            # Добавляем информацию об ошибке
            error_id = self.tree.insert(
                file_id,
                "end",
                text=f"⚠️ Синтаксическая ошибка",
                tags=('error',)
            )
            self.all_tree_items.append(error_id)
            
        elif ast_node:
            # Файл с правильным синтаксисом
            file_id = self.tree.insert(
                parent_id, 
                "end", 
                text=f"📄 {file_name}", 
                tags=('file',)
            )
            
            self._item_map[file_id] = {
                "type": "file",
                "name": file_name,
                "path": file_path,
                "full_path": file_path,
                "display_name": f"📄 {file_name}",
                "node": ast_node
            }
            self.all_tree_items.append(file_id)
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: добавляем структуру кода
            self._add_code_structure_to_file(file_id, ast_node)
        else:
            # Файл не найден в AST дереве (возможно, не Python файл)
            file_id = self.tree.insert(
                parent_id, 
                "end", 
                text=f"📄 {file_name}", 
                tags=('file',)
            )
            self._item_map[file_id] = {
                "type": "file",
                "name": file_name,
                "path": file_path,
                "full_path": file_path,
                "display_name": f"📄 {file_name}"
            }
            self.all_tree_items.append(file_id)
        
        return file_id

    def _add_code_structure_to_file(self, file_id, module_node):
        """Добавляет структуру кода к файлу в дереве."""
        if not module_node or not hasattr(module_node, 'children'):
            logger.debug(f"У модуля {module_node.name} нет children")
            return
        
        logger.info(f"Добавление структуры кода для файла: {module_node.name}, детей: {len(module_node.children)}")
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: добавляем ВСЕ дочерние элементы
        for child_node in module_node.children:
            logger.debug(f"  Добавление узла: {child_node.name}, тип: {child_node.type}")
            self._add_code_node_to_tree(file_id, child_node)

    def _add_code_node_to_tree(self, parent_id, code_node):
        """Рекурсивно добавляет узел кода в дерево."""
        if not code_node:
            return
        
        # Убедимся, что есть children
        if not hasattr(code_node, 'children'):
            code_node.children = []
        
        display_name, node_type = self._get_display_info(code_node)
        
        logger.debug(f"    Создание элемента дерева: {display_name}, тип: {node_type}")
        
        element_id = self.tree.insert(
            parent_id, 
            "end", 
            text=display_name, 
            tags=(node_type,)
        )
        
        self._item_map[element_id] = {
            "type": node_type,
            "name": code_node.name,
            "node": code_node,
            "display_name": display_name,
            "path": code_node.file_path if hasattr(code_node, 'file_path') else ""
        }
        self.all_tree_items.append(element_id)
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: для ВСЕХ узлов добавляем дочерние элементы
        if hasattr(code_node, 'children') and code_node.children:
            logger.debug(f"    У узла {code_node.name} есть {len(code_node.children)} детей")
            
            # Для классов добавляем методы
            if node_type == 'class':
                for child in code_node.children:
                    if child.type in ['method', 'async_method']:
                        self._add_code_node_to_tree(element_id, child)
                    else:
                        # Другие элементы класса (вложенные классы, функции)
                        self._add_code_node_to_tree(element_id, child)
            
            # Для import_section и global_section добавляем все дочерние элементы
            elif node_type in ['import_section', 'global_section']:
                for child in code_node.children:
                    self._add_code_node_to_tree(element_id, child)
            
            # Для функций и методов не добавляем дочерние элементы (у них обычно нет)
            elif node_type not in ['function', 'async_function', 'method', 'async_method']:
                # Для других типов добавляем всех детей
                for child in code_node.children:
                    self._add_code_node_to_tree(element_id, child)

    def _get_display_info(self, code_node: CodeNode) -> tuple:
        """Возвращает отображаемое имя и тип для узла кода."""
        node_type = code_node.type
        
        if node_type == 'global_section':
            # Извлекаем номер из имени (global_code#1 -> 1)
            section_num = code_node.name.split('#')[-1] if '#' in code_node.name else "1"
            return f"🔹 Global Code#{section_num}", 'global_section'
        
        elif node_type == 'import_section':
            # Извлекаем номер из имени (imports#1 -> 1)
            section_num = code_node.name.split('#')[-1] if '#' in code_node.name else "1"
            return f"📦 Imports#{section_num}", 'import_section'
        
        elif node_type == 'function':
            return f"📝 {code_node.name}()", 'function'
        
        elif node_type == 'async_function':
            return f"⚡ {code_node.name}()", 'async_function'
        
        elif node_type == 'class':
            return f"🏛️ {code_node.name}", 'class'
        
        elif node_type == 'method':
            return f"📋 {code_node.name}()", 'method'
        
        elif node_type == 'async_method':
            return f"⚡ {code_node.name}()", 'async_method'
        
        elif node_type == 'module_error':
            return f"❌ {code_node.name}", 'module_error'
        
        elif node_type == 'module':
            return f"📦 {code_node.name}", 'module'
        
        else:
            logger.warning(f"Неизвестный тип узла: {node_type}, имя: {code_node.name}")
            return f"❓ {code_node.name} ({node_type})", node_type

    def get_selected_item(self) -> Dict:
        """Возвращает выбранный элемент."""
        if not self.tree:
            return {}
            
        selection = self.tree.selection()
        if not selection or selection[0] not in self._item_map:
            return {}
        
        item_data = self._item_map[selection[0]].copy()
        item_data['id'] = selection[0]
        
        # Очищаем имя от эмодзи
        if 'display_name' in item_data:
            display_text = item_data['display_name']
            clean_name = re.sub(r'[🔹📦📝⚡🏛️📋❓📁📄()]', '', display_text).strip()
            item_data['clean_name'] = clean_name
            
        return item_data
        
    def get_selected_element_code(self) -> str:
        """
        Возвращает исходный код выбранного элемента.
        
        Returns:
            str: Исходный код элемента или пустая строка если не найден
        """
        selected_item = self.get_selected_item()
        if not selected_item:
            return ""
        
        # Получаем узел кода
        code_node = selected_item.get('node')
        if not code_node:
            logger.debug("Выбранный элемент не содержит узла кода")
            return ""
        
        # Извлекаем исходный код
        source_code = self._extract_element_source_code(code_node, selected_item)
        
        logger.debug(f"Получен код элемента: {selected_item.get('name')}, "
                    f"тип: {selected_item.get('type')}, длина: {len(source_code)}")
        
        return source_code
        
    def _extract_element_source_code(self, code_node: CodeNode, item_data: Dict) -> str:
        """Извлекает исходный код для элемента."""
        if not code_node:
            return ""
        
        # Для файлов показываем весь код
        if item_data.get('type') == 'file':
            return code_node.source_code if hasattr(code_node, 'source_code') else ""
        
        # Для элементов кода (функций, классов, методов) показываем их код
        if hasattr(code_node, 'source_code') and code_node.source_code:
            return code_node.source_code
        
        # Пытаемся получить код из AST узла
        if hasattr(code_node, 'ast_node') and code_node.ast_node:
            try:
                import ast
                return ast.unparse(code_node.ast_node) if hasattr(ast, 'unparse') else str(code_node.ast_node)
            except Exception as e:
                logger.debug(f"Не удалось распарсить AST узел: {e}")
        
        # Для секций (импорты, глобальный код)
        if item_data.get('type') in ['import_section', 'global_section']:
            return code_node.source_code if hasattr(code_node, 'source_code') else ""
        
        # Для директорий и проектов возвращаем пустую строку
        if item_data.get('type') in ['directory', 'project']:
            return ""
        
        # По умолчанию возвращаем имя элемента
        return f"# {item_data.get('name', '')}\n# Тип: {item_data.get('type', 'unknown')}"

    def highlight_search_results(self, items: List[str]):
        """Подсвечивает результаты поиска."""
        if not self.tree:
            return
            
        # Сбрасываем подсветку
        for item_id in self.all_tree_items:
            current_tags = list(self.tree.item(item_id, 'tags'))
            if 'found' in current_tags:
                current_tags.remove('found')
            self.tree.item(item_id, tags=tuple(current_tags))

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
        if not self.tree:
            return
            
        parent_id = self.tree.parent(item_id)
        while parent_id:
            self.tree.item(parent_id, open=True)
            parent_id = self.tree.parent(parent_id)

        self.tree.selection_set(item_id)
        self.tree.focus(item_id)
        self.tree.see(item_id)

    def expand_all(self):
        """Раскрывает все ветки."""
        if not self.tree:
            return
            
        for item in self.tree.get_children():
            self._expand_recursive(item)

    def _expand_recursive(self, item: str):
        """Рекурсивно раскрывает ветку."""
        if not self.tree:
            return
            
        self.tree.item(item, open=True)
        for child in self.tree.get_children(item):
            self._expand_recursive(child)

    def collapse_all(self):
        """Сворачивает все ветки."""
        if not self.tree:
            return
            
        for item in self.tree.get_children():
            self._collapse_recursive(item)

    def _collapse_recursive(self, item: str):
        """Рекурсивно сворачивает ветку."""
        if not self.tree:
            return
            
        self.tree.item(item, open=False)
        for child in self.tree.get_children(item):
            self._collapse_recursive(child)

    def bind_on_select(self, callback: Callable):
        """Привязывает обработчик выбора."""
        if self.tree:
            self.tree.bind("<<TreeviewSelect>>", lambda e: callback())

    def search_elements(self, search_text: str) -> List[str]:
        """Ищет элементы в дереве с поддержкой точечной нотации."""
        search_lower = search_text.lower()
        results = []

        if not self.tree:
            return results

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
                clean_text = self._clean_search_text(item_text)
                if search_lower in clean_text:
                    results.append(item_id)

        return results

    def _get_item_full_path(self, item_id: str) -> str:
        """Возвращает полный путь элемента в формате module.class.method."""
        path_parts = []
        current_id = item_id
        
        while current_id:
            item_text = self.tree.item(current_id, 'text')
            path_parts.append(item_text)
            current_id = self.tree.parent(current_id)
        
        path_parts.reverse()
        return '.'.join(path_parts)

    def _clean_search_text(self, text: str) -> str:
        """Очищает текст для поиска от эмодзи и специальных символов."""
        # Регулярное выражение для удаления эмодзи
        emoji_pattern = re.compile(
            "["u"\U0001F600-\U0001F64F"  # смайлики
            u"\U0001F300-\U0001F5FF"  # символы и пиктограммы
            u"\U0001F680-\U0001F6FF"  # транспорт и карты
            u"\U0001F1E0-\U0001F1FF"  # флаги
            "]+", flags=re.UNICODE
        )
        
        # Удаляем эмодзи
        text_no_emoji = emoji_pattern.sub('', text)
        
        # Удаляем технические символы
        cleaned = re.sub(r'[🔹📦📝⚡🏛️📋❓📁📄()\[\]]', '', text_no_emoji)
        
        # Убираем лишние пробелы
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip().lower()

    def _matches_dot_notation(self, text: str, search_parts: List[str]) -> bool:
        """Проверяет соответствие точечной нотации."""
        search_text = text.replace(os.sep, '.').replace('/', '.').replace('\\', '.')
        search_text = search_text.lower()
        
        # Очищаем от эмодзи
        search_text = self._clean_search_text(search_text)
        
        combined_search = '.'.join(search_parts)
        return combined_search in search_text

    def get_all_items(self) -> List[str]:
        """Возвращает все элементы дерева."""
        return self.all_tree_items

    def load_project_structure(self, directory: str):
        """Загружает структуру проекта из директории."""
        if not os.path.exists(directory):
            logger.error(f"Директория не существует: {directory}")
            return
        
        structure = {
            'project_path': directory,
            'modules': [],
            'files': {},
            'directories': []
        }
        
        # Парсим проект для получения AST структуры
        try:
            self.project_tree = self.ast_service.parse_project(directory)
            logger.info(f"AST дерево проекта получено: {len(self.project_tree)} файлов")
        except Exception as e:
            logger.error(f"Ошибка парсинга проекта: {e}")
            self.project_tree = {}
        
        # Собираем файловую структуру
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
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
                    
                    # Пытаемся получить содержимое файла
                    try:
                        content = ""
                        if file_path in self.project_tree:
                            content = self.project_tree[file_path].source_code
                        elif os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                        
                        structure['files'][rel_path] = {
                            'path': file_path,
                            'module': module_name,
                            'name': file,
                            'content': content
                        }
                    except Exception as e:
                        logger.error(f"Ошибка чтения файла {file_path}: {e}")
                        structure['files'][rel_path] = {
                            'path': file_path,
                            'module': module_name,
                            'name': file,
                            'content': f"# Ошибка чтения: {e}"
                        }
        
        self.fill_tree(structure)

    def get_tree_widget(self) -> ttk.Treeview:
        """Возвращает виджет дерева."""
        return self.tree
    
    def pack(self, **kwargs):
        """Упаковывает виджет и создает внутренние виджеты."""
        super().pack(**kwargs)
        if not self.tree:
            self._setup_ui()
            

    def load_project_from_repository(self, project_service):
        """Загружает проект из сервиса проекта с AST данными."""
        if not project_service or not project_service.project_path:
            logger.error("Не указан проект для загрузки")
            return
        
        try:
            # Получаем полную структуру проекта
            structure = project_service.get_project_structure()
            
            if not structure:
                logger.error("Не удалось получить структуру проекта")
                return
            
            # Заполняем дерево
            self.fill_tree(structure)
            
            logger.info(f"Проект загружен из репозитория: {project_service.project_path}")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки проекта из репозитория: {e}")
            raise

    def load_from_project_service(self, project_service):
        """Загружает структуру проекта из ProjectService."""
        if not project_service or not hasattr(project_service, 'get_project_structure'):
            logger.error("ProjectService не поддерживает get_project_structure")
            return
        
        try:
            # Получаем полную структуру с AST
            structure = project_service.get_project_structure()
            
            if not structure:
                logger.error("Пустая структура проекта")
                return
            
            # Очищаем текущее дерево
            if self.tree:
                self.tree.delete(*self.tree.get_children())
            
            self._item_map.clear()
            self.all_tree_items = []
            
            # Сохраняем AST дерево
            self.project_tree = structure.get('ast_tree', {})
            
            # Создаем корневой элемент
            project_path = structure.get('project_path', '')
            project_name = os.path.basename(project_path) if project_path else "Проект"
            project_root = self.tree.insert("", "end", text=f"📁 {project_name}", tags=('project_root',))
            
            self._item_map[project_root] = {
                "type": "project",
                "name": project_name,
                "path": project_path,
                "display_name": f"📁 {project_name}"
            }
            self.all_tree_items.append(project_root)
            
            # Группируем файлы по директориям
            dir_structure = {}
            files_data = structure.get('files', {})
            
            for file_rel_path, file_info in files_data.items():
                if isinstance(file_info, dict):
                    dir_path = os.path.dirname(file_rel_path)
                    if dir_path not in dir_structure:
                        dir_structure[dir_path] = []
                    dir_structure[dir_path].append((file_rel_path, file_info))
                else:
                    # Простая структура
                    dir_path = os.path.dirname(file_rel_path)
                    if dir_path not in dir_structure:
                        dir_structure[dir_path] = []
                    dir_structure[dir_path].append((file_rel_path, file_info))
            
            # Добавляем директории из структуры
            directories = structure.get('directories', [])
            for directory in sorted(directories):
                dir_id = self._add_directory(project_root, directory)
                
                # Добавляем файлы этой директории
                if directory in dir_structure:
                    for file_rel_path, file_info in dir_structure[directory]:
                        self._add_file_with_info(dir_id, file_rel_path, file_info)
            
            # Добавляем файлы из корневой директории
            if '' in dir_structure:
                for file_rel_path, file_info in dir_structure['']:
                    self._add_file_with_info(project_root, file_rel_path, file_info)
            
            # Проверяем файлы с ошибками
            error_files = []
            for file_path, ast_node in self.project_tree.items():
                if ast_node and ast_node.type == 'module_error':
                    error_files.append(os.path.basename(file_path))
            
            # Раскрываем корневой элемент
            self.tree.item(project_root, open=True)
            
            logger.info(f"Проект загружен: {len(self.all_tree_items)} элементов, "
                       f"{len(error_files)} файлов с ошибками")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки из ProjectService: {e}")
            raise
    
    def _add_file_with_info(self, parent_id, file_rel_path, file_info):
        """Добавляет файл с информацией в дерево."""
        if isinstance(file_info, dict):
            file_path = file_info.get('path', '')
            ast_node = file_info.get('ast_node')
            file_name = file_info.get('name', os.path.basename(file_rel_path))
        else:
            file_path = file_rel_path
            ast_node = None
            file_name = os.path.basename(file_rel_path)
        
        # Ищем AST узел если не передан
        if not ast_node and file_path:
            for project_file_path, node in self.project_tree.items():
                if os.path.normpath(project_file_path) == os.path.normpath(file_path):
                    ast_node = node
                    break
        
        if ast_node and ast_node.type == 'module_error':
            # Файл с ошибкой
            file_id = self.tree.insert(
                parent_id, 
                "end", 
                text=f"❌ {file_name}", 
                tags=('module_error',)
            )
            self._item_map[file_id] = {
                "type": "file_error",
                "name": file_name,
                "path": file_path,
                "full_path": file_path,
                "display_name": f"❌ {file_name}",
                "node": ast_node
            }
            
            error_id = self.tree.insert(
                file_id,
                "end",
                text=f"⚠️ Синтаксическая ошибка",
                tags=('error',)
            )
            self.all_tree_items.append(error_id)
            
        elif ast_node:
            # Файл с AST структурой
            file_id = self.tree.insert(
                parent_id, 
                "end", 
                text=f"📄 {file_name}", 
                tags=('file',)
            )
            
            self._item_map[file_id] = {
                "type": "file",
                "name": file_name,
                "path": file_path,
                "full_path": file_path,
                "display_name": f"📄 {file_name}",
                "node": ast_node
            }
            self.all_tree_items.append(file_id)
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: добавляем структуру кода
            self._add_code_structure_to_file(file_id, ast_node)
        else:
            # Файл без AST (возможно, не Python файл)
            file_id = self.tree.insert(
                parent_id, 
                "end", 
                text=f"📄 {file_name}", 
                tags=('file',)
            )
            self._item_map[file_id] = {
                "type": "file",
                "name": file_name,
                "path": file_path,
                "full_path": file_path,
                "display_name": f"📄 {file_name}"
            }
            self.all_tree_items.append(file_id)
        
        return file_id