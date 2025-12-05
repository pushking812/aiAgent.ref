# tests/test_dialogs_view.py

import tkinter as tk
import pytest
from unittest.mock import Mock, patch, MagicMock
from gui.views.dialogs_view import DialogsView, ProjectCreationDialog, DirectoryOverwriteDialog


class TestDialogsView:
    """Тесты для DialogsView"""
    
    @pytest.fixture
    def root(self):
        """Создает корневое окно для тестов."""
        return tk.Tk()
    
    @pytest.fixture
    def dialogs(self, root):
        """Создает экземпляр DialogsView."""
        return DialogsView(root)
    
    @patch('tkinter.messagebox.askyesnocancel')
    def test_ask_save_changes(self, mock_ask, dialogs):
        """Тест диалога сохранения изменений."""
        mock_ask.return_value = True
        result = dialogs.ask_save_changes("test.py")
        
        mock_ask.assert_called_once_with(
            "Сохранить изменения",
            "Сохранить изменения в файле test.py?"
        )
        assert result is True
    
    @patch('tkinter.messagebox.showinfo')
    def test_show_info_dialog(self, mock_showinfo, dialogs):
        """Тест информационного диалога."""
        dialogs.show_info_dialog("Тест", "Сообщение")
        
        mock_showinfo.assert_called_once_with("Тест", "Сообщение")
    
    @patch('tkinter.messagebox.showerror')
    def test_show_error_dialog(self, mock_showerror, dialogs):
        """Тест диалога ошибки."""
        dialogs.show_error_dialog("Ошибка", "Описание")
        
        mock_showerror.assert_called_once_with("Ошибка", "Описание")
    
    @patch('tkinter.messagebox.showwarning')
    def test_show_warning_dialog(self, mock_showwarning, dialogs):
        """Тест диалога предупреждения."""
        dialogs.show_warning_dialog("Предупреждение", "Внимание!")
        
        mock_showwarning.assert_called_once_with("Предупреждение", "Внимание!")
    
    @patch('tkinter.filedialog.askdirectory')
    def test_ask_directory(self, mock_askdirectory, dialogs):
        """Тест диалога выбора директории."""
        mock_askdirectory.return_value = "/test/path"
        result = dialogs.ask_directory("Выберите папку")
        
        mock_askdirectory.assert_called_once_with(title="Выберите папку")
        assert result == "/test/path"
    
    @patch('gui.views.dialogs_view.filedialog.askdirectory')
    def test_project_creation_dialog_browse(self, mock_askdirectory, root):
        """Тест кнопки обзора в диалоге создания проекта."""
        project_manager = Mock()
        dialog = ProjectCreationDialog(root, project_manager)
        
        mock_askdirectory.return_value = "/selected/path"
        dialog._browse_path()
        
        assert dialog.path_var.get() == "/selected/path"
        mock_askdirectory.assert_called_once_with(title="Выберите папку для создания проекта")
    
    @patch('tkinter.messagebox.showwarning')
    @patch('tkinter.messagebox.askyesno')
    def test_directory_overwrite_dialog(self, mock_askyesno, mock_showwarning, root):
        """Тест диалога перезаписи директории."""
        mock_askyesno.return_value = True
        dialog = DirectoryOverwriteDialog(root, "/test/path", "TestProject")
        
        result = dialog.show()
        
        mock_askyesno.assert_called_once()
        assert result is True
    
    def test_diff_dialog_creation(self, dialogs):
        """Тест создания диалога сравнения."""
        # Используем патч для Toplevel, чтобы не создавать реальное окно
        with patch('tkinter.Toplevel') as mock_toplevel:
            mock_window = MagicMock()
            mock_toplevel.return_value = mock_window
            
            dialogs.show_diff("diff text", "Сравнение")
            
            # Проверяем, что окно было создано
            mock_toplevel.assert_called_once()
            mock_window.title.assert_called_with("Сравнение")
    
    def test_project_creation_dialog_initialization(self, root):
        """Тест инициализации диалога создания проекта."""
        project_manager = Mock()
        dialog = ProjectCreationDialog(root, project_manager)
        
        assert dialog.parent == root
        assert dialog.project_manager == project_manager
        assert dialog.result is None
    
    @patch('tkinter.messagebox.showwarning')
    def test_project_creation_dialog_validation(self, mock_showwarning, root):
        """Тест валидации в диалоге создания проекта."""
        project_manager = Mock()
        dialog = ProjectCreationDialog(root, project_manager)
        
        # Пустой путь
        dialog.path_var.set("")
        dialog.name_var.set("TestProject")
        
        # Симулируем нажатие OK
        dialog._on_ok()
        
        mock_showwarning.assert_called_once_with("Ошибка", "Укажите путь для создания проекта")
    
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('gui.views.dialogs_view.DirectoryOverwriteDialog')
    def test_project_creation_directory_exists(self, mock_overwrite_dialog, 
                                               mock_listdir, mock_exists, root):
        """Тест обработки существующей директории."""
        project_manager = Mock()
        dialog = ProjectCreationDialog(root, project_manager)
        
        # Настраиваем моки
        mock_exists.return_value = True
        mock_listdir.return_value = ["file1.py", "file2.py"]
        mock_overwrite_instance = Mock()
        mock_overwrite_instance.show.return_value = True
        mock_overwrite_dialog.return_value = mock_overwrite_instance
        
        dialog.path_var.set("/test")
        dialog.name_var.set("existing_project")
        
        # Симулируем нажатие OK
        dialog._on_ok()
        
        # Проверяем, что диалог перезаписи был вызван
        mock_overwrite_dialog.assert_called_once()


class TestIntegration:
    """Интеграционные тесты"""
    
    @pytest.fixture
    def app(self):
        """Создает простое приложение для тестов."""
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        return root
    
    def test_dialogs_view_creation(self, app):
        """Тест создания DialogsView."""
        dialogs = DialogsView(app)
        assert dialogs.parent == app
    
    @patch('tkinter.Tk')
    def test_dialog_parent_relationship(self, mock_tk):
        """Тест отношения родитель-потомок в диалогах."""
        mock_parent = MagicMock()
        dialogs = DialogsView(mock_parent)
        
        assert dialogs.parent == mock_parent


if __name__ == '__main__':
    pytest.main([__file__, '-v'])