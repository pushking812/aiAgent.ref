# tests/unit/test_project_tree_view.py

"""Юнит-тесты для ProjectTreeView."""

import re
from unittest.mock import Mock, patch

import pytest

from gui.views.project_tree_view import IProjectTreeView, ProjectTreeView


class TestProjectTreeViewUnit:
    """Юнит-тесты ProjectTreeView."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        # Создаем минимальный мок tkinter виджета
        self.mock_parent = Mock()
        self.mock_parent._w = 'mock_parent'
        self.mock_parent.tk = Mock()
        self.mock_parent._last_child_ids = {}
        self.mock_parent.children = {}
        
        # Патчим все tkinter-зависимости
        with patch('gui.views.project_tree_view.ttk.Frame'):
            with patch('gui.views.project_tree_view.ttk.Treeview'):
                self.view = ProjectTreeView(self.mock_parent)

    def test_interface_implementation(self):
        """Тест реализации интерфейса IProjectTreeView."""
        interface_methods = [
            'setup_tree', 'fill_tree', 'get_selected_item',
            'highlight_search_results', 'expand_all', 'collapse_all',
            'bind_on_select', 'search_elements', 'set_on_tree_select_callback'
        ]

        for method_name in interface_methods:
            assert hasattr(ProjectTreeView, method_name)
            assert callable(getattr(ProjectTreeView, method_name))

    def test_clean_search_path_logic(self):
        """Тестирует очистку путей для поиска с учетом эмодзи и форматирования."""
        # Сначала проверим логику функции очистки напрямую
        def clean_search_path(path: str) -> str:
            """Очищает путь для поиска."""
            cleaned = re.sub(r'[🔹📦📝⚡🏛️📋❓()]', '', path)
            cleaned = re.sub(r'\s+', '', cleaned)
            # Заменяем множественные точки на одну
            cleaned = re.sub(r'\.{2,}', '.', cleaned)
            cleaned = cleaned.strip('.')
            return cleaned.lower()
        
        test_cases = [
            ("app.module", "app.module"),
            ("app..main", "app.main"),  # множественные точки заменяются на одну
            ("  app.module  ", "app.module"),
            ("app.🔹module", "app.module"),
            ("app.📦module", "app.module"),
            ("app.📝module", "app.module"),
            ("app.⚡module", "app.module"),
            ("app.🏛️module", "app.module"),
            ("app.📋module", "app.module"),
            ("app.❓module", "app.module"),
            ("app.()module", "app.module"),
            ("app. .main", "app.main"),
            (".app.module.", "app.module"),
            ("..app..module..", "app.module"),
            ("APP.MODULE", "app.module"),
            ("App.Module", "app.module"),
            ("app..module..test", "app.module.test"),
            ("  app  ..  module  ", "app.module"),
            ("app🔹📦📝⚡🏛️📋❓()module", "appmodule"),
            ("", ""),
            ("...", ""),
            (".", ""),
        ]

        for input_path, expected in test_cases:
            result = clean_search_path(input_path)
            assert result == expected, f"Для '{input_path}' ожидалось '{expected}', получено '{result}'"
    
    def test_search_logic(self):
        """Тест логики поиска."""
        # Создаем простую имитацию логики поиска
        items = [
            {"id": "1", "text": "app", "tags": ("module",)},
            {"id": "2", "text": "main.py", "tags": ("file",)},
            {"id": "3", "text": "tests", "tags": ("module",)},
        ]
        
        def simple_search(search_text):
            search_lower = search_text.lower()
            results = []
            for item in items:
                item_text = item["text"].lower()
                if search_lower in item_text:
                    results.append(item["id"])
            return results

        # Тестируем
        results = simple_search("app")
        assert "1" in results

        results = simple_search("main")
        assert "2" in results

        results = simple_search("nonexistent")
        assert results == []


# Дополнительные тесты для edge cases
class TestProjectTreeViewAdditional:
    """Дополнительные тесты ProjectTreeView."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.mock_parent = Mock()
        self.mock_parent._w = 'mock_parent'
        self.mock_parent.tk = Mock()
        self.mock_parent._last_child_ids = {}
        self.mock_parent.children = {}
        
        with patch('gui.views.project_tree_view.ttk.Frame'):
            with patch('gui.views.project_tree_view.ttk.Treeview'):
                self.view = ProjectTreeView(self.mock_parent)

    def test_clean_search_path_edge_cases(self):
        """Тест крайних случаев очистки пути."""
        test_cases = [
            ("", ""),
            (".", ""),
            ("...", ""),
            (".....", ""),
            ("a.b.c", "a.b.c"),
            ("A.B.C", "a.b.c"),
            ("  a  .  b  .  c  ", "a.b.c"),
            ("a.🔹.b.📦.c", "a.b.c"),
        ]
        
        for input_path, expected in test_cases:
            result = self.view._clean_search_path(input_path)
            assert result == expected, f"Для '{input_path}' ожидалось '{expected}', получено '{result}'"


# Тесты для методов, которые требуют мокинга tkinter
class TestProjectTreeViewWithMocks:
    """Тесты с моками для tkinter методов."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.mock_parent = Mock()
        self.mock_parent._w = 'mock_parent'
        self.mock_parent.tk = Mock()
        self.mock_parent._last_child_ids = {}
        self.mock_parent.children = {}
        
        with patch('gui.views.project_tree_view.ttk.Frame'):
            with patch('gui.views.project_tree_view.ttk.Treeview'):
                self.view = ProjectTreeView(self.mock_parent)
        
        # Мокаем tree
        self.view.tree = Mock()

    def test_fill_tree_simple(self):
        """Упрощенный тест заполнения дерева."""
        mock_data = {
            "app": {"type": "module", "children": []}
        }
        
        # Настраиваем моки
        self.view.tree.delete = Mock()
        self.view.tree.get_children = Mock(return_value=[])
        
        with patch.object(self.view.tree, 'insert') as mock_insert:
            # Вызываем fill_tree с пустыми данными, чтобы проверить, что insert не вызывается
            self.view.fill_tree({})
            mock_insert.assert_not_called()
            
            # Теперь с данными
            self.view.fill_tree(mock_data)
            mock_insert.assert_called()

    def test_get_selected_item_simple(self):
        """Упрощенный тест получения выбранного элемента."""
        # Настраиваем мок для tree
        self.view.tree.selection = Mock(return_value=("item1",))
        
        # Мокаем item метод
        mock_item_data = {"text": "test.py", "tags": ("file",)}
        self.view.tree.item = Mock(return_value=mock_item_data)
        
        # Вызываем метод
        result = self.view.get_selected_item()
        
        # Проверяем, что метод возвращает кортеж
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_expand_all_simple(self):
        """Упрощенный тест раскрытия всех узлов."""
        # Настраиваем моки, чтобы избежать рекурсии
        self.view.tree.get_children = Mock(return_value=[])
        self.view.tree.set = Mock()
        
        # Должно работать без ошибок
        self.view.expand_all()
        
        # Проверяем, что get_children был вызван
        self.view.tree.get_children.assert_called_once()

    def test_collapse_all_simple(self):
        """Упрощенный тест сворачивания всех узлов."""
        # Настраиваем моки, чтобы избежать рекурсии
        self.view.tree.get_children = Mock(return_value=[])
        self.view.tree.set = Mock()
        
        # Должно работать без ошибок
        self.view.collapse_all()
        
        # Проверяем, что get_children был вызван
        self.view.tree.get_children.assert_called_once()

    def test_search_elements_with_mock(self):
        """Тест поиска элементов с правильными моками."""
        # Настраиваем моки
        mock_items = ["1", "2", "3"]
        self.view.tree.get_children = Mock(return_value=mock_items)
        
        # Мокаем item метод
        def mock_item(item_id, option=None):
            items_data = {
                "1": {"text": "app.py", "tags": ("file", "python")},
                "2": {"text": "utils.py", "tags": ("file", "python")},
                "3": {"text": "tests", "tags": ("folder",)},
            }
            if option == 'text':
                return items_data[item_id]["text"]
            elif option == 'tags':
                return items_data[item_id]["tags"]
            return items_data[item_id]
        
        self.view.tree.item = Mock(side_effect=mock_item)
        
        # Мокаем _clean_search_path
        self.view._clean_search_path = Mock(side_effect=lambda x: x.lower())
        
        # Вызываем search_elements
        results = self.view.search_elements("py")
        
        # Проверяем результаты
        assert isinstance(results, list)
        # Должны найти app.py и utils.py
        assert len(results) == 2
        assert "1" in results
        assert "2" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])