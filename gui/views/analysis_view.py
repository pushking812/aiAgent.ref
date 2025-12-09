# gui/views/analysis_view.py

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Callable, Optional
import logging

from gui.utils.ui_factory import ui_factory

logger = logging.getLogger('ai_code_assistant')


class IAnalysisView(ABC):
    def setup_analysis_panel(self, parent): pass
    def add_analysis_result(self, result_type: str, message: str, file: str = "", line: int = 0): pass
    def clear_analysis(self): pass
    def show_analysis_report(self): pass
    def bind_analyze_code(self, callback: Callable): pass
    def bind_show_analysis_report(self, callback: Callable): pass
    def bind_auto_refactor(self, callback: Callable): pass


class AnalysisView(ttk.Frame, IAnalysisView):
    """Представление анализа кода с использованием фабрики UI."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        
        self._on_analyze_callback: Optional[Callable] = None
        self._on_report_callback: Optional[Callable] = None
        self._on_refactor_callback: Optional[Callable] = None
        
        logger.debug("AnalysisView инициализирован")
    
    def setup_analysis_panel(self, parent):
        """Настраивает панель анализа с использованием фабрики."""
        # Основной фрейм анализа
        analysis_frame = ui_factory.create_label_frame(parent, text="Анализ кода", padding=5)
        analysis_frame.pack(fill=tk.BOTH, expand=True)
        
        # Панель инструментов анализа
        toolbar_frame = ui_factory.create_frame(analysis_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.analyze_button = ui_factory.create_button(
            toolbar_frame,
            text="🔍 Анализировать",
            tooltip="Запустить анализ кода проекта"
        )
        self.analyze_button.pack(side=tk.LEFT, padx=2)
        
        self.report_button = ui_factory.create_button(
            toolbar_frame,
            text="📊 Отчет",
            tooltip="Показать подробный отчет анализа"
        )
        self.report_button.pack(side=tk.LEFT, padx=2)
        
        self.refactor_button = ui_factory.create_button(
            toolbar_frame,
            text="🛠️ Рефакторинг",
            tooltip="Автоматический рефакторинг кода"
        )
        self.refactor_button.pack(side=tk.LEFT, padx=2)
        
        # Область вывода результатов
        results_frame = ui_factory.create_frame(analysis_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview для результатов анализа
        columns = ('type', 'message', 'file', 'line')
        self.results_tree = ui_factory.create_treeview(
            results_frame,
            columns=columns,
            show='headings'
        )
        
        # Настраиваем колонки
        self.results_tree.heading('type', text='Тип')
        self.results_tree.heading('message', text='Сообщение')
        self.results_tree.heading('file', text='Файл')
        self.results_tree.heading('line', text='Строка')
        
        self.results_tree.column('type', width=80)
        self.results_tree.column('message', width=300)
        self.results_tree.column('file', width=150)
        self.results_tree.column('line', width=60)
        
        # Настраиваем теги для разных типов результатов
        self.results_tree.tag_configure('info', foreground='blue')
        self.results_tree.tag_configure('warning', foreground='orange')
        self.results_tree.tag_configure('error', foreground='red')
        self.results_tree.tag_configure('success', foreground='green')
        
        # Полоса прокрутки
        scrollbar = ui_factory.create_scrollbar(
            results_frame,
            orient="vertical",
            command=self.results_tree.yview
        )
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        logger.debug("Панель анализа настроена")
    
    def add_analysis_result(self, result_type: str, message: str, file: str = "", line: int = 0):
        """Добавляет результат анализа в дерево."""
        # Определяем иконку по типу
        icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅'
        }
        
        icon = icons.get(result_type, '❓')
        display_type = f"{icon} {result_type}"
        
        # Вставляем строку
        item_id = self.results_tree.insert(
            '',
            'end',
            values=(display_type, message, file, line),
            tags=(result_type,)
        )
        
        # Автопрокрутка к новому элементу
        self.results_tree.see(item_id)
        
        logger.debug(f"Добавлен результат анализа: {result_type} - {message}")
    
    def clear_analysis(self):
        """Очищает все результаты анализа."""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        logger.debug("Результаты анализа очищены")
    
    def show_analysis_report(self):
        """Показывает отчет анализа."""
        # Собираем статистику
        items = self.results_tree.get_children()
        if not items:
            logger.debug("Нет данных для отчета")
            return
        
        # Подсчитываем типы
        counts = {'info': 0, 'warning': 0, 'error': 0, 'success': 0}
        for item in items:
            tags = self.results_tree.item(item, 'tags')
            if tags:
                counts[tags[0]] += 1
        
        # Создаем отчет
        report = f"Отчет анализа кода:\n"
        report += f"Всего проблем: {len(items)}\n"
        report += f"Информационных: {counts['info']}\n"
        report += f"Предупреждений: {counts['warning']}\n"
        report += f"Ошибок: {counts['error']}\n"
        report += f"Успешных: {counts['success']}\n"
        
        logger.info(f"Показан отчет анализа: {len(items)} проблем")
        
        # Показываем в диалоге
        import tkinter.messagebox as messagebox
        messagebox.showinfo("Отчет анализа", report)
    
    def bind_analyze_code(self, callback: Callable):
        """Привязывает обработчик анализа кода."""
        self._on_analyze_callback = callback
        self.analyze_button.config(command=callback)
        logger.debug("Обработчик анализа кода привязан")
    
    def bind_show_analysis_report(self, callback: Callable):
        """Привязывает обработчик показа отчета."""
        self._on_report_callback = callback
        self.report_button.config(command=callback)
        logger.debug("Обработчик отчета привязан")
    
    def bind_auto_refactor(self, callback: Callable):
        """Привязывает обработчик рефакторинга."""
        self._on_refactor_callback = callback
        self.refactor_button.config(command=callback)
        logger.debug("Обработчик рефакторинга привязан")