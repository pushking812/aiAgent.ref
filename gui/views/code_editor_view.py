# gui/views/code_editor_view.py

from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, scrolledtext

class ICodeEditorView(ABC):
    def get_source_content(self): pass
    def set_source_content(self, text): pass
    def bind_on_text_modified(self, callback): pass
    def get_ai_content(self): pass
    def set_ai_content(self, text): pass
    def clear_ai_content(self): pass
    def bind_on_ai_modified(self, callback): pass

class CodeEditorView(ttk.Frame, ICodeEditorView):
    """
    Реализация редактора исходного и AI-кода.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        # --- Редактор исходного кода ---
        source_label = ttk.Label(self, text="Исходный код")
        source_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
        self.source_text = scrolledtext.ScrolledText(self, wrap=tk.NONE)
        self.source_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # --- Редактор AI-кода ---
        ai_label = ttk.Label(self, text="AI-код / Сценарий")
        ai_label.pack(anchor=tk.W, padx=5)
        self.ai_text = scrolledtext.ScrolledText(self, wrap=tk.NONE, height=6)
        self.ai_text.pack(fill=tk.X, padx=5, pady=(0, 5))

    def get_source_content(self):
        """Получить контент исходного кода"""
        return self.source_text.get("1.0", tk.END).rstrip("\n")

    def set_source_content(self, text):
        """Установить контент исходного кода"""
        self.source_text.delete("1.0", tk.END)
        self.source_text.insert("1.0", text)

    def bind_on_text_modified(self, callback):
        """Привязать обработчик к изменению исходного кода."""
        self.source_text.bind("<KeyRelease>", callback)
        # Можно добавить доп. проверку изменения через <<Modified>> event

    def get_ai_content(self):
        """Получить AI-код (сценарий)"""
        return self.ai_text.get("1.0", tk.END).rstrip("\n")

    def set_ai_content(self, text):
        """Установить AI-код (сценарий)"""
        self.ai_text.delete("1.0", tk.END)
        self.ai_text.insert("1.0", text)

    def clear_ai_content(self):
        """Очистить поле AI-кода"""
        self.ai_text.delete("1.0", tk.END)

    def bind_on_ai_modified(self, callback):
        """Привязать обработчик к изменению AI-кода."""
        self.ai_text.bind("<KeyRelease>", callback)