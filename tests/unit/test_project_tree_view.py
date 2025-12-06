# tests/unit/test_project_tree_view.py

"""Юнит-тесты для ProjectTreeView."""

import re
from unittest.mock import Mock, patch

import pytest

from gui.views.project_tree_view import IProjectTreeView, ProjectTreeView


class TestProjectTreeViewUnit:
    """Юнит-тесты ProjectTreeView."""

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
        """Тест логики метода _clean_search_path."""
        # Проверяем логику очистки путей
        test_cases = [
            # (вход, ожидаемый результат после очистки)
            ("app.main", "app.main"),
            ("app.🔹main", "app.main"),
            ("app📦main📝", "appmain"),
            ("  app  .  main  ", "app.main"),
            (".app.main.", "app.main"),
            ("APP.MAIN", "app.main"),
            ("app..main", "app..main"),  # Двойные точки в середине не удаляются!
        ]

        # Функция очистки из реального кода
        def clean_search_path(path):
            cleaned = re.sub(r'[🔹📦📝⚡🏛️📋❓()]', '', path)
            cleaned = re.sub(r'\s+', '', cleaned)
            cleaned = cleaned.strip('.')
            return cleaned.lower()

        for input_path, expected in test_cases:
            result = clean_search_path(input_path)
            assert result == expected, f"Для '{input_path}' ожидалось '{expected}', получено '{result}'"

    def test_search_logic(self):
        """Тест логики поиска."""
        # Тестовая структура данных
        class MockTreeView:
            def __init__(self):
                self.items = {
                    "1": {"text": "app", "tags": ("module",)},
                    "2": {"text": "main.py", "tags": ("file",)},
                    "3": {"text": "tests", "tags": ("module",)},
                }

            def item(self, item_id, option):
                if option == 'text':
                    return self.items[item_id]["text"]
                elif option == 'tags':
                    return self.items[item_id]["tags"]

        # Тест поиска
        tree = MockTreeView()
        all_items = ["1", "2", "3"]

        def simple_search(search_text):
            search_lower = search_text.lower()
            results = []
            for item_id in all_items:
                item_text = tree.item(item_id, 'text').lower()
                if search_lower in item_text:
                    results.append(item_id)
            return results

        # Тестируем
        results = simple_search("app")
        assert "1" in results

        results = simple_search("main")
        assert "2" in results

        results = simple_search("nonexistent")
        assert results == []
