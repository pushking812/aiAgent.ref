# tests/gui/test_project_tree_view_gui.py

"""GUI тесты для ProjectTreeView (требуют --run-gui)."""

import pytest
from unittest.mock import Mock, patch
import tkinter as tk
from tkinter import ttk
from gui.views.project_tree_view import ProjectTreeView


@pytest.fixture
def tk_root():
    """Создает временное Tkinter окно для тестов."""
    root = tk.Tk()
    root.withdraw()  # Скрываем окно
    yield root
    root.destroy()


@pytest.fixture
def project_tree_view(tk_root):
    """Создает экземпляр ProjectTreeView для тестов."""
    view = ProjectTreeView(tk_root)
    view.pack()
    return view


@pytest.fixture
def sample_project_structure():
    """Возвращает пример структуры проекта для тестов."""
    return {
        "modules": ["app", "tests"],
        "files": {
            "app/main.py": "print('Hello')",
            "app/utils.py": "def helper(): pass",
            "tests/test_app.py": "import unittest",
        }
    }


@pytest.mark.gui
class TestProjectTreeViewGUI:
    """GUI тесты ProjectTreeView (требуют реального Tkinter)."""
    
    def test_fill_tree_gui(self, project_tree_view, sample_project_structure):
        """Тест заполнения дерева в GUI."""
        project_tree_view.fill_tree(sample_project_structure)
        
        # Проверяем что элементы были добавлены
        children = project_tree_view.tree.get_children()
        assert len(children) > 0
    
    def test_search_elements_gui(self, project_tree_view, sample_project_structure):
        """Тест поиска элементов в GUI."""
        project_tree_view.fill_tree(sample_project_structure)
        
        results = project_tree_view.search_elements("app")
        assert isinstance(results, list)
        
        # По крайней мере app и test_app должны быть найдены
        assert len(results) >= 2
    
    def test_expand_collapse_gui(self, project_tree_view, sample_project_structure):
        """Тест раскрытия/сворачивания в GUI."""
        project_tree_view.fill_tree(sample_project_structure)
        
        # Проверяем что методы не вызывают ошибок
        project_tree_view.expand_all()
        project_tree_view.collapse_all()
        
        assert True  # Если дошли сюда без исключений - тест пройден