# gui/utils/ui_components.py

"""
Устаревший модуль ui_components.py - поддерживается для обратной совместимости
Все функции делегируются новой фабрике ui_factory.py
"""

import warnings
from typing import Optional, List, Dict, Any, Callable
import tkinter as tk
from tkinter import ttk

# Импортируем новую фабрику
from .ui_factory import ui_factory, Tooltip as NewTooltip


class Tooltip:
    """
    Устаревший класс Tooltip - делегирует новой реализации
    Оставлен для обратной совместимости
    """
    
    def __init__(self, widget, text: str):
        warnings.warn(
            "Класс Tooltip из ui_components.py устарел. Используйте ui_factory.Tooltip",
            DeprecationWarning,
            stacklevel=2
        )
        # Создаем новый Tooltip
        self._tooltip = NewTooltip(widget, text)
    
    def show_tooltip(self, event=None):
        """Показывает подсказку"""
        return self._tooltip._show_tooltip(event)
    
    def hide_tooltip(self, event=None):
        """Скрывает подсказку"""
        return self._tooltip._hide_tooltip(event)


class UIComponentFactory:
    """
    Устаревший класс UIComponentFactory - делегирует новой фабрике
    Оставлен для обратной совместимости
    """
    
    @staticmethod
    def create_button_frame(parent, title: str, buttons_config: List[Dict[str, Any]]) -> ttk.Frame:
        """
        Создает фрейм с кнопками по конфигурации
        """
        warnings.warn(
            "Метод UIComponentFactory.create_button_frame устарел. Используйте ui_factory.create_button_frame",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Адаптируем конфигурацию к новому формату
        adapted_config = []
        for config in buttons_config:
            adapted = {
                'text': config.get('text', ''),
                'command': config.get('command'),
                'tooltip': config.get('tooltip'),
                'square': config.get('square', False)
            }
            adapted_config.append(adapted)
        
        # Используем новую фабрику
        return ui_factory.create_button_frame(parent, title, adapted_config)
    
    @staticmethod
    def create_scrolled_text(parent, **kwargs) -> tk.Text:
        """
        Создает текстовое поле со скроллбаром
        """
        warnings.warn(
            "Метод UIComponentFactory.create_scrolled_text устарел. Используйте ui_factory.create_scrolled_text",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Используем новую фабрику
        return ui_factory.create_scrolled_text(parent, **kwargs)
    
    @staticmethod
    def create_toolbar(parent, buttons_config: List[Dict[str, Any]], **kwargs) -> ttk.Frame:
        """
        Создает панель инструментов
        """
        warnings.warn(
            "Метод UIComponentFactory.create_toolbar устарел. Используйте ui_factory.create_toolbar",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Адаптируем конфигурацию
        adapted_config = []
        for config in buttons_config:
            adapted = {
                'text': config.get('text', ''),
                'command': config.get('command'),
                'tooltip': config.get('tooltip'),
                'square': config.get('square', False),
                'padx': config.get('padx', 2)
            }
            adapted_config.append(adapted)
        
        # Используем новую фабрику
        return ui_factory.create_toolbar(parent, adapted_config, **kwargs)
    
    @staticmethod
    def create_button(parent, text: str, command=None, tooltip: Optional[str] = None, 
                     square: bool = False, **kwargs) -> ttk.Button:
        """
        Создает кнопку с опциональной подсказкой
        """
        warnings.warn(
            "Метод UIComponentFactory.create_button устарел. Используйте ui_factory.create_button",
            DeprecationWarning,
            stacklevel=2
        )
        
        return ui_factory.create_button(
            parent=parent,
            text=text,
            command=command,
            tooltip=tooltip,
            square=square,
            **kwargs
        )
    
    @staticmethod
    def create_label(parent, text: str, bold: bool = False, small: bool = False,
                    foreground: Optional[str] = None, **kwargs) -> ttk.Label:
        """
        Создает метку с заданным стилем
        """
        warnings.warn(
            "Метод UIComponentFactory.create_label устарел. Используйте ui_factory.create_label",
            DeprecationWarning,
            stacklevel=2
        )
        
        return ui_factory.create_label(
            parent=parent,
            text=text,
            bold=bold,
            small=small,
            foreground=foreground,
            **kwargs
        )
    
    @staticmethod
    def create_entry(parent, textvariable=None, width: Optional[int] = None,
                    tooltip: Optional[str] = None, **kwargs) -> ttk.Entry:
        """
        Создает поле ввода
        """
        warnings.warn(
            "Метод UIComponentFactory.create_entry устарел. Используйте ui_factory.create_entry",
            DeprecationWarning,
            stacklevel=2
        )
        
        return ui_factory.create_entry(
            parent=parent,
            textvariable=textvariable,
            width=width,
            tooltip=tooltip,
            **kwargs
        )
    
    @staticmethod
    def create_frame(parent, padding: Optional[int] = None, **kwargs) -> ttk.Frame:
        """
        Создает фрейм
        """
        warnings.warn(
            "Метод UIComponentFactory.create_frame устарел. Используйте ui_factory.create_frame",
            DeprecationWarning,
            stacklevel=2
        )
        
        return ui_factory.create_frame(parent, padding=padding, **kwargs)
    
    @staticmethod
    def create_label_frame(parent, text: str, padding: Optional[int] = 5, **kwargs) -> ttk.LabelFrame:
        """
        Создает фрейм с заголовком
        """
        warnings.warn(
            "Метод UIComponentFactory.create_label_frame устарел. Используйте ui_factory.create_label_frame",
            DeprecationWarning,
            stacklevel=2
        )
        
        return ui_factory.create_label_frame(parent, text=text, padding=padding, **kwargs)


# Создаем глобальные экземпляры для обратной совместимости
ui_component_factory = UIComponentFactory()


# Функция для миграции со старого API на новый
def migrate_to_ui_factory():
    """
    Помогает мигрировать со старого ui_components.py на новую ui_factory.py
    """
    print("=" * 60)
    print("МИГРАЦИЯ С ui_components.py НА ui_factory.py")
    print("=" * 60)
    print("\nЗамените импорты:")
    print("  FROM: from gui.utils.ui_components import Tooltip, UIComponentFactory")
    print("  TO:   from gui.utils.ui_factory import Tooltip, ui_factory")
    print("\nЗамените использование:")
    print("  Старое: UIComponentFactory.create_button(parent, 'text', ...)")
    print("  Новое:  ui_factory.create_button(parent, 'text', ...)")
    print("\nЗамените создание подсказок:")
    print("  Старое: Tooltip(button, 'текст подсказки')")
    print("  Новое:  Tooltip(button, 'текст подсказки')")
    print("\nПодробности в документации: gui/utils/ui_factory.py")
    print("=" * 60)


# Автоматически показываем предупреждение при импорте
warnings.warn(
    "Модуль ui_components.py устарел. Используйте ui_factory.py\n"
    "Запустите migrate_to_ui_factory() для получения инструкций по миграции.",
    DeprecationWarning,
    stacklevel=2
)


if __name__ == "__main__":
    # При запуске модуля напрямую показываем инструкцию по миграции
    migrate_to_ui_factory()