# Инструкция по запуску тестов

## Структура тестов

tests/
+-- conftest.py # Основные фикстуры и настройки pytest
+-- base_gui_test.py # Базовый класс для GUI тестов
+-- helpers/ # Вспомогательные модули
¦ +-- init.py
¦ +-- tkinter_helpers.py # Хелперы для работы с Tkinter
¦ L-- comparison_helpers.py # Хелперы для сравнения
+-- unit/ # Юнит-тесты (без GUI)
¦ +-- init.py
¦ +-- test_code_editor_view.py
¦ +-- test_dialogs_view.py
¦ +-- test_main_window_view.py
¦ L-- test_project_tree_view.py
+-- integration/ # Интеграционные тесты
¦ +-- init.py
¦ L-- test_gui_integration.py
+-- gui/ # GUI тесты (с реальным tkinter)
¦ +-- init.py
¦ +-- test_gui_components.py
¦ L-- test_real_tkinter.py
+-- test_basic.py # Базовые тесты
L-- init.py
text


## Маркеры тестов

- `@pytest.mark.unit` - юнит-тесты (без зависимостей)
- `@pytest.mark.gui` - GUI тесты (могут требовать tkinter)
- `@pytest.mark.integration` - интеграционные тесты
- `@pytest.mark.slow` - медленные тесты (пропускаются по умолчанию)
- `@pytest.mark.requires_tkinter` - тесты, требующие tkinter
- `@pytest.mark.tkinter` - тесты с реальным tkinter

## Команды для запуска

### 1. Все тесты (кроме медленных)
pytest
2. Только юнит-тесты
pytest -m unit
3. GUI тесты (если tkinter доступен)
pytest --run-gui -m gui
4. Все тесты включая медленные
pytest --runslow
5. Тесты с покрытием
pytest --cov=gui.views --cov-report=html --cov-report=term-missing
6. Тесты с детальным выводом
pytest -v --tb=short
7. Пропустить GUI тесты
pytest --no-gui
Запуск конкретных тестов
Запуск одного файла
pytest tests/unit/test_code_editor_view.py
Запуск одного тестового класса
pytest tests/unit/test_dialogs_view.py::TestDialogsViewUnit
Запуск одного теста
pytest tests/unit/test_dialogs_view.py::TestDialogsViewUnit::test_interface_methods_exist
Покрытие кода
Для проверки покрытия кода установите pytest-cov:
pip install pytest-cov
Запуск с покрытием:
pytest --cov=gui.views --cov-report=html
HTML отчет будет создан в папке htmlcov/.
Отладка тестов
Для отладки проблемных тестов:
    Запустить с максимальной детализацией:
pytest -vvs --tb=long
    Запустить только проблемный тест:
pytest -xvs tests/path/to/test.py::TestClass::test_method
    Использовать отладчик:
python
import pdb; pdb.set_trace()  # Вставить в тест для отладки
Примечания
    GUI тесты требуют установленного tkinter
    Некоторые тесты могут требовать графической среды (X11/Wayland на Linux)
    Для headless тестирования можно использовать xvfb:
xvfb-run pytest --run-gui
    Тесты помеченные как @pytest.mark.slow пропускаются по умолчанию
    Для ускорения тестов можно использовать параллельный запуск:
pytest -n auto
Опции pytest
Основные опции командной строки:
    -v, --verbose: Увеличить детализацию вывода
    -q, --quiet: Уменьшить детализацию вывода
    -x, --exitfirst: Выйти при первой ошибке
    --lf, --last-failed: Запустить только упавшие тесты
    --ff, --failed-first: Сначала запустить упавшие тесты
    -k EXPRESSION: Запустить только тесты, соответствующие выражению
    -m MARKEXPR: Запустить только тесты с указанным маркером
text


## Сводка изменений:

1. **Убраны дублирующиеся файлы**: Все файлы с `test_dialogs_*.py` были объединены в один логичный набор тестов.

2. **Создана структурированная архитектура**:
   - `tests/unit/` - юнит-тесты без зависимостей
   - `tests/gui/` - GUI тесты с реальным tkinter
   - `tests/integration/` - интеграционные тесты
   - `tests/helpers/` - вспомогательные функции

3. **Вынесен общий код** в `helpers/`:
   - Функции для создания mock виджетов
   - Хелперы для сравнения Tkinter значений
   - Утилиты для работы с тестами

4. **Создан базовый класс** `BaseGUITest` с общими фикстурами.

5. **Унифицированы маркеры тестов** для четкого разделения.

6. **Создана документация** `RUN_TESTS.md` с инструкциями по запуску.

7. **Улучшена конфигурация pytest** в `conftest.py`.

## Преимущества новой структуры:

1. **Устранено дублирование кода** - общие функции вынесены в хелперы
2. **Четкое разделение тестов** - unit, gui, integration
3. **Упрощенный запуск** - разные маркеры для разных типов тестов
4. **Лучшая поддерживаемость** - изменения в одном месте
5. **Улучшенная читаемость** - логическая группировка тестов
6. **Легче добавлять новые тесты** - понятная структура

Теперь тесты можно запускать более целенаправленно и эффективно!
