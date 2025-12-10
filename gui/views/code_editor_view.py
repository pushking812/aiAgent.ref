# gui/views/code_editor_view.py

import logging
import time
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk
from typing import Callable, Optional

from gui.utils.ui_factory import ui_factory, Tooltip

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
    def setup_auto_save_checkbox(self, var: tk.BooleanVar): pass
    def is_modified(self) -> bool: pass
    def get_source_text_widget(self): pass
    def get_ai_text_widget(self): pass


class CodeEditorView(ttk.Frame, ICodeEditorView):
    """Реализация редактора с использованием фабрики UI."""
    
    def __init__(self, parent):
        super().__init__(parent)
        if parent:
            self.pack(fill=tk.BOTH, expand=True)
        
        # Инициализация переменных
        self._last_content = ""
        self._last_modified_time = 0
        self._on_text_modified_callback: Optional[Callable] = None
        self._on_focus_out_callback: Optional[Callable] = None
        self._is_modified = False
        self._auto_save_var = None
        
        # Создаем виджеты только если родитель указан
        if parent:
            self._create_widgets()
        
        logger.debug("CodeEditorView инициализирован")
    
    def _create_widgets(self):
        """Создает все виджеты редактора."""
        # Редактор исходного кода (верхняя часть)
        source_container = ui_factory.create_frame(self)
        source_container.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Заголовок исходного кода
        source_header = ui_factory.create_frame(source_container)
        source_header.pack(fill=tk.X)
        
        source_label = ui_factory.create_label(
            source_header,
            text="Исходный код",
            bold=True
        )
        source_label.pack(side=tk.LEFT)
        
        # Статус изменений
        self.modified_label = tk.Label(
            source_header,
            text="",
            foreground="red",
            font=('Arial', 9)
        )
        self.modified_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Фрейм для галочки автосохранения
        self.auto_save_frame = ui_factory.create_frame(source_header)
        self.auto_save_frame.pack(side=tk.RIGHT)
        
        # Редактор исходного кода
        source_frame = ui_factory.create_frame(source_container)
        source_frame.pack(fill=tk.BOTH, expand=True)
        
        self.source_text = ui_factory.create_scrolled_text(source_frame, wrap=tk.NONE)
        self.source_text.pack(fill=tk.BOTH, expand=True)
        
        # Редактор AI-кода (нижняя часть)
        ai_container = ui_factory.create_frame(self)
        ai_container.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок AI-кода
        ai_header = ui_factory.create_frame(ai_container)
        ai_header.pack(fill=tk.X)
        
        ai_label = ui_factory.create_label(
            ai_header,
            text="AI-код / Сценарий",
            bold=True
        )
        ai_label.pack(side=tk.LEFT)
        
        # Редактор AI кода
        ai_frame = ui_factory.create_frame(ai_container)
        ai_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ai_text = ui_factory.create_scrolled_text(ai_frame, wrap=tk.NONE, height=6)
        self.ai_text.pack(fill=tk.BOTH, expand=True)

    def setup_auto_save_checkbox(self, var: tk.BooleanVar):
        """Настраивает галочку автосохранения с использованием фабрики."""
        self._auto_save_var = var
        
        # Создаем фрейм для галочки
        auto_save_frame = ui_factory.create_frame(self)
        auto_save_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.auto_save_check = ui_factory.create_checkbutton(
            auto_save_frame,
            text="Автосохранение при переключении",
            variable=var,
            tooltip="Автоматически сохранять изменения при переключении между файлами"
        )
        self.auto_save_check.pack(side=tk.LEFT)
        
        # Привязываем обработку потери фокуса
        if self.source_text:
            self.source_text.bind('<FocusOut>', self._on_editor_focus_out)
        
        logger.debug("Галочка автосохранения настроена")

    def _on_auto_save_blur_changed(self):
        """Обработчик изменения галочки автосохранения."""
        if self._auto_save_var:
            new_value = self._auto_save_var.get()
            logger.info("Автосохранение при переключении: %s", 
                       "включено" if new_value else "выключено")

    def _on_editor_focus_out(self, event):
        """Обработчик потери фокуса редактором."""
        try:
            auto_save_enabled = self._auto_save_var.get() if self._auto_save_var else False
            logger.debug("Потеря фокуса редактором: auto_save=%s, is_modified=%s", 
                        auto_save_enabled, self._is_modified)
            
            if auto_save_enabled and self._is_modified and self._on_focus_out_callback:
                logger.info("Автосохранение при потере фокуса")
                self._on_focus_out_callback(event)
                
        except Exception as e:
            logger.error("Ошибка в обработчике потери фокуса: %s", e)

    def set_on_text_modified_callback(self, callback: Callable):
        """Устанавливает callback для обработки изменений текста."""
        self._on_text_modified_callback = callback
        logger.debug("Callback для изменений текста установлен")

    def bind_focus_out(self, callback: Callable):
        """Привязывает обработчик потери фокуса."""
        if self.source_text:
            self.source_text.bind('<FocusOut>', callback)
            self._on_focus_out_callback = callback
            logger.debug("Обработчик потери фокуса привязан")

    def bind_on_text_modified(self, callback):
        """Привязать обработчик к изменению исходного кода."""
        if self.source_text:
            self.source_text.bind("<KeyRelease>", self._on_text_modified)
        self._on_text_modified_callback = callback

    def _on_text_modified(self, event=None):
        """Обработчик изменения текста в редакторе."""
        try:
            if event and event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R',
                                          'Alt_L', 'Alt_R', 'Caps_Lock', 'Num_Lock']:
                return

            current_time = time.time()
            if current_time - self._last_modified_time < 0.5:
                return
            self._last_modified_time = current_time

            current_content = self.get_source_content()
            
            if self._last_content == current_content:
                logger.debug("Текст не изменился")
                return

            logger.info("Текст изменился! Устанавливаем флаг изменений")
            
            self._last_content = current_content
            self._is_modified = True
            self.update_modified_status(True)

            if self._on_text_modified_callback:
                logger.debug("Вызов callback изменения текста")
                self._on_text_modified_callback(event)

        except Exception as e:
            logger.error("Ошибка в обработчике изменения текста: %s", e, exc_info=True)

    def get_source_content(self):
        """Получить контент исходного кода."""
        if not hasattr(self, 'source_text') or not self.source_text:
            return ""
        content = self.source_text.get("1.0", tk.END).rstrip("\n")
        logger.debug("Получено содержимое редактора: %s символов", len(content))
        return content

    def set_source_content(self, text):
        """Устанавливает содержимое редактора исходного кода."""
        logger.debug("Установка содержимого редактора: %s символов", len(text))
        
        if not hasattr(self, 'source_text') or not self.source_text:
            return
            
        if hasattr(self.source_text, 'unbind'):
            self.source_text.unbind('<KeyRelease>')
            
        self.source_text.delete("1.0", tk.END)
        self.source_text.insert("1.0", text)
        
        self._last_content = text
        logger.debug("_last_content обновлен: %s символов", len(text))
        
        if hasattr(self.source_text, 'see'):
            self.source_text.see("1.0")
            
        if hasattr(self.source_text, 'update'):
            self.source_text.update()
        
        self._is_modified = False
        self.update_modified_status(False)
        
        if hasattr(self.source_text, 'bind'):
            self.source_text.bind('<KeyRelease>', self._on_text_modified)
            
        logger.debug("Содержимое установлено успешно")

    def get_ai_content(self):
        """Получить AI-код (сценарий)."""
        if not hasattr(self, 'ai_text') or not self.ai_text:
            return ""
        content = self.ai_text.get("1.0", tk.END).rstrip("\n")
        logger.debug("Получено содержимое AI редактора: %s символов", len(content))
        return content

    def set_ai_content(self, text):
        """Устанавливает AI-код (сценарий)."""
        logger.debug("Установка содержимого AI редактора: %s символов", len(text))
        if hasattr(self, 'ai_text') and self.ai_text:
            self.ai_text.delete("1.0", tk.END)
            self.ai_text.insert("1.0", text)
            if hasattr(self.ai_text, 'see'):
                self.ai_text.see("1.0")
            if hasattr(self.ai_text, 'update'):
                self.ai_text.update()

    def clear_ai_content(self):
        """Очищает поле AI-кода."""
        if hasattr(self, 'ai_text') and self.ai_text:
            self.ai_text.delete("1.0", tk.END)
            logger.debug("AI редактор очищен")

    def set_source_editable(self, editable: bool):
        """Включает/выключает редактирование исходного кода."""
        if hasattr(self, 'source_text') and self.source_text:
            state = tk.NORMAL if editable else tk.DISABLED
            self.source_text.config(state=state)
            logger.debug("Редактирование исходного кода: %s", "включено" if editable else "выключено")

    def update_modified_status(self, modified: bool):
        """Обновляет статус изменений в интерфейсе."""
        self._is_modified = modified
        if hasattr(self, 'modified_label'):
            if modified:
                self.modified_label.config(text="[ИЗМЕНЕНО]")
            else:
                self.modified_label.config(text="")

    def bind_on_ai_modified(self, callback):
        """Привязать обработчик к изменению AI-кода."""
        if hasattr(self, 'ai_text') and self.ai_text:
            self.ai_text.bind("<KeyRelease>", callback)

    def is_modified(self) -> bool:
        """Возвращает статус изменений."""
        return self._is_modified

    def get_source_text_widget(self):
        """Возвращает виджет редактора исходного кода."""
        if hasattr(self, 'source_text'):
            return self.source_text
        return None

    def get_ai_text_widget(self):
        """Возвращает виджет редактора AI-кода."""
        if hasattr(self, 'ai_text'):
            return self.ai_text
        return None
    
    def pack(self, **kwargs):
        """Упаковывает виджет и создает внутренние виджеты."""
        super().pack(**kwargs)
        if not hasattr(self, 'source_text'):
            self._create_widgets()