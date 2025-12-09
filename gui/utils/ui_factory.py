"""
gui/utils/ui_factory.py

Фабрика UI компонентов с поддержкой Tooltip и централизованной конфигурацией
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, List, Dict, Any, Callable, Union
import logging

logger = logging.getLogger('ai_code_assistant')


class Tooltip:
    """Всплывающая подсказка для виджетов с улучшенной реализацией"""
    
    def __init__(self, widget: tk.Widget, text: str, delay: int = 500):
        """
        Инициализация подсказки
        
        Args:
            widget: Виджет, к которому привязывается подсказка
            text: Текст подсказки
            delay: Задержка перед показом (мс)
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window: Optional[tk.Toplevel] = None
        self.scheduled_id: Optional[str] = None
        
        # Привязка событий
        self.widget.bind("<Enter>", self._schedule_tooltip)
        self.widget.bind("<Leave>", self._hide_tooltip)
        self.widget.bind("<ButtonPress>", self._hide_tooltip)
    
    def _schedule_tooltip(self, event=None):
        """Запланировать показ подсказки"""
        if self.scheduled_id:
            self.widget.after_cancel(self.scheduled_id)
        self.scheduled_id = self.widget.after(self.delay, self._show_tooltip)
    
    def _show_tooltip(self):
        """Показать подсказку"""
        if self.tooltip_window:
            return
        
        # Определяем позицию
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        
        # Создаем окно подсказки
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Устанавливаем стиль подсказки
        self.tooltip_window.configure(background="#ffffe0", relief="solid", borderwidth=1)
        
        # Создаем метку с текстом
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9),
            padx=5,
            pady=2
        )
        label.pack()
        
        # Делаем окно поверх других
        self.tooltip_window.attributes("-topmost", True)
    
    def _hide_tooltip(self, event=None):
        """Скрыть подсказку"""
        if self.scheduled_id:
            self.widget.after_cancel(self.scheduled_id)
            self.scheduled_id = None
        
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def update_text(self, new_text: str):
        """Обновить текст подсказки"""
        self.text = new_text
        if self.tooltip_window:
            self._hide_tooltip()
            self._show_tooltip()


class UIFactory:
    """
    Фабрика для создания переиспользуемых UI компонентов
    с централизованной конфигурацией и стилями
    """
    
    # Конфигурация стилей
    STYLES = {
        'tooltip': {
            'background': '#ffffe0',
            'relief': 'solid',
            'borderwidth': 1,
            'font': ('Arial', 9)
        },
        'button_square': {
            'width': 3
        },
        'button_regular': {
            'width': None
        },
        'label_regular': {
            'font': ('Arial', 10)
        },
        'label_bold': {
            'font': ('Arial', 10, 'bold')
        },
        'label_small': {
            'font': ('Arial', 8)
        },
        'entry_regular': {
            'font': ('Courier', 10)
        },
        'text_editor': {
            'font': ('Courier', 10),
            'tabs': 32
        },
        'treeview': {
            'font': ('Arial', 9)
        }
    }
    
    @staticmethod
    def create_button(parent: tk.Widget, 
                     text: str, 
                     command: Optional[Callable] = None,
                     tooltip: Optional[str] = None,
                     square: bool = False,
                     width: Optional[int] = None,
                     **kwargs) -> ttk.Button:
        """
        Создает кнопку с опциональной подсказкой
        
        Args:
            parent: Родительский виджет
            text: Текст кнопки
            command: Функция-обработчик
            tooltip: Текст всплывающей подсказки
            square: Квадратная форма кнопки
            width: Ширина кнопки
            **kwargs: Дополнительные параметры
            
        Returns:
            ttk.Button: Созданная кнопка
        """
        # Определяем ширину
        if square:
            width = 3
        elif width is None:
            width = UIFactory.STYLES['button_regular']['width']
        
        # Создаем кнопку
        btn = ttk.Button(parent, text=text, command=command, width=width, **kwargs)
        
        # Добавляем подсказку если указана
        if tooltip:
            Tooltip(btn, tooltip)
        
        logger.debug(f"Создана кнопка: text={text}, square={square}, tooltip={bool(tooltip)}")
        return btn
    
    @staticmethod
    def create_label(parent: tk.Widget,
                    text: str,
                    bold: bool = False,
                    small: bool = False,
                    foreground: Optional[str] = None,
                    **kwargs) -> ttk.Label:
        """
        Создает метку с заданным стилем
        
        Args:
            parent: Родительский виджет
            text: Текст метки
            bold: Жирный шрифт
            small: Мелкий шрифт
            foreground: Цвет текста
            **kwargs: Дополнительные параметры
            
        Returns:
            ttk.Label: Созданная метка
        """
        # Определяем стиль
        style_config = {}
        if bold:
            style_config.update(UIFactory.STYLES['label_bold'])
        elif small:
            style_config.update(UIFactory.STYLES['label_small'])
        else:
            style_config.update(UIFactory.STYLES['label_regular'])
        
        # Добавляем цвет если указан
        if foreground:
            style_config['foreground'] = foreground
        
        # Объединяем стили
        style_config.update(kwargs)
        
        label = ttk.Label(parent, text=text, **style_config)
        logger.debug(f"Создана метка: text={text}, bold={bold}, small={small}")
        return label
    
    @staticmethod
    def create_entry(parent: tk.Widget,
                    textvariable: Optional[tk.Variable] = None,
                    width: Optional[int] = None,
                    tooltip: Optional[str] = None,
                    **kwargs) -> ttk.Entry:
        """
        Создает поле ввода
        
        Args:
            parent: Родительский виджет
            textvariable: Переменная для хранения значения
            width: Ширина поля
            tooltip: Текст всплывающей подсказки
            **kwargs: Дополнительные параметры
            
        Returns:
            ttk.Entry: Созданное поле ввода
        """
        # Объединяем стили
        style_config = UIFactory.STYLES['entry_regular'].copy()
        if width:
            style_config['width'] = width
        style_config.update(kwargs)
        
        entry = ttk.Entry(parent, textvariable=textvariable, **style_config)
        
        # Добавляем подсказку если указана
        if tooltip:
            Tooltip(entry, tooltip)
        
        logger.debug(f"Создано поле ввода: width={width}, tooltip={bool(tooltip)}")
        return entry
    
    @staticmethod
    def create_frame(parent: tk.Widget,
                    padding: Optional[int] = None,
                    **kwargs) -> ttk.Frame:
        """
        Создает фрейм
        
        Args:
            parent: Родительский виджет
            padding: Внутренние отступы
            **kwargs: Дополнительные параметры
            
        Returns:
            ttk.Frame: Созданный фрейм
        """
        frame = ttk.Frame(parent, **kwargs)
        if padding:
            frame.configure(padding=padding)
        
        logger.debug("Создан фрейм")
        return frame
    
    @staticmethod
    def create_label_frame(parent: tk.Widget,
                          text: str,
                          padding: Optional[int] = 5,
                          **kwargs) -> ttk.LabelFrame:
        """
        Создает фрейм с заголовком
        
        Args:
            parent: Родительский виджет
            text: Текст заголовка
            padding: Внутренние отступы
            **kwargs: Дополнительные параметры
            
        Returns:
            ttk.LabelFrame: Созданный фрейм с заголовком
        """
        frame = ttk.LabelFrame(parent, text=text, **kwargs)
        if padding:
            frame.configure(padding=padding)
        
        logger.debug(f"Создан фрейм с заголовком: text={text}")
        return frame
    
    @staticmethod
    def create_scrolled_text(parent: tk.Widget,
                            wrap: str = tk.NONE,
                            height: Optional[int] = None,
                            **kwargs) -> scrolledtext.ScrolledText:
        """
        Создает текстовое поле со скроллбаром
        
        Args:
            parent: Родительский виджет
            wrap: Перенос строк
            height: Высота в строках
            **kwargs: Дополнительные параметры
            
        Returns:
            scrolledtext.ScrolledText: Созданное текстовое поле
        """
        # Объединяем стили
        style_config = UIFactory.STYLES['text_editor'].copy()
        style_config['wrap'] = wrap
        
        if height:
            style_config['height'] = height
        
        style_config.update(kwargs)
        
        text_widget = scrolledtext.ScrolledText(parent, **style_config)
        
        # Настраиваем табуляцию
        try:
            import tkinter.font as font
            current_font = text_widget.cget('font')
            font_obj = font.Font(font=current_font)
            tab_width = font_obj.measure(' ' * 4)
            text_widget.configure(tabs=(tab_width,))
        except Exception as e:
            logger.warning(f"Не удалось настроить Tab: {e}")
            text_widget.configure(tabs=32)
        
        logger.debug(f"Создано текстовое поле: height={height}, wrap={wrap}")
        return text_widget
    
    @staticmethod
    def create_treeview(parent: tk.Widget,
                       columns: List[str],
                       show: str = 'tree',
                       **kwargs) -> ttk.Treeview:
        """
        Создает дерево (Treeview)
        
        Args:
            parent: Родительский виджет
            columns: Список колонок
            show: Что показывать ('tree', 'headings', 'tree headings')
            **kwargs: Дополнительные параметры
            
        Returns:
            ttk.Treeview: Созданное дерево
        """
        tree = ttk.Treeview(parent, columns=columns, show=show, **kwargs)
        logger.debug(f"Создано дерево: columns={columns}, show={show}")
        return tree
    
    @staticmethod
    def create_separator(parent: tk.Widget,
                        orient: str = 'horizontal',
                        **kwargs) -> ttk.Separator:
        """
        Создает разделитель
        
        Args:
            parent: Родительский виджет
            orient: Ориентация ('horizontal' или 'vertical')
            **kwargs: Дополнительные параметры
            
        Returns:
            ttk.Separator: Созданный разделитель
        """
        separator = ttk.Separator(parent, orient=orient, **kwargs)
        logger.debug(f"Создан разделитель: orient={orient}")
        return separator
    
    @staticmethod
    def create_checkbutton(parent: tk.Widget,
                          text: str,
                          variable: Optional[tk.Variable] = None,
                          tooltip: Optional[str] = None,
                          **kwargs) -> ttk.Checkbutton:
        """
        Создает флажок (Checkbutton)
        
        Args:
            parent: Родительский виджет
            text: Текст флажка
            variable: Переменная для хранения состояния
            tooltip: Текст всплывающей подсказки
            **kwargs: Дополнительные параметры
            
        Returns:
            ttk.Checkbutton: Созданный флажок
        """
        checkbutton = ttk.Checkbutton(parent, text=text, variable=variable, **kwargs)
        
        # Добавляем подсказку если указана
        if tooltip:
            Tooltip(checkbutton, tooltip)
        
        logger.debug(f"Создан флажок: text={text}, tooltip={bool(tooltip)}")
        return checkbutton
    
    @staticmethod
    def create_scrollbar(parent: tk.Widget,
                        orient: str = 'vertical',
                        command: Optional[Callable] = None,
                        **kwargs) -> ttk.Scrollbar:
        """
        Создает полосу прокрутки
        
        Args:
            parent: Родительский виджет
            orient: Ориентация ('vertical' или 'horizontal')
            command: Команда для прокрутки
            **kwargs: Дополнительные параметры
            
        Returns:
            ttk.Scrollbar: Созданная полоса прокрутки
        """
        scrollbar = ttk.Scrollbar(parent, orient=orient, command=command, **kwargs)
        logger.debug(f"Создана полоса прокрутки: orient={orient}")
        return scrollbar
    
    @staticmethod
    def create_button_frame(parent: tk.Widget,
                           title: str,
                           buttons_config: List[Dict[str, Any]],
                           **kwargs) -> ttk.LabelFrame:
        """
        Создает фрейм с кнопками по конфигурации
        
        Args:
            parent: Родительский виджет
            title: Заголовок фрейма
            buttons_config: Конфигурация кнопок
            **kwargs: Дополнительные параметры
            
        Returns:
            ttk.LabelFrame: Созданный фрейм с кнопками
        """
        frame = UIFactory.create_label_frame(parent, text=title, **kwargs)
        
        for config in buttons_config:
            btn = UIFactory.create_button(
                frame,
                text=config.get('text', ''),
                command=config.get('command'),
                tooltip=config.get('tooltip'),
                square=config.get('square', False),
                width=config.get('width')
            )
            btn.pack(side=tk.LEFT, padx=config.get('padx', 2))
        
        logger.debug(f"Создан фрейм с кнопками: title={title}, buttons={len(buttons_config)}")
        return frame
    
    @staticmethod
    def create_toolbar(parent: tk.Widget,
                      buttons_config: List[Dict[str, Any]],
                      **kwargs) -> ttk.Frame:
        """
        Создает панель инструментов
        
        Args:
            parent: Родительский виджет
            buttons_config: Конфигурация кнопок
            **kwargs: Дополнительные параметры
            
        Returns:
            ttk.Frame: Созданная панель инструментов
        """
        toolbar = UIFactory.create_frame(parent, **kwargs)
        
        for config in buttons_config:
            btn = UIFactory.create_button(
                toolbar,
                text=config.get('text', ''),
                command=config.get('command'),
                tooltip=config.get('tooltip'),
                square=config.get('square', False),
                width=config.get('width')
            )
            btn.pack(side=tk.LEFT, padx=config.get('padx', 2))
        
        logger.debug(f"Создана панель инструментов: buttons={len(buttons_config)}")
        return toolbar
    
    @staticmethod
    def setup_default_styles():
        """
        Настраивает стандартные стили для ttk
        """
        try:
            style = ttk.Style()
            
            # Стиль для кнопок
            style.configure('TButton', font=('Arial', 10))
            
            # Стиль для меток
            style.configure('TLabel', font=('Arial', 10))
            style.configure('Bold.TLabel', font=('Arial', 10, 'bold'))
            style.configure('Small.TLabel', font=('Arial', 8))
            
            # Стиль для фреймов
            style.configure('TLabelframe', font=('Arial', 10, 'bold'))
            
            logger.debug("Стили ttk настроены")
        except Exception as e:
            logger.warning(f"Не удалось настроить стили ttk: {e}")


# Инициализация фабрики
ui_factory = UIFactory()