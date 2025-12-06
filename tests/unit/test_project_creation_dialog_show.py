# tests/unit/test_project_creation_dialog_show.py

"""Специализированные тесты для метода show ProjectCreationDialog (строки 110-225)"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import os
from gui.views.dialogs_view import ProjectCreationDialog


class TestProjectCreationDialogShowDetailed:
    """Детальные тесты метода show ProjectCreationDialog."""
    
    @patch('tkinter.Toplevel')
    @patch('tkinter.ttk.Frame')
    @patch('tkinter.ttk.Label')
    @patch('tkinter.ttk.Entry')
    @patch('tkinter.ttk.Button')
    @patch('tkinter.ttk.Radiobutton')
    @patch('tkinter.StringVar')
    def test_show_creates_all_widgets(self, mock_stringvar, mock_radiobutton, mock_entry,
                                     mock_button, mock_label, mock_ttk_frame, mock_toplevel,
                                     mock_tk_parent, mock_project_manager):
        """Тест что show создает все виджеты."""
        # Настраиваем моки
        mock_window = MagicMock()
        mock_window._last_child_ids = {}
        mock_window.title = Mock()
        mock_window.geometry = Mock()
        mock_window.transient = Mock()
        mock_window.grab_set = Mock()
        mock_window.wait_window = Mock(return_value=None)
        
        mock_toplevel.return_value = mock_window
        
        # StringVar моки
        mock_path_var = MagicMock()
        mock_name_var = MagicMock()
        mock_type_var = MagicMock()
        mock_stringvar.side_effect = [mock_path_var, mock_name_var, mock_type_var]
        
        # Frame моки
        mock_main_frame = MagicMock()
        mock_main_frame._last_child_ids = {}
        mock_main_frame.pack = Mock()
        
        mock_path_frame = MagicMock()
        mock_path_frame._last_child_ids = {}
        mock_path_frame.grid = Mock()
        
        mock_name_frame = MagicMock()
        mock_name_frame._last_child_ids = {}
        mock_name_frame.grid = Mock()
        
        mock_type_frame = MagicMock()
        mock_type_frame._last_child_ids = {}
        mock_type_frame.grid = Mock()
        
        mock_button_frame = MagicMock()
        mock_button_frame._last_child_ids = {}
        mock_button_frame.grid = Mock()
        
        mock_ttk_frame.side_effect = [
            mock_main_frame, mock_path_frame, mock_name_frame, 
            mock_type_frame, mock_button_frame
        ]
        
        # Label моки
        mock_labels = []
        for _ in range(5):  # Ожидаем примерно 5 меток
            mock_label_instance = MagicMock()
            mock_label_instance._last_child_ids = {}
            mock_label_instance.grid = Mock()
            mock_labels.append(mock_label_instance)
        
        mock_label.side_effect = mock_labels
        
        # Entry моки
        mock_path_entry = MagicMock()
        mock_path_entry._last_child_ids = {}
        mock_path_entry.grid = Mock()
        
        mock_name_entry = MagicMock()
        mock_name_entry._last_child_ids = {}
        mock_name_entry.grid = Mock()
        
        mock_entry.side_effect = [mock_path_entry, mock_name_entry]
        
        # Button моки
        mock_browse_button = MagicMock()
        mock_browse_button._last_child_ids = {}
        mock_browse_button.grid = Mock()
        
        mock_cancel_button = MagicMock()
        mock_cancel_button._last_child_ids = {}
        mock_cancel_button.grid = Mock()
        
        mock_create_button = MagicMock()
        mock_create_button._last_child_ids = {}
        mock_create_button.grid = Mock()
        
        mock_button.side_effect = [mock_browse_button, mock_cancel_button, mock_create_button]
        
        # Radiobutton моки
        mock_empty_rb = MagicMock()
        mock_empty_rb._last_child_ids = {}
        mock_empty_rb.grid = Mock()
        
        mock_template_rb = MagicMock()
        mock_template_rb._last_child_ids = {}
        mock_template_rb.grid = Mock()
        
        mock_radiobutton.side_effect = [mock_empty_rb, mock_template_rb]
        
        # Создаем диалог
        dialog = ProjectCreationDialog(mock_tk_parent, mock_project_manager)
        
        # Мокаем os.path.exists и os.listdir для простого случая
        with patch('os.path.exists', return_value=False), \
             patch('os.listdir', return_value=[]):
            
            # Запускаем show
            result = dialog.show()
            
            # Проверяем что окно было создано
            mock_toplevel.assert_called_once()
            
            # Проверяем настройки окна
            mock_window.title.assert_called()
            mock_window.geometry.assert_called()
            mock_window.transient.assert_called_with(mock_tk_parent)
            mock_window.grab_set.assert_called_once()
            mock_window.wait_window.assert_called_once()
            
            # Проверяем что были созданы StringVar
            assert mock_stringvar.call_count >= 3
            
            # Проверяем что были созданы фреймы
            assert mock_ttk_frame.call_count >= 5
            
            # Проверяем что были созданы метки
            assert mock_label.call_count >= 3
            
            # Проверяем что были созданы поля ввода
            assert mock_entry.call_count >= 2
            
            # Проверяем что были созданы кнопки
            assert mock_button.call_count >= 3
            
            # Проверяем что были созданы радиокнопки
            assert mock_radiobutton.call_count >= 2
    
    @patch('tkinter.Toplevel')
    @patch('tkinter.ttk.Frame')
    @patch('tkinter.ttk.Label')
    @patch('tkinter.ttk.Entry')
    @patch('tkinter.ttk.Button')
    @patch('tkinter.ttk.Radiobutton')
    @patch('tkinter.StringVar')
    def test_show_with_existing_directory(self, mock_stringvar, mock_radiobutton, mock_entry,
                                         mock_button, mock_label, mock_ttk_frame, mock_toplevel,
                                         mock_tk_parent, mock_project_manager):
        """Тест show с существующей директорией."""
        # Настраиваем базовые моки
        mock_window = MagicMock()
        mock_window.wait_window = Mock(return_value=None)
        mock_toplevel.return_value = mock_window
        
        # Настраиваем остальные моки
        mock_path_var = MagicMock()
        mock_name_var = MagicMock()
        mock_type_var = MagicMock()
        mock_stringvar.side_effect = [mock_path_var, mock_name_var, mock_type_var]
        
        # Моки для остальных виджетов
        mock_ttk_frame.return_value = MagicMock()
        mock_label.return_value = MagicMock()
        mock_entry.return_value = MagicMock()
        mock_button.return_value = MagicMock()
        mock_radiobutton.return_value = MagicMock()
        
        dialog = ProjectCreationDialog(mock_tk_parent, mock_project_manager)
        
        # Мокаем os.path.exists и os.listdir для случая существующей непустой директории
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=["file1.txt", "file2.txt"]), \
             patch('gui.views.dialogs_view.DirectoryOverwriteDialog') as mock_overwrite_class:
            
            # Мокаем диалог перезаписи
            mock_overwrite_dialog = Mock()
            mock_overwrite_dialog.show.return_value = True  # Пользователь согласился
            mock_overwrite_class.return_value = mock_overwrite_dialog
            
            # Запускаем show
            result = dialog.show()
            
            # Проверяем что DirectoryOverwriteDialog был вызван
            mock_overwrite_class.assert_called_once()
            mock_overwrite_dialog.show.assert_called_once()
    
    def test_on_cancel_method(self, mock_tk_parent, mock_project_manager):
        """Тест метода _on_cancel."""
        with patch.object(ProjectCreationDialog, '__init__', lambda self, parent, pm: None):
            dialog = ProjectCreationDialog(mock_tk_parent, mock_project_manager)
            
            # Создаем мок окна
            mock_window = Mock()
            dialog.dialog_window = mock_window
            
            # Вызываем _on_cancel
            dialog._on_cancel()
            
            # Окно должно быть уничтожено
            mock_window.destroy.assert_called_once()
    
    @patch('tkinter.filedialog.askdirectory')
    def test_browse_path_method(self, mock_askdirectory, mock_tk_parent, mock_project_manager):
        """Тест метода _browse_path."""
        with patch.object(ProjectCreationDialog, '__init__', lambda self, parent, pm: None):
            dialog = ProjectCreationDialog(mock_tk_parent, mock_project_manager)
            
            # Создаем мок для path_var
            mock_path_var = Mock()
            dialog.path_var = mock_path_var
            
            # Тест 1: Пользователь выбрал путь
            test_path = "/selected/path"
            mock_askdirectory.return_value = test_path
            
            dialog._browse_path()
            
            mock_askdirectory.assert_called_with(title="Выберите папку для создания проекта")
            mock_path_var.set.assert_called_with(test_path)
            
            # Сброс моков
            mock_askdirectory.reset_mock()
            mock_path_var.reset_mock()
            
            # Тест 2: Пользователь отменил (пустая строка)
            mock_askdirectory.return_value = ""
            
            dialog._browse_path()
            
            mock_askdirectory.assert_called_with(title="Выберите папку для создания проекта")
            mock_path_var.set.assert_not_called()  # Не должно устанавливать пустую строку