# gui/views/dialogs_view.py

from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from typing import Optional, Tuple, Any, List
import logging

logger = logging.getLogger('ai_code_assistant')


class IDialogsView(ABC):
    def ask_save_changes(self, filename: str): pass
    def show_diff(self, diff_text: str, title: str): pass
    def show_info_dialog(self, title: str, message: str): pass
    def show_error_dialog(self, title: str, message: str): pass
    def show_warning_dialog(self, title: str, message: str): pass
    def ask_directory(self, title: str) -> Optional[str]: pass
    def show_project_creation_dialog(self, project_manager) -> Optional[Tuple]: pass
    def show_directory_overwrite_dialog(self, directory_path: str, project_name: str) -> bool: pass


class DialogsView(IDialogsView):
    """
    Расширенная реализация диалоговых окон с поддержкой создания проектов.
    """
    
    def __init__(self, parent):
        self.parent = parent

    def ask_save_changes(self, filename: str):
        """
        Диалог подтверждения сохранения изменений в файле.
        Возвращает: True (Да), False (Нет), None (Отмена)
        """
        return messagebox.askyesnocancel(
            "Сохранить изменения",
            f"Сохранить изменения в файле {filename}?"
        )

    def show_diff(self, diff_text: str, title: str = "Сравнение изменений"):
        """
        Открыть окно с текстом различий для сравнения файлов/версий.
        """
        win = tk.Toplevel(self.parent)
        win.title(title)
        win.geometry("600x400")
        
        diff_frame = ttk.Frame(win)
        diff_frame.pack(fill=tk.BOTH, expand=True)
        
        text = tk.Text(diff_frame, wrap=tk.NONE)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert("1.0", diff_text)
        text.config(state=tk.DISABLED)
        
        close_btn = ttk.Button(diff_frame, text="Закрыть", command=win.destroy)
        close_btn.pack(pady=5)
        
        win.transient(self.parent)
        win.grab_set()
        win.wait_window()

    def show_info_dialog(self, title: str, message: str):
        """Обычный инфо-диалог."""
        messagebox.showinfo(title, message)

    def show_error_dialog(self, title: str, message: str):
        """Ошибка или предупреждение."""
        messagebox.showerror(title, message)

    def show_warning_dialog(self, title: str, message: str):
        """Показать предупреждение."""
        messagebox.showwarning(title, message)

    def ask_directory(self, title: str) -> Optional[str]:
        """Открывает диалог выбора директории."""
        return filedialog.askdirectory(title=title)

    def show_project_creation_dialog(self, project_manager) -> Optional[Tuple]:
        """
        Диалог создания нового проекта.
        Возвращает: (path, name, template_name, is_empty, full_project_path) или None
        """
        dialog = ProjectCreationDialog(self.parent, project_manager)
        return dialog.show()

    def show_directory_overwrite_dialog(self, directory_path: str, project_name: str) -> bool:
        """
        Диалог подтверждения перезаписи директории.
        Возвращает: True (перезаписать), False (отмена)
        """
        dialog = DirectoryOverwriteDialog(self.parent, directory_path, project_name)
        return dialog.show()


class ProjectCreationDialog:
    """Диалог создания нового проекта (адаптирован из старого кода)"""
    
    def __init__(self, parent, project_manager):
        self.parent = parent
        self.project_manager = project_manager
        self.result = None
        
        logger.debug("Инициализирован ProjectCreationDialog")
    
    def show(self) -> Optional[Tuple]:
        """Показывает диалог и возвращает результат"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Создание проекта")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Центрируем диалог
        dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        result = [None]
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(main_frame, text="Создание нового проекта", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 20))
        
        # Путь проекта
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(path_frame, text="Путь:").pack(anchor=tk.W)
        
        path_entry_frame = ttk.Frame(path_frame)
        path_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(path_entry_frame, textvariable=self.path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(path_entry_frame, text="Обзор...", 
                  command=self._browse_path).pack(side=tk.RIGHT)
        
        # Имя проекта
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(name_frame, text="Имя проекта:").pack(anchor=tk.W)
        
        self.name_var = tk.StringVar(value="new_python_project")
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var)
        name_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Выбор типа проекта
        type_frame = ttk.LabelFrame(main_frame, text="Тип проекта", padding="10")
        type_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.project_type_var = tk.StringVar(value="empty")
        
        ttk.Radiobutton(
            type_frame, 
            text="📁 Пустой проект",
            variable=self.project_type_var, 
            value="empty"
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(
            type_frame, 
            text="📋 Проект из шаблона", 
            variable=self.project_type_var, 
            value="template"
        ).pack(anchor=tk.W, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def on_ok():
            path = self.path_var.get().strip()
            name = self.name_var.get().strip()
            
            if not path:
                messagebox.showwarning("Ошибка", "Укажите путь для создания проекта")
                return
            
            if not name:
                messagebox.showwarning("Ошибка", "Укажите имя проекта")
                return
            
            # Формируем полный путь к проекту
            full_project_path = os.path.join(path, name)
            
            # Проверяем, существует ли директория
            if os.path.exists(full_project_path) and os.listdir(full_project_path):
                # Директория не пуста - показываем диалог перезаписи
                from .dialogs_view import DirectoryOverwriteDialog
                overwrite_dialog = DirectoryOverwriteDialog(dialog, full_project_path, name)
                if not overwrite_dialog.show():
                    return
            
            project_type = self.project_type_var.get()
            is_empty = (project_type == "empty")
            template_name = None if is_empty else "python_basic"  # Упрощенная версия
            
            result[0] = (path, name, template_name, is_empty, full_project_path)
            dialog.destroy()
        
        def on_cancel():
            result[0] = None
            dialog.destroy()
        
        ttk.Button(button_frame, text="Отмена", command=on_cancel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Создать", command=on_ok).pack(side=tk.RIGHT, padx=5)
        
        # Фокус на диалог
        dialog.focus_set()
        
        # Ждем закрытия
        self.parent.wait_window(dialog)
        
        return result[0]
    
    def _browse_path(self):
        """Открывает диалог выбора пути"""
        path = filedialog.askdirectory(title="Выберите папку для создания проекта")
        if path:
            self.path_var.set(path)


class DirectoryOverwriteDialog:
    """Диалог подтверждения перезаписи директории"""
    
    def __init__(self, parent, directory_path: str, project_name: str):
        self.parent = parent
        self.directory_path = directory_path
        self.project_name = project_name
        
        logger.debug("Инициализирован DirectoryOverwriteDialog для %s", directory_path)
    
    def show(self) -> bool:
        """Показывает диалог и возвращает результат"""
        result = messagebox.askyesno(
            "Подтверждение перезаписи",
            f"Директория '{self.project_name}' уже существует и содержит файлы.\n"
            f"Все существующие файлы будут удалены!\n\n"
            f"Продолжить?"
        )
        return result