# gui/views/analysis_view.py

import logging
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk, scrolledtext
from typing import Callable, Optional

logger = logging.getLogger('ai_code_assistant')


class IAnalysisView(ABC):
    def setup_analysis_panel(self, parent): pass
    def clear_analysis(self): pass
    def add_analysis_result(self, result_type: str, message: str, file: str = "", line: int = 0): pass
    def show_analysis_report(self): pass
    def bind_analyze_code(self, callback: Callable): pass
    def bind_show_analysis_report(self, callback: Callable): pass
    def bind_auto_refactor(self, callback: Callable): pass
    def get_widget(self): pass


class AnalysisView(ttk.Frame, IAnalysisView):
    """Панель результатов анализа кода расположенная внизу как в старом коде."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Панель анализа занимает нижнюю часть
        analysis_frame = ttk.LabelFrame(self, text="Результаты анализа кода")
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Дерево результатов
        tree_frame = ttk.Frame(analysis_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('type', 'file', 'line', 'message')
        self.analysis_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        self.analysis_tree.heading('type', text='Тип')
        self.analysis_tree.heading('file', text='Файл')
        self.analysis_tree.heading('line', text='Строка')
        self.analysis_tree.heading('message', text='Сообщение')
        
        self.analysis_tree.column('type', width=80)
        self.analysis_tree.column('file', width=150)
        self.analysis_tree.column('line', width=50)
        self.analysis_tree.column('message', width=300)
        
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.analysis_tree.yview)
        self.analysis_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.analysis_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления анализом
        button_frame = ttk.Frame(analysis_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.analyze_button = ttk.Button(button_frame, text="🔍 Анализировать")
        self.analyze_button.pack(side=tk.LEFT, padx=2)
        
        self.show_report_button = ttk.Button(button_frame, text="📊 Показать отчет")
        self.show_report_button.pack(side=tk.LEFT, padx=2)
        
        self.refactor_button = ttk.Button(button_frame, text="🛠️ Авторефакторинг")
        self.refactor_button.pack(side=tk.LEFT, padx=2)
        
        logger.debug("AnalysisView инициализирован")

    def setup_analysis_panel(self, parent):
        """Настраивает панель анализа."""
        # Настройка тегов для цветового кодирования
        self.analysis_tree.tag_configure('error', foreground='red')
        self.analysis_tree.tag_configure('warning', foreground='orange')
        self.analysis_tree.tag_configure('info', foreground='blue')
        self.analysis_tree.tag_configure('success', foreground='green')

    def clear_analysis(self):
        """Очищает результаты анализа."""
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)

    def add_analysis_result(self, result_type: str, message: str, file: str = "", line: int = 0):
        """Добавляет результат анализа."""
        item_id = self.analysis_tree.insert(
            '', 'end',
            values=(result_type, file, line, message)
        )
        
        # Цвет в зависимости от типа
        tags = (result_type,)
        self.analysis_tree.item(item_id, tags=tags)

    def show_analysis_report(self):
        """Показывает полный отчет анализа."""
        # Создаем окно с полным отчетом
        report_window = tk.Toplevel(self)
        report_window.title("Полный отчет анализа")
        report_window.geometry("800x600")
        
        report_text = scrolledtext.ScrolledText(report_window, wrap=tk.WORD)
        report_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Собираем все результаты
        report = "ОТЧЕТ АНАЛИЗА КОДА\n"
        report += "=" * 50 + "\n\n"
        
        for item in self.analysis_tree.get_children():
            values = self.analysis_tree.item(item, 'values')
            report += f"{values[0]}: {values[1]}:{values[2]} - {values[3]}\n"
        
        report_text.insert('1.0', report)
        report_text.config(state='disabled')
        
        close_button = ttk.Button(report_window, text="Закрыть", command=report_window.destroy)
        close_button.pack(pady=5)

    def bind_analyze_code(self, callback: Callable):
        """Привязывает обработчик к кнопке 'Анализировать'."""
        self.analyze_button.config(command=callback)

    def bind_show_analysis_report(self, callback: Callable):
        """Привязывает обработчик к кнопке 'Показать отчет'."""
        self.show_report_button.config(command=callback)

    def bind_auto_refactor(self, callback: Callable):
        """Привязывает обработчик к кнопке 'Авторефакторинг'."""
        self.refactor_button.config(command=callback)

    def get_widget(self):
        """Возвращает сам виджет для размещения."""
        return self