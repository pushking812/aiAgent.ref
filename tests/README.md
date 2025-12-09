*tests/README.md*

# Структура тестов GUI приложения

## ## Структура директорий

tests/
+-- conftest.py # Основные фикстуры и настройки
+-- base_gui_test.py # Базовый класс для GUI тестов
+-- helpers/ # Вспомогательные модули
¦ +-- init.py
¦ +-- tkinter_helpers.py # Хелперы для работы с Tkinter
¦ L-- comparison_helpers.py # Хелперы для сравнения
+-- unit/ # Юнит-тесты
¦ +-- init.py
¦ +-- test_basic.py
¦ +-- test_code_editor_view.py
¦ +-- test_project_tree_view.py
¦ +-- test_main_window_view.py
¦ L-- test_dialogs_view.py
+-- integration/ # Интеграционные тесты
¦ +-- init.py
¦ L-- test_gui_integration.py
+-- gui/ # GUI тесты (с реальным tkinter)
¦ +-- init.py
¦ +-- test_gui_components.py
¦ L-- test_real_tkinter.py
L-- init.py



## ### Маркеры тестов

- `@pytest.mark.gui` - GUI тесты, требующие tkinter
- `@pytest.mark.unit` - Unit-тесты без зависимостей
- `@pytest.mark.integration` - Интеграционные тесты
- `@pytest.mark.slow` - Медленные тесты (пропускаются по умолчанию)
- `@pytest.mark.requires_gui` - Требуют реального GUI окружения
- `@pytest.mark.requires_tkinter` - Требуют установленного tkinter

## ## Запуск тестов

### Скрипт run_tests.py

# Все тесты
python run_tests.py

# С покрытием кода
python run_tests.py --coverage

# Только unit тесты
python run_tests.py --module unit

# Только GUI тесты
python run_tests.py --module gui

# GUI тесты в headless режиме (Linux)
python run_tests.py --gui-headless

# Тесты с определенным маркером
python run_tests.py -m gui

# Медленные тесты
python run_tests.py --runslow

Прямой запуск через pytest


# Все тесты
pytest tests/

# Только unit тесты
pytest tests/unit/

# С покрытием
pytest tests/ --cov=gui --cov-report=html

# GUI тесты (если tkinter доступен)
pytest tests/gui/ --run-gui

## Конфигурация
pytest.ini

Основные настройки pytest, включая маркеры, фильтры предупреждений и настройки покрытия.
requirements-test.txt
Тестовые зависимости Python. Устанавливаются командой:
pip install -r requirements-test.txt
.github/workflows/ci.yml
CI/CD конфигурация для GitHub Actions. Запускает:
    Линтинг и форматирование
    Матрицу тестов на разных ОС и версиях Python
    Тесты производительности
    Деплой документации тестов

## Покрытие кода

Целевой уровень покрытия: 70%
Отчеты о покрытии генерируются в директории:
    htmlcov/ - HTML отчет
    coverage.xml - XML отчет для CI
    Терминал - краткий отчет

## Фикстуры (conftest.py)

Основные фикстуры:
    tk_root() - Корневое окно Tkinter
    code_editor_view() - Экземпляр CodeEditorView
    main_window_view() - Экземпляр MainWindowView
    project_tree_view() - Экземпляр ProjectTreeView
    dialogs_view() - Экземпляр DialogsView
    sample_project_structure() - Пример структуры проекта для тестов

### Хелперы
tkinter_helpers.py

Функции для сравнения Tkinter объектов:
    compare_tkinter_colors() - сравнение цветов
    compare_show_values() - сравнение значений 'show' для Treeview
    compare_tkinter_values() - универсальное сравнение

### Модульность

Тесты разделены по типам:
    Unit тесты (tests/unit/) - тестирование отдельных компонентов
    Integration тесты (tests/integration/) - тестирование взаимодействия компонентов
    GUI тесты (tests/gui/) - тесты с реальным Tkinter
Каждый модуль тестирует определенный компонент GUI:
    main_window_view.py - Главное окно
    code_editor_view.py - Редактор кода
    project_tree_view.py - Дерево проекта
    dialogs_view.py - Диалоговые окна

## Отладка тестов

Для отладки используйте флаги:


# Подробный вывод
pytest -v

# Вывод трассировки
pytest --tb=long

# Остановка на первом падении
pytest -x

# Запуск конкретного теста
pytest tests/unit/test_code_editor_view.py::TestCodeEditorView::test_initialization

## Мониторинг покрытия

Проверка текущего покрытия:
python run_tests.py --check-coverage
