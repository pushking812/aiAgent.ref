# gui/views/code_editor_view.py

import logging
import time
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import scrolledtext, ttk
from typing import Callable, Optional

logger = logging.getLogger('ai_code_assistant')


class ICodeEditorView(ABC):
    def get_source_content(self): pass
    def set_source_content(self, text): pass
    def bind_on_text_modified(self, callback): pass
    def get_ai_content(self): pass
    def set_ai_content(self, text): pass
    def clear_ai_content(self): pass
    def bind_on_ai_modified(self, callback): pass
    def set_on_text_modified_callback(self, callback: Callable): pass
    def set_source_editable(self, editable: bool): pass
    def update_modified_status(self, modified: bool): pass
    def bind_focus_out(self, callback: Callable): pass


class CodeEditorView(ttk.Frame, ICodeEditorView):
    """
    Расширенная реализация редактора с отслеживанием изменений и автосохранением.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        # Инициализация переменных для отслеживания изменений
        self._last_content = ""
        self._last_modified_time = 0
        self._on_text_modified_callback: Optional[Callable] = None
        self._on_focus_out_callback: Optional[Callable] = None
        self._is_modified = False

        # --- Редактор исходного кода ---
        source_container = ttk.Frame(self)
        source_container.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Заголовок и кнопки
        source_header = ttk.Frame(source_container)
        source_header.pack(fill=tk.X)

        ttk.Label(source_header, text="Исходный код", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        # Статус изменений
        self.modified_label = ttk.Label(
            source_header,
            text="",
            foreground="red",
            font=('Arial', 9)
        )
        self.modified_label.pack(side=tk.LEFT, padx=(10, 0))

        # Кнопки для исходного кода
        source_buttons_frame = ttk.Frame(source_header)
        source_buttons_frame.pack(side=tk.RIGHT)

        # Редактор исходного кода
        source_frame = ttk.Frame(source_container)
        source_frame.pack(fill=tk.BOTH, expand=True)

        self.source_text = scrolledtext.ScrolledText(source_frame, wrap=tk.NONE)
        self.source_text.pack(fill=tk.BOTH, expand=True)
        self._configure_text_widget(self.source_text)

        # --- Редактор AI-кода ---
        ai_container = ttk.Frame(self)
        ai_container.pack(fill=tk.BOTH, expand=True)

        # Заголовок и кнопки
        ai_header = ttk.Frame(ai_container)
        ai_header.pack(fill=tk.X)

        ttk.Label(ai_header, text="AI-код / Сценарий", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        # Кнопки для AI кода
        ai_buttons_frame = ttk.Frame(ai_header)
        ai_buttons_frame.pack(side=tk.RIGHT)

        # Редактор AI кода
        ai_frame = ttk.Frame(ai_container)
        ai_frame.pack(fill=tk.BOTH, expand=True)

        self.ai_text = scrolledtext.ScrolledText(ai_frame, wrap=tk.NONE, height=6)
        self.ai_text.pack(fill=tk.BOTH, expand=True)
        self._configure_text_widget(self.ai_text)

        logger.debug("CodeEditorView инициализирован")

    def _configure_text_widget(self, text_widget: scrolledtext.ScrolledText):
        """Настраивает текстовый виджет (табуляция)"""
        try:
            import tkinter.font as font
            current_font = text_widget.cget('font')
            font_obj = font.Font(font=current_font)
            tab_width = font_obj.measure(' ' * 4)
            text_widget.configure(tabs=(tab_width,))
        except Exception as e:
            logger.warning("Не удалось настроить Tab: %s", e)
            text_widget.configure(tabs=32)

    def set_on_text_modified_callback(self, callback: Callable):
        """Устанавливает callback для обработки изменений текста"""
        self._on_text_modified_callback = callback
        logger.debug("Callback для изменений текста установлен")

    def bind_focus_out(self, callback: Callable):
        """Привязывает обработчик потери фокуса"""
        if self.source_text:
            self.source_text.bind('<FocusOut>', callback)
            self._on_focus_out_callback = callback
            logger.debug("Обработчик потери фокуса привязан")

    def bind_on_text_modified(self, callback):
        """Привязать обработчик к изменению исходного кода."""
        self.source_text.bind("<KeyRelease>", self._on_text_modified)
        self._on_text_modified_callback = callback

    def _on_text_modified(self, event=None):
        """Обработчик изменения текста в редакторе"""
        try:
            # Пропускаем служебные клавиши
            if event and event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R',
                                          'Alt_L', 'Alt_R', 'Caps_Lock', 'Num_Lock']:
                return

            current_time = time.time()
            # Защита от слишком частых срабатываний
            if current_time - self._last_modified_time < 0.5:  # 500 мс задержка
                return
            self._last_modified_time = current_time

            # Получаем текущее содержимое
            current_content = self.get_source_content()

            # Проверяем, изменился ли текст на самом деле
            if self._last_content == current_content:
                logger.debug("Текст не изменился")
                return

            logger.info("Текст изменился! Устанавливаем флаг изменений")

            # Сохраняем текущее содержимое для следующей проверки
            self._last_content = current_content
            self._is_modified = True
            self.update_modified_status(True)

            # Вызываем callback если есть
            if self._on_text_modified_callback:
                logger.debug("Вызов callback изменения текста")
                self._on_text_modified_callback(event)

        except Exception as e:
            logger.error("? Ошибка в обработчике изменения текста: %s", e, exc_info=True)

    def get_source_content(self):
        """Получить контент исходного кода"""
        content = self.source_text.get("1.0", tk.END).rstrip("\n")
        logger.debug("Получено содержимое редактора: %s символов", len(content))
        return content

    def set_source_content(self, text):
        """Устанавливает содержимое редактора исходного кода"""
        logger.debug("Установка содержимого редактора: %s символов", len(text))

        # Временно отключаем отслеживание изменений
        self.source_text.unbind('<KeyRelease>')

        # Очищаем редактор
        self.source_text.delete("1.0", tk.END)

        # Вставляем новое содержимое
        self.source_text.insert("1.0", text)

        # Инициализируем последнее содержимое
        self._last_content = text
        logger.debug("_last_content обновлен: %s символов", len(text))

        # Прокручиваем к началу
        self.source_text.see("1.0")

        # Обновляем интерфейс
        self.source_text.update()

        # Сбрасываем флаг изменений
        self._is_modified = False
        self.update_modified_status(False)

        # Включаем обратно отслеживание изменений
        self.source_text.bind('<KeyRelease>', self._on_text_modified)

        logger.debug("Содержимое установлено успешно")

    def get_ai_content(self):
        """Получить AI-код (сценарий)"""
        content = self.ai_text.get("1.0", tk.END).rstrip("\n")
        logger.debug("Получено содержимое AI редактора: %s символов", len(content))
        return content

    def set_ai_content(self, text):
        """Устанавливает AI-код (сценарий)"""
        logger.debug("Установка содержимого AI редактора: %s символов", len(text))
        self.ai_text.delete("1.0", tk.END)
        self.ai_text.insert("1.0", text)
        self.ai_text.see("1.0")
        self.ai_text.update()

    def clear_ai_content(self):
        """Очищает поле AI-кода"""
        self.ai_text.delete("1.0", tk.END)
        logger.debug("AI редактор очищен")

    def set_source_editable(self, editable: bool):
        """Включает/выключает редактирование исходного кода"""
        state = tk.NORMAL if editable else tk.DISABLED
        self.source_text.config(state=state)
        logger.debug("Редактирование исходного кода: %s", "включено" if editable else "выключено")

    def update_modified_status(self, modified: bool):
        """Обновляет статус изменений в интерфейсе"""
        self._is_modified = modified
        if modified:
            self.modified_label.config(text="[ИЗМЕНЕНО]")
        else:
            self.modified_label.config(text="")

    def bind_on_ai_modified(self, callback):
        """Привязать обработчик к изменению AI-кода."""
        self.ai_text.bind("<KeyRelease>", callback)

    def is_modified(self) -> bool:
        """Возвращает статус изменений"""
        return self._is_modified
