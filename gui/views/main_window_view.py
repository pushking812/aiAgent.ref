# gui/views/main_window_view.py

from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox

class IMainWindowView(ABC):
    def set_status(self, text: str): pass
    def show_info(self, title: str, msg: str): pass
    def show_error(self, title: str, msg: str): pass
    def show_warning(self, title: str, msg: str): pass
    def bind_create_project(self, callback): pass
    def bind_open_project(self, callback): pass
    def bind_create_structure(self, callback): pass

class MainWindowView(ttk.Frame, IMainWindowView):
    def __init__(self, root):
        super().__init__(root)
        self.pack(fill=tk.BOTH, expand=True)

        # Верхняя панель с кнопками
        self.top_panel = ttk.Frame(self)
        self.top_panel.pack(fill=tk.X, pady=(0, 5))

        self.create_project_button = ttk.Button(self.top_panel, text="Создать проект")
        self.create_project_button.pack(side=tk.LEFT, padx=(5, 5))

        self.open_project_button = ttk.Button(self.top_panel, text="Открыть проект")
        self.open_project_button.pack(side=tk.LEFT, padx=(5, 5))

        self.create_structure_button = ttk.Button(self.top_panel, text="Структура из AI")
        self.create_structure_button.pack(side=tk.LEFT, padx=(5, 5))

        self.content_panel = ttk.Frame(self)
        self.content_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.status_label = ttk.Label(self, text="Проект не открыт")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

    def set_status(self, text: str):
        """
        Установить строку статуса приложения.
        """
        self.status_label.config(text=text)

    def show_info(self, title: str, msg: str):
        """
        Показать информационное сообщение.
        """
        messagebox.showinfo(title, msg)

    def show_error(self, title: str, msg: str):
        """
        Показать сообщение об ошибке.
        """
        messagebox.showerror(title, msg)

    def show_warning(self, title: str, msg: str):
        """
        Показать предупреждение.
        """
        messagebox.showwarning(title, msg)

    def bind_create_project(self, callback):
        """
        Привязать обработчик к кнопке 'Создать проект'.
        """
        self.create_project_button.config(command=callback)

    def bind_open_project(self, callback):
        """
        Привязать обработчик к кнопке 'Открыть проект'.
        """
        self.open_project_button.config(command=callback)

    def bind_create_structure(self, callback):
        """
        Привязать обработчик к кнопке 'Структура из AI'.
        """
        self.create_structure_button.config(command=callback)