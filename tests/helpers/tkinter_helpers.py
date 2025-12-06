# tests/helpers/tkinter_helpers.py

"""Хелперы для работы с Tkinter в тестах."""

from unittest.mock import MagicMock, Mock


def create_mock_widget(widget_type="frame", **kwargs):
    """Создает mock виджет Tkinter с базовыми методами."""
    mock_widget = MagicMock()
    mock_widget.pack = Mock()
    mock_widget.grid = Mock()
    mock_widget.place = Mock()
    mock_widget.config = Mock()
    mock_widget.cget = Mock(return_value="default")
    mock_widget.winfo_exists = Mock(return_value=True)
    mock_widget.winfo_children = Mock(return_value=[])
    mock_widget.winfo_parent = Mock(return_value=None)
    mock_widget.bind = Mock()
    mock_widget.unbind = Mock()

    # Дополнительные методы для конкретных типов виджетов
    if widget_type == "text":
        mock_widget.get = Mock(return_value="")
        mock_widget.delete = Mock()
        mock_widget.insert = Mock()
        mock_widget.see = Mock()
        mock_widget.update = Mock()
        mock_widget.tag_configure = Mock()
        mock_widget.tag_add = Mock()
        mock_widget.tag_remove = Mock()
        mock_widget.mark_set = Mock()

    elif widget_type == "treeview":
        mock_widget.insert = Mock()
        mock_widget.delete = Mock()
        mock_widget.get_children = Mock(return_value=[])
        mock_widget.item = Mock()
        mock_widget.selection_set = Mock()
        mock_widget.focus = Mock()
        mock_widget.see = Mock()
        mock_widget.parent = Mock(return_value="")

    elif widget_type == "button":
        mock_widget.invoke = Mock()
        mock_widget.flash = Mock()

    # Устанавливаем переданные атрибуты
    for key, value in kwargs.items():
        setattr(mock_widget, key, value)

    return mock_widget


class MockTkinterWidget:
    """Класс для создания mock виджетов Tkinter."""

    def __init__(self, widget_type="frame", **kwargs):
        self.widget_type = widget_type
        self.mock = create_mock_widget(widget_type, **kwargs)

    def __getattr__(self, name):
        return getattr(self.mock, name)

    def __call__(self, *args, **kwargs):
        return self.mock(*args, **kwargs)
