# gui/utils/gui_helpers.py

import tkinter as tk
from tkinter import ttk

def center_window(window, width=800, height=600):
    """
    Центрирует окно на экране.
    """
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def add_tooltip(widget, text):
    """
    Добавляет tooltip с заданным текстом к widget (правильный ХВ).
    """
    def on_enter(event):
        widget._tooltip = tk.Toplevel(widget)
        widget._tooltip.wm_overrideredirect(True)
        widget._tooltip.wm_geometry(
            f"+{widget.winfo_rootx() + 20}+{widget.winfo_rooty() + 20}"
        )
        label = tk.Label(widget._tooltip, text=text, background="#ffffe0", borderwidth=1, relief="solid")
        label.pack(ipadx=2, ipady=2)

    def on_leave(event):
        if getattr(widget, "_tooltip", None):
            widget._tooltip.destroy()
            widget._tooltip = None
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def clear_frame(frame):
    """
    Удаляет все дочерние виджеты внутри заданного frame.
    """
    for child in frame.winfo_children():
        child.destroy()

def set_uniform_style():
    """
    Устанавливает единый стиль для ttk-виджетов.
    Можно доработать для темы.
    """
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', font=('Arial', 10))
    style.configure('TLabel', font=('Arial', 10))
    style.configure('Treeview', font=('Arial', 10))