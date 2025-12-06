# tests/gui/test_gui_components.py

"""GUI тесты компонентов (с реальным tkinter)."""

import pytest

from tests.base_gui_test import BaseGUITest


@pytest.mark.gui
@pytest.mark.requires_tkinter
class TestGUIComponents(BaseGUITest):
    """GUI тесты компонентов с реальным tkinter."""

    def test_code_editor_view_gui(self, code_editor_view):
        """GUI тест CodeEditorView."""
        assert code_editor_view is not None

        # Проверяем основные виджеты
        assert code_editor_view.source_text is not None
        assert code_editor_view.ai_text is not None

        # Тест установки и получения содержимого
        test_content = "def test():\n    return True"
        code_editor_view.set_source_content(test_content)
        retrieved_content = code_editor_view.get_source_content()
        assert retrieved_content == test_content

        # Тест AI редактора
        ai_content = "# AI generated code"
        code_editor_view.set_ai_content(ai_content)
        assert code_editor_view.get_ai_content() == ai_content

        # Очистка AI редактора
        code_editor_view.clear_ai_content()
        assert code_editor_view.get_ai_content() == ""

    def test_main_window_view_gui(self, main_window_view):
        """GUI тест MainWindowView."""
        assert main_window_view is not None

        # Проверяем виджеты
        assert main_window_view.top_panel.winfo_exists()
        assert main_window_view.content_panel.winfo_exists()
        assert main_window_view.status_label.winfo_exists()

        # Тест установки статуса
        test_status = "Test status"
        main_window_view.set_status(test_status)
        assert main_window_view.status_label.cget('text') == test_status

        # Проверяем кнопки
        assert main_window_view.create_project_button.winfo_exists()
        assert main_window_view.open_project_button.winfo_exists()
        assert main_window_view.create_structure_button.winfo_exists()

    def test_project_tree_view_gui(self, project_tree_view, sample_project_structure):
        """GUI тест ProjectTreeView."""
        assert project_tree_view is not None

        # Заполняем дерево тестовой структурой
        project_tree_view.fill_tree(sample_project_structure)

        # Проверяем что элементы добавлены
        assert len(project_tree_view.all_tree_items) > 0

        # Тест поиска
        results = project_tree_view.search_elements("app")
        assert isinstance(results, list)

        # Тест подсветки результатов
        if results:
            project_tree_view.highlight_search_results(results)
            # Просто проверяем что метод не падает

        # Тест методов раскрытия/сворачивания
        project_tree_view.expand_all()
        project_tree_view.collapse_all()
        # Просто проверяем что методы не падают


@pytest.mark.gui
@pytest.mark.requires_tkinter
class TestGUIComponentInteraction(BaseGUITest):
    """Тесты взаимодействия GUI компонентов."""

    def test_window_hierarchy(self, tk_root):
        """Тест иерархии окон."""
        from gui.views.code_editor_view import CodeEditorView
        from gui.views.main_window_view import MainWindowView

        # Создаем главное окно
        main_view = MainWindowView(tk_root)

        # Создаем редактор кода внутри content_panel
        editor = CodeEditorView(main_view.content_panel)

        # Проверяем иерархию
        assert editor.winfo_parent() == str(main_view.content_panel)
        assert main_view.winfo_parent() == str(tk_root)

    def test_component_initialization_order(self, tk_root):
        """Тест порядка инициализации компонентов."""
        from gui.views.main_window_view import MainWindowView
        from gui.views.project_tree_view import ProjectTreeView

        # Создаем компоненты
        main_view = MainWindowView(tk_root)
        tree_view = ProjectTreeView(main_view.content_panel)

        # Проверяем что компоненты созданы
        assert main_view is not None
        assert tree_view is not None
        assert tree_view.parent == main_view.content_panel
