# gui/views/code_structure_view.py

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable
import logging
from core.business.ast_service import ASTService
from core.models.code_model import CodeNode
from gui.utils.ui_factory import ui_factory, Tooltip

logger = logging.getLogger('ai_code_assistant')


class ICodeStructureView:
    """Интерфейс для отображения структуры кода"""
    def display_code_structure(self, file_path: str, ast_node: CodeNode): pass
    def clear_structure(self): pass
    def bind_on_element_select(self, callback: Callable): pass
    def get_selected_element(self) -> Dict: pass


class CodeStructureView(ttk.Frame, ICodeStructureView):
    """Виджет для отображения структуры кода с эмодзи"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        
        self.ast_service = ASTService()
        self._on_element_select_callback: Optional[Callable] = None
        self._item_map: Dict[str, Dict] = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настраивает UI виджета"""
        # Контейнер для структуры кода
        structure_frame = ui_factory.create_label_frame(self, text="Структура кода")
        structure_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview для отображения структуры
        self.tree = ui_factory.create_treeview(
            structure_frame,
            columns=('type', 'line'),
            show='tree'
        )
        
        # Настраиваем колонки
        self.tree.heading("#0", text="Элементы кода")
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("type", width=100, stretch=False)
        self.tree.column("line", width=50, stretch=False)
        
        # Настраиваем теги для разных типов элементов
        self._setup_tree_tags()
        
        # Полоса прокрутки
        scrollbar = ui_factory.create_scrollbar(
            structure_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка событий
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)
    
    def _setup_tree_tags(self):
        """Настраивает теги дерева с эмодзи и цветами"""
        type_styles = {
            'module': {'emoji': '📦', 'foreground': 'blue'},
            'class': {'emoji': '🏛️', 'foreground': 'darkblue'},
            'function': {'emoji': '⚡', 'foreground': 'green'},
            'async_function': {'emoji': '⚡', 'foreground': 'darkgreen'},
            'method': {'emoji': '🔹', 'foreground': 'purple'},
            'import_section': {'emoji': '📥', 'foreground': 'gray'},
            'global_section': {'emoji': '📋', 'foreground': 'brown'},
            'module_error': {'emoji': '❌', 'foreground': 'red'}
        }
        
        for type_name, style in type_styles.items():
            self.tree.tag_configure(type_name, foreground=style['foreground'])
    
    def display_code_structure(self, file_path: str, ast_node: CodeNode):
        """Отображает структуру кода файла"""
        self.clear_structure()
        self._item_map.clear()
        
        if not ast_node:
            logger.error(f"Не удалось получить AST для файла: {file_path}")
            return
        
        # Добавляем корневой элемент (модуль)
        module_emoji = '📦' if ast_node.type != 'module_error' else '❌'
        module_text = f"{module_emoji} {ast_node.name}"
        
        module_id = self.tree.insert(
            '',
            'end',
            text=module_text,
            values=(ast_node.type, ''),
            tags=(ast_node.type,)
        )
        
        self._item_map[module_id] = {
            'type': ast_node.type,
            'name': ast_node.name,
            'node': ast_node,
            'file_path': file_path
        }
        
        # Рекурсивно добавляем дочерние элементы
        self._add_children_recursive(module_id, ast_node.children)
        
        # Раскрываем корневой элемент
        self.tree.item(module_id, open=True)
        
        logger.debug(f"Структура кода отображена: {file_path}, элементов: {len(self._item_map)}")
    
    def _add_children_recursive(self, parent_id: str, children: List[CodeNode], level: int = 0):
        """Рекурсивно добавляет дочерние элементы"""
        type_emojis = {
            'module': '📦',
            'class': '🏛️',
            'function': '⚡',
            'async_function': '⚡',
            'method': '🔹',
            'import_section': '📥',
            'global_section': '📋',
            'module_error': '❌'
        }
        
        for child in children:
            emoji = type_emojis.get(child.type, '❓')
            
            # Форматируем имя элемента
            display_name = child.name
            if child.type in ['function', 'async_function', 'method']:
                display_name = f"{child.name}()"
            
            item_text = f"{emoji} {display_name}"
            
            # Определяем номер строки (если возможно)
            line_info = ""
            if hasattr(child, 'ast_node') and child.ast_node and hasattr(child.ast_node, 'lineno'):
                line_info = str(child.ast_node.lineno)
            
            # Вставляем элемент
            item_id = self.tree.insert(
                parent_id,
                'end',
                text=item_text,
                values=(child.type, line_info),
                tags=(child.type,)
            )
            
            self._item_map[item_id] = {
                'type': child.type,
                'name': child.name,
                'node': child,
                'line': line_info
            }
            
            # Добавляем подсказку с превью кода
            if child.source_code:
                preview = child.source_code[:100].replace('\n', ' ')
                if len(child.source_code) > 100:
                    preview += "..."
                Tooltip(self.tree, preview)
            
            # Рекурсивно добавляем детей
            if hasattr(child, 'children') and child.children:
                self._add_children_recursive(item_id, child.children, level + 1)
    
    def clear_structure(self):
        """Очищает отображение структуры"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._item_map.clear()
        logger.debug("Структура кода очищена")
    
    def _on_tree_select(self, event=None):
        """Обработчик выбора элемента в дереве"""
        selection = self.tree.selection()
        if selection and selection[0] in self._item_map:
            element_info = self._item_map[selection[0]]
            if self._on_element_select_callback:
                self._on_element_select_callback(element_info)
    
    def bind_on_element_select(self, callback: Callable):
        """Привязывает обработчик выбора элемента"""
        self._on_element_select_callback = callback
        logger.debug("Обработчик выбора элемента привязан")
    
    def get_selected_element(self) -> Dict:
        """Возвращает выбранный элемент"""
        selection = self.tree.selection()
        if selection and selection[0] in self._item_map:
            return self._item_map[selection[0]].copy()
        return {}
    
    def expand_all(self):
        """Раскрывает все ветки"""
        for item in self.tree.get_children():
            self._expand_recursive(item)
    
    def _expand_recursive(self, item: str):
        """Рекурсивно раскрывает ветку"""
        self.tree.item(item, open=True)
        for child in self.tree.get_children(item):
            self._expand_recursive(child)
    
    def collapse_all(self):
        """Сворачивает все ветки"""
        for item in self.tree.get_children():
            self.tree.item(item, open=False)