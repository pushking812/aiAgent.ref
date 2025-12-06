# tests/conftest.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk

# Регистрируем маркеры
def pytest_configure(config):
    """Регистрируем пользовательские маркеры."""
    config.addinivalue_line(
        "markers",
        "gui: тесты, связанные с GUI компонентами"
    )
    config.addinivalue_line(
        "markers", 
        "unit: unit-тесты (без зависимостей)"
    )
    config.addinivalue_line(
        "markers",
        "integration: интеграционные тесты"
    )
    config.addinivalue_line(
        "markers",
        "slow: медленные тесты (пропускаются по умолчанию)"
    )
    config.addinivalue_line(
        "markers",
        "requires_tkinter: тесты, требующие tkinter"
    )

def pytest_addoption(parser):
    """Добавляем пользовательские опции командной строки."""
    parser.addoption(
        "--runslow",
        action="store_true",
        default=False,
        help="запускать медленные тесты"
    )

def pytest_collection_modifyitems(config, items):
    """Модифицируем коллекцию тестов."""
    runslow = config.getoption("--runslow", default=False)
    
    if not runslow:
        skip_slow = pytest.mark.skip(reason="требуется --runslow чтобы запустить")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

# ОБЩИЕ ФИКСТУРЫ
@pytest.fixture
def tk_root():
    """Создает корневое окно tkinter для тестов."""
    try:
        root = tk.Tk()
        root.withdraw()
        yield root
        try:
            root.destroy()
        except:
            pass
    except tk.TclError:
        pytest.skip("Tkinter не доступен")

@pytest.fixture
def mock_tkinter():
    """Фикстура для мока tkinter."""
    mock_tk = Mock()
    mock_tk.Tk = Mock()
    mock_tk.Toplevel = Mock()
    mock_tk.Frame = Mock()
    mock_tk.Label = Mock()
    mock_tk.Button = Mock()
    mock_tk.Text = Mock()
    mock_tk.ScrolledText = Mock()
    mock_tk.Entry = Mock()
    mock_tk.StringVar = Mock()
    mock_tk.BOTH = 'both'
    mock_tk.X = 'x'
    mock_tk.Y = 'y'
    mock_tk.LEFT = 'left'
    mock_tk.RIGHT = 'right'
    mock_tk.TOP = 'top'
    mock_tk.BOTTOM = 'bottom'
    mock_tk.END = 'end'
    mock_tk.NORMAL = 'normal'
    mock_tk.DISABLED = 'disabled'
    mock_tk.NONE = 'none'
    
    return mock_tk

@pytest.fixture
def mock_messagebox():
    """Фикстура для мока messagebox."""
    with patch('tkinter.messagebox') as mock_mb:
        yield mock_mb

@pytest.fixture
def mock_filedialog():
    """Фикстура для мока filedialog."""
    with patch('tkinter.filedialog') as mock_fd:
        yield mock_fd

# ФИКСТУРЫ ДЛЯ КОНКРЕТНЫХ КОМПОНЕНТОВ
@pytest.fixture
def code_editor_view(tk_root):
    """Создает экземпляр CodeEditorView."""
    from gui.views.code_editor_view import CodeEditorView
    view = CodeEditorView(tk_root)
    return view

@pytest.fixture
def main_window_view(tk_root):
    """Создает экземпляр MainWindowView."""
    from gui.views.main_window_view import MainWindowView
    view = MainWindowView(tk_root)
    return view

@pytest.fixture
def dialogs_view(tk_root):
    """Создает экземпляр DialogsView."""
    from gui.views.dialogs_view import DialogsView
    view = DialogsView(tk_root)
    return view

@pytest.fixture
def project_tree_view(tk_root):
    """Создает экземпляр ProjectTreeView."""
    from gui.views.project_tree_view import ProjectTreeView
    view = ProjectTreeView(tk_root)
    view.setup_tree()
    return view

# ВСПОМОГАТЕЛЬНЫЕ ФИКСТУРЫ
@pytest.fixture
def sample_project_structure():
    """Возвращает пример структуры проекта для тестов."""
    return {
        "modules": ["app", "tests", "gui"],
        "files": {
            "app/main.py": "print('Hello')",
            "app/utils.py": "def helper(): pass",
            "tests/test_app.py": "import pytest",
            "gui/views.py": "class View: pass"
        }
    }

@pytest.fixture
def mock_callback():
    """Создает mock для callback функций."""
    return Mock()