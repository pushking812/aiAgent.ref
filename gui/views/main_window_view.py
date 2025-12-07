# gui/views/main_window_view.py

from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

class IMainWindowView(ABC):
    def set_status(self, text: str): pass
    def show_info(self, title: str, msg: str): pass
    def show_error(self, title: str, msg: str): pass
    def show_warning(self, title: str, msg: str): pass
    def bind_create_project(self, callback): pass
    def bind_open_project(self, callback): pass
    def bind_create_structure(self, callback): pass
    def bind_refresh_project(self, callback): pass
    def bind_save_project(self, callback): pass
    def bind_show_pending_changes(self, callback): pass
    def bind_close_project(self, callback): pass
    def bind_analyze_code(self, callback): pass
    def bind_show_analysis_report(self, callback): pass
    def bind_auto_refactor(self, callback): pass
    def bind_save_current_file(self, callback): pass
    def bind_delete_selected_element(self, callback): pass
    def bind_add_ai_code(self, callback): pass
    def bind_replace_selected_element(self, callback): pass
    def bind_clear_ai_code(self, callback): pass
    def set_unsaved_changes_status(self, text: str): pass
    def set_auto_save_var(self, var: tk.BooleanVar): pass
    def get_auto_save_var(self) -> tk.BooleanVar: pass
    def get_content_panel(self) -> ttk.Frame: pass

class MainWindowView(ttk.Frame, IMainWindowView):
    def __init__(self, root):
        super().__init__(root)
        self.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  # Внешние отступы как в старом коде
        
        # Создаем главный контейнер (как в старом коде self.main_container)
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель управления (точная копия старого кода)
        top_panel = ttk.Frame(self.main_container)
        top_panel.pack(fill=tk.X, pady=(0, 5))  # Точные отступы как в старом коде
        
        # Кнопки проекта с иконками как в старом коде
        project_buttons = [
            {'text': '🆕', 'tooltip': 'Создать новый проект', 'square': True},
            {'text': '📁', 'tooltip': 'Открыть проект', 'square': True},
            {'text': '📐', 'tooltip': 'Создать структуру из AI', 'square': True},
            {'text': '🔄', 'tooltip': 'Обновить проект', 'square': True},
            {'text': '💾', 'tooltip': 'Сохранить все файлы', 'square': True},
            {'text': '📋', 'tooltip': 'Показать отложенные изменения', 'square': True},
            {'text': '❌', 'tooltip': 'Закрыть проект', 'square': True},
        ]
        
        # Фрейм для кнопок проекта с подписью
        project_label = ttk.Label(top_panel, text="Проект:")
        project_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.create_project_button = self._create_button(top_panel, '🆕', padx=2)
        self.open_project_button = self._create_button(top_panel, '📁', padx=2)
        self.create_structure_button = self._create_button(top_panel, '📐', padx=2)
        self.refresh_project_button = self._create_button(top_panel, '🔄', padx=2)
        self.save_project_button = self._create_button(top_panel, '💾', padx=2)
        self.show_pending_changes_button = self._create_button(top_panel, '📋', padx=2)
        self.close_project_button = self._create_button(top_panel, '❌', padx=2)
        
        # Разделитель
        ttk.Separator(top_panel, orient='vertical').pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        # Кнопки анализа кода
        analysis_label = ttk.Label(top_panel, text="Анализ кода:")
        analysis_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.analyze_code_button = self._create_button(top_panel, '🔍', padx=2)
        self.show_analysis_report_button = self._create_button(top_panel, '📊', padx=2)
        self.auto_refactor_button = self._create_button(top_panel, '🛠️', padx=2)
        
        # Разделитель
        ttk.Separator(top_panel, orient='vertical').pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        # Кнопки редактора кода
        editor_label = ttk.Label(top_panel, text="Редактор:")
        editor_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_current_file_button = self._create_button(top_panel, '💾', padx=2)
        self.delete_selected_element_button = self._create_button(top_panel, '🗑️', padx=2)
        
        # Разделитель
        ttk.Separator(top_panel, orient='vertical').pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        # Кнопки AI кода
        ai_label = ttk.Label(top_panel, text="AI Код:")
        ai_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.add_ai_code_button = self._create_button(top_panel, '➕', padx=2)
        self.replace_selected_element_button = self._create_button(top_panel, '🔄', padx=2)
        self.clear_ai_code_button = self._create_button(top_panel, '🧹', padx=2)
        
        # Правая часть - статус проекта и индикатор изменений
        status_frame = ttk.Frame(top_panel)
        status_frame.pack(side=tk.RIGHT, padx=10)
        
        self.status_label = ttk.Label(status_frame, text="Проект не открыт")
        self.status_label.pack(side=tk.LEFT)
        
        # Индикатор несохраненных изменений
        self.unsaved_changes_label = ttk.Label(
            status_frame, 
            text="", 
            foreground="red",
            font=('Arial', 9, 'bold')
        )
        self.unsaved_changes_label.pack(side=tk.LEFT, padx=(10, 0))

        # Основная панель контента (для размещения других компонентов)
        self.content_panel = ttk.Frame(self.main_container)
        self.content_panel.pack(fill=tk.BOTH, expand=True)
        
        # Галочка автосохранения будет добавлена в CodeEditorView как в старом коде

    def _create_button(self, parent, text, padx=0):
        """Создает кнопку квадратной формы как в старом коде."""
        btn = ttk.Button(parent, text=text, width=3)
        btn.pack(side=tk.LEFT, padx=padx)
        return btn

    def set_status(self, text: str):
        """Установить строку статуса приложения."""
        self.status_label.config(text=text)

    def set_unsaved_changes_status(self, text: str):
        """Установить статус несохраненных изменений."""
        self.unsaved_changes_label.config(text=text)

    def set_auto_save_var(self, var: tk.BooleanVar):
        """Установить переменную автосохранения."""
        # Реализуется в CodeEditorView
        pass

    def get_auto_save_var(self) -> tk.BooleanVar:
        """Получить переменную автосохранения."""
        # Реализуется в CodeEditorView
        return tk.BooleanVar(value=False)

    def show_info(self, title: str, msg: str):
        """Показать информационное сообщение."""
        messagebox.showinfo(title, msg)

    def show_error(self, title: str, msg: str):
        """Показать сообщение об ошибке."""
        messagebox.showerror(title, msg)

    def show_warning(self, title: str, msg: str):
        """Показать предупреждение."""
        messagebox.showwarning(title, msg)

    def get_content_panel(self) -> ttk.Frame:
        """Получить панель контента для размещения других компонентов."""
        return self.content_panel

    def bind_create_project(self, callback):
        """Привязать обработчик к кнопке 'Создать проект'."""
        self.create_project_button.config(command=callback)

    def bind_open_project(self, callback):
        """Привязать обработчик к кнопке 'Открыть проект'."""
        self.open_project_button.config(command=callback)

    def bind_create_structure(self, callback):
        """Привязать обработчик к кнопке 'Структура из AI'."""
        self.create_structure_button.config(command=callback)

    def bind_refresh_project(self, callback):
        """Привязать обработчик к кнопке 'Обновить проект'."""
        self.refresh_project_button.config(command=callback)

    def bind_save_project(self, callback):
        """Привязать обработчик к кнопке 'Сохранить проект'."""
        self.save_project_button.config(command=callback)

    def bind_show_pending_changes(self, callback):
        """Привязать обработчик к кнопке 'Отложенные изменения'."""
        self.show_pending_changes_button.config(command=callback)

    def bind_close_project(self, callback):
        """Привязать обработчик к кнопке 'Закрыть проект'."""
        self.close_project_button.config(command=callback)

    def bind_analyze_code(self, callback):
        """Привязать обработчик к кнопке 'Анализ'."""
        self.analyze_code_button.config(command=callback)

    def bind_show_analysis_report(self, callback):
        """Привязать обработчик к кнопке 'Отчет анализа'."""
        self.show_analysis_report_button.config(command=callback)

    def bind_auto_refactor(self, callback):
        """Привязать обработчик к кнопке 'Рефакторинг'."""
        self.auto_refactor_button.config(command=callback)

    def bind_save_current_file(self, callback):
        """Привязать обработчик к кнопке 'Сохранить файл'."""
        self.save_current_file_button.config(command=callback)

    def bind_delete_selected_element(self, callback):
        """Привязать обработчик к кнопке 'Удалить элемент'."""
        self.delete_selected_element_button.config(command=callback)

    def bind_add_ai_code(self, callback):
        """Привязать обработчик к кнопке 'Добавить AI код'."""
        self.add_ai_code_button.config(command=callback)

    def bind_replace_selected_element(self, callback):
        """Привязать обработчик к кнопке 'Заменить элемент'."""
        self.replace_selected_element_button.config(command=callback)

    def bind_clear_ai_code(self, callback):
        """Привязать обработчик к кнопке 'Очистить AI код'."""
        self.clear_ai_code_button.config(command=callback)