# tests/gui/test_dialogs_view_gui.py

"""GUI тесты для dialogs_view.py (требуют tkinter)"""

import pytest
import tkinter as tk
from tkinter import ttk
from gui.views.dialogs_view import DialogsView, ProjectCreationDialog, DirectoryOverwriteDialog


@pytest.fixture
def tk_root():
    """Создает корневое окно Tkinter для тестов."""
    try:
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        yield root
        root.destroy()
    except tk.TclError:
        pytest.skip("Tkinter не доступен")


@pytest.mark.gui
@pytest.mark.requires_tkinter
class TestDialogsViewWithTkinter:
    """Тесты DialogsView с реальным Tkinter."""
    
    def test_dialogs_view_creation(self, tk_root):
        """Тест создания DialogsView с реальным Tkinter."""
        dialogs = DialogsView(tk_root)
        assert dialogs is not None
        assert dialogs.parent == tk_root
    
    def test_project_creation_dialog_creation(self, tk_root):
        """Тест создания ProjectCreationDialog с реальным Tkinter."""
        mock_pm = Mock()
        dialog = ProjectCreationDialog(tk_root, mock_pm)
        assert dialog is not None
        assert dialog.parent == tk_root
        assert dialog.project_manager == mock_pm


@pytest.mark.gui
@pytest.mark.requires_tkinter
class TestDialogsViewRealMethods:
    """Тесты реальных методов с Tkinter."""
    
    def test_show_diff_exists(self, tk_root):
        """Тест что метод show_diff существует и может быть вызван."""
        dialogs = DialogsView(tk_root)
        
        # Создаем простое окно и сразу закрываем его
        from unittest.mock import patch
        
        with patch.object(tk.Toplevel, 'wait_window'):
            # Просто проверяем что метод не падает
            try:
                dialogs.show_diff("test diff", "Test")
                # Если не упало - хорошо
                assert True
            except Exception as e:
                # Игнорируем ошибки связанные с wait_window
                if 'wait_window' not in str(e):
                    raise
    
    def test_directory_overwrite_dialog_show(self, tk_root):
        """Тест метода show DirectoryOverwriteDialog."""
        dialog = DirectoryOverwriteDialog(tk_root, "/test/path", "TestProject")
        
        from unittest.mock import patch
        with patch('tkinter.messagebox.askyesno', return_value=True):
            result = dialog.show()
            assert result is True