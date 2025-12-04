# gui/views/dialogs_view.py

from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox

class IDialogsView(ABC):
    def ask_save_changes(self, filename: str): pass
    def show_diff(self, diff_text: str): pass
    def show_info_dialog(self, title: str, message: str): pass
    def show_error_dialog(self, title: str, message: str): pass

class DialogsView(IDialogsView):
    """
    Реализация диалоговых окон: подтверждение, сравнение, сообщения.
    """
    def ask_save_changes(self, filename: str):
        """
        Диалог подтверждения сохранения изменений в файле.
        Возвращает: True (Да), False (Нет), None (Отмена)
        """
        return messagebox.askyesnocancel("Сохранить изменения",
            f"Сохранить изменения в файле {filename}?")

    def show_diff(self, diff_text: str, title: str = "Сравнение изменений"):
        """
        Открыть окно с текстом различий для сравнения файлов/версий.
        """
        win = tk.Toplevel()
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
        win.transient()
        win.grab_set()
        win.wait_window()

    def show_info_dialog(self, title: str, message: str):
        """
        Обычный инфо-диалог (например, после успешной операции).
        """
        messagebox.showinfo(title, message)

    def show_error_dialog(self, title: str, message: str):
        """
        Ошибка или предупреждение.
        """
        messagebox.showerror(title, message)