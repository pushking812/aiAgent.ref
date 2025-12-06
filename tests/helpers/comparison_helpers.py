# tests/helpers/comparison_helpers.py

"""Хелперы для сравнения значений в тестах."""


def compare_tkinter_values(value1, value2):
    """Умное сравнение Tkinter значений."""
    # Если оба - строки, просто сравниваем
    if isinstance(value1, str) and isinstance(value2, str):
        return value1 == value2

    # Если один из них None
    if value1 is None or value2 is None:
        return value1 is value2

    # Преобразуем оба в строки для сравнения
    str1 = str(value1).strip().lower()
    str2 = str(value2).strip().lower()

    # Убираем возможные префиксы/суффиксы
    str1 = str1.replace("'", "").replace('"', '')
    str2 = str2.replace("'", "").replace('"', '')

    return str1 == str2


def tk_color_comparison_helper():
    """Хелпер для сравнения цветов Tkinter."""

    def compare_colors(color1, color2):
        """Сравнивает два цвета Tkinter."""
        # Оба могут быть объектами или строками
        str1 = str(color1).lower().strip()
        str2 = str(color2).lower().strip()
        return str1 == str2

    return compare_colors


def tk_show_value_helper():
    """Хелпер для сравнения значений 'show'."""

    def compare_show_values(value1, value2):
        """Сравнивает значения 'show'."""
        # Обрабатываем кортежи и строки
        if isinstance(value1, tuple):
            str1 = ''.join(str(item) for item in value1)
        else:
            str1 = str(value1)

        if isinstance(value2, tuple):
            str2 = ''.join(str(item) for item in value2)
        else:
            str2 = str(value2)

        return str1 == str2

    return compare_show_values
