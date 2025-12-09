# gui/views/dialogs_view.py

from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from typing import Optional, Tuple, Any, List

from gui.utils.ui_factory import ui_factory

import logging
logger = logging.getLogger('ai_code_assistant')


class IDialogsView(ABC):
    def ask_save_changes(self, filename: str): pass
    def show_diff(self, diff_text: str, title: str): pass
    def show_info_dialog(self, title: str, message: str): pass
    def show_error_dialog(self, title: str, message: str): pass
    def show_warning_dialog(self, title: str, message: str) -> bool: pass
    def ask_directory(self, title: str) -> Optional[str]: pass
    def show_project_creation_dialog(self, project_manager) -> Optional[Tuple]: pass
    def show_directory_overwrite_dialog(self, directory_path: str, project_name: str) -> bool: pass
    def show_pending_changes_dialog(self, changes: List) -> bool: pass


class DialogsView(IDialogsView):
    """Реализация диалоговых окон с использованием фабрики UI."""
    
    def __init__(self, parent):
        self.parent = parent

    def ask_save_changes(self, filename: str):
        """Диалог подтверждения сохранения изменений в файле."""
        return messagebox.askyesnocancel(
            "Сохранить изменения",
            f"Сохранить изменения в файле {filename}?"
        )

    def show_diff(self, diff_text: str, title: str = "Сравнение изменений"):
        """Открыть окно с текстом различий для сравнения файлов/версий."""
        win = tk.Toplevel(self.parent)
        win.title(title)
        win.geometry("600x400")
        
        diff_frame = ui_factory.create_frame(win)
        diff_frame.pack(fill=tk.BOTH, expand=True)
        
        text = ui_factory.create_scrolled_text(diff_frame, wrap=tk.NONE)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert("1.0", diff_text)
        text.config(state=tk.DISABLED)
        
        close_btn = ui_factory.create_button(diff_frame, text="Закрыть", command=win.destroy)
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

    def show_warning_dialog(self, title: str, message: str) -> bool:
        """Показать предупреждение с подтверждением."""
        return messagebox.askyesno(title, message)

    def ask_directory(self, title: str) -> Optional[str]:
        """Открывает диалог выбора директории."""
        return filedialog.askdirectory(title=title)

    def show_project_creation_dialog(self, project_manager) -> Optional[Tuple]:
        """Диалог создания нового проекта."""
        dialog = ProjectCreationDialog(self.parent, project_manager)
        return dialog.show()

    def show_directory_overwrite_dialog(self, directory_path: str, project_name: str) -> bool:
        """Диалог подтверждения перезаписи директории."""
        dialog = DirectoryOverwriteDialog(self.parent, directory_path, project_name)
        return dialog.show()

    def show_pending_changes_dialog(self, changes: List) -> bool:
        """Показать диалог отложенных изменений."""
        dialog = PendingChangesDialog(self.parent, changes)
        return dialog.show()


class ProjectCreationDialog:
    """Диалог создания нового проекта с использованием фабрики UI."""
    
    def __init__(self, parent, project_manager):
        self.parent = parent
        self.project_manager = project_manager
        self.result = None
        
        logger.debug("Инициализирован ProjectCreationDialog")
    
    def show(self) -> Optional[Tuple]:
        """Показывает диалог и возвращает результат."""
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
        
        main_frame = ui_factory.create_frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ui_factory.create_label(
            main_frame,
            text="Создание нового проекта",
            bold=True
        )
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Путь проекта
        path_frame = ui_factory.create_frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        path_label = ui_factory.create_label(path_frame, text="Путь:")
        path_label.pack(anchor=tk.W)
        
        path_entry_frame = ui_factory.create_frame(path_frame)
        path_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.path_var = tk.StringVar()
        path_entry = ui_factory.create_entry(
            path_entry_frame,
            textvariable=self.path_var,
            tooltip="Путь для создания проекта"
        )
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ui_factory.create_button(
            path_entry_frame,
            text="Обзор...",
            tooltip="Выбрать папку",
            command=self._browse_path
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Имя проекта
        name_frame = ui_factory.create_frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 20))
        
        name_label = ui_factory.create_label(name_frame, text="Имя проекта:")
        name_label.pack(anchor=tk.W)
        
        self.name_var = tk.StringVar(value="new_python_project")
        name_entry = ui_factory.create_entry(
            name_frame,
            textvariable=self.name_var,
            tooltip="Имя нового проекта"
        )
        name_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Выбор типа проекта
        type_frame = ui_factory.create_label_frame(main_frame, text="Тип проекта", padding=10)
        type_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.project_type_var = tk.StringVar(value="empty")
        
        empty_rb = ttk.Radiobutton(
            type_frame,
            text="📁 Пустой проект",
            variable=self.project_type_var,
            value="empty"
        )
        empty_rb.pack(anchor=tk.W, pady=5)
        
        template_rb = ttk.Radiobutton(
            type_frame,
            text="📋 Проект из шаблона",
            variable=self.project_type_var,
            value="template"
        )
        template_rb.pack(anchor=tk.W, pady=5)
        
        # Кнопки
        button_frame = ui_factory.create_frame(main_frame)
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
            
            full_project_path = os.path.join(path, name)
            
            if os.path.exists(full_project_path) and os.listdir(full_project_path):
                overwrite_dialog = DirectoryOverwriteDialog(dialog, full_project_path, name)
                if not overwrite_dialog.show():
                    return
            
            project_type = self.project_type_var.get()
            is_empty = (project_type == "empty")
            template_name = None if is_empty else "python_basic"
            
            result[0] = (path, name, template_name, is_empty, full_project_path)
            dialog.destroy()
        
        def on_cancel():
            result[0] = None
            dialog.destroy()
        
        cancel_btn = ui_factory.create_button(
            button_frame,
            text="Отмена",
            command=on_cancel
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        create_btn = ui_factory.create_button(
            button_frame,
            text="Создать",
            command=on_ok
        )
        create_btn.pack(side=tk.RIGHT, padx=5)
        
        dialog.focus_set()
        self.parent.wait_window(dialog)
        
        return result[0]
    
    def _browse_path(self):
        """Открывает диалог выбора пути."""
        path = filedialog.askdirectory(title="Выберите папку для создания проекта")
        if path:
            self.path_var.set(path)


class DirectoryOverwriteDialog:
    """Диалог подтверждения перезаписи директории."""
    
    def __init__(self, parent, directory_path: str, project_name: str):
        self.parent = parent
        self.directory_path = directory_path
        self.project_name = project_name
        
        logger.debug(f"Инициализирован DirectoryOverwriteDialog для {directory_path}")
    
    def show(self) -> bool:
        """Показывает диалог и возвращает результат."""
        result = messagebox.askyesno(
            "Подтверждение перезаписи",
            f"Директория '{self.project_name}' уже существует и содержит файлы.\n"
            f"Все существующие файлы будут удалены!\n\n"
            f"Продолжить?"
        )
        return result


class PendingChangesDialog:
    """Диалог отложенных изменений с использованием фабрики UI."""
    
    def __init__(self, parent, changes: List):
        self.parent = parent
        self.changes = changes
        self.result = False
    
    def show(self) -> bool:
        """Показать диалог."""
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Отложенные изменения ({len(self.changes)})")
        dialog.geometry("600x400")
        
        main_frame = ui_factory.create_frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Список изменений
        tree_frame = ui_factory.create_frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        columns = ('action', 'entity', 'file')
        tree = ui_factory.create_treeview(tree_frame, columns=columns, show='headings')
        
        tree.heading('action', text='Действие')
        tree.heading('entity', text='Элемент')
        tree.heading('file', text='Файл')
        
        tree.column('action', width=100)
        tree.column('entity', width=200)
        tree.column('file', width=200)
        
        for change in self.changes:
            tree.insert('', 'end', values=(
                change.get('action', ''),
                change.get('entity', ''),
                change.get('file', '')
            ))
        
        scrollbar = ui_factory.create_scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки
        button_frame = ui_factory.create_frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def on_apply():
            self.result = True
            dialog.destroy()
        
        def on_discard():
            self.result = False
            dialog.destroy()
        
        apply_btn = ui_factory.create_button(
            button_frame,
            text="Применить",
            command=on_apply
        )
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        discard_btn = ui_factory.create_button(
            button_frame,
            text="Отменить",
            command=on_discard
        )
        discard_btn.pack(side=tk.RIGHT, padx=5)
        
        dialog.transient(self.parent)
        dialog.grab_set()
        self.parent.wait_window(dialog)
        
        return self.result