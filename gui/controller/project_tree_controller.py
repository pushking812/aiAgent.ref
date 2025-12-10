# gui/controllers/project_tree_controller.py

import logging
from typing import Optional, Callable
from gui.views.project_tree_view import ProjectTreeView

logger = logging.getLogger('ai_code_assistant')


class ProjectTreeController:
    """Контроллер для управления деревом проекта и взаимодействием с другими компонентами."""
    
    def __init__(self, tree_view: ProjectTreeView, code_display_callback: Optional[Callable] = None):
        """
        Инициализация контроллера.
        
        Args:
            tree_view: Экземпляр ProjectTreeView
            code_display_callback: Функция для отображения кода (принимает строку с кодом)
        """
        self.tree_view = tree_view
        self.code_display_callback = code_display_callback
        
        # Привязываем обработчик выбора
        if self.tree_view:
            self.tree_view.set_on_tree_select_callback(self._on_tree_selection_changed)
        
        logger.debug("ProjectTreeController инициализирован")
    
    def _on_tree_selection_changed(self):
        """Обработчик изменения выбора в дереве."""
        try:
            # Получаем код выбранного элемента
            code = self.tree_view.get_selected_element_code()
            
            # Вызываем callback для отображения кода
            if self.code_display_callback and code is not None:
                self.code_display_callback(code)
            
            logger.debug("Обработано изменение выбора в дереве")
            
        except Exception as e:
            logger.error(f"Ошибка обработки выбора в дереве: {e}")
    
    def set_code_display_callback(self, callback: Callable):
        """Устанавливает callback для отображения кода."""
        self.code_display_callback = callback
    
    def load_project(self, project_path: str):
        """Загружает проект в дерево."""
        if self.tree_view:
            self.tree_view.load_project_structure(project_path)
    
    def get_selected_item_info(self):
        """Возвращает информацию о выбранном элементе."""
        if self.tree_view:
            return self.tree_view.get_selected_item()
        return {}
    
    def search_in_tree(self, search_text: str):
        """Выполняет поиск в дереве."""
        if self.tree_view:
            return self.tree_view.search_elements(search_text)
        return []
    
    def expand_all(self):
        """Раскрывает все ветки дерева."""
        if self.tree_view:
            self.tree_view.expand_all()
    
    def collapse_all(self):
        """Сворачивает все ветки дерева."""
        if self.tree_view:
            self.tree_view.collapse_all()