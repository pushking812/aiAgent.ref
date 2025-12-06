# tests/conftest.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Регистрируем маркеры
def pytest_configure(config):
    """Регистрируем пользовательские маркеры."""
    config.addinivalue_line(
        "markers",
        "gui: тесты GUI компонентов (требуют tkinter)"
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
        "requires_gui: тесты, требующие реального GUI окружения"
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
    parser.addoption(
        "--run-gui",
        action="store_true", 
        default=False,
        help="запускать GUI тесты (требует tkinter)"
    )
    parser.addoption(
        "--no-gui",
        action="store_true",
        default=False,
        help="пропускать GUI тесты"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="запускать GUI тесты в headless режиме (требует Xvfb)"
    )

def pytest_collection_modifyitems(config, items):
    """Модифицируем коллекцию тестов."""
    # Обработка медленных тестов
    runslow = config.getoption("--runslow", default=False)
    if not runslow:
        skip_slow = pytest.mark.skip(reason="требуется --runslow чтобы запустить")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
    
    # Обработка GUI тестов
    run_gui = config.getoption("--run-gui", default=False)
    no_gui = config.getoption("--no-gui", default=False)
    
    # Пропускаем GUI тесты если не указан --run-gui или указан --no-gui
    if not run_gui or no_gui:
        skip_gui = pytest.mark.skip(reason="GUI тесты отключены, используйте --run-gui для запуска")
        for item in items:
            if "requires_gui" in item.keywords or "requires_tkinter" in item.keywords:
                item.add_marker(skip_gui)
    
    # Проверяем доступность tkinter для GUI тестов
    if run_gui and not no_gui:
        try:
            import tkinter as tk
            tk_available = True
        except ImportError:
            tk_available = False
        
        if not tk_available:
            skip_no_tk = pytest.mark.skip(reason="tkinter не установлен")
            for item in items:
                if "requires_tkinter" in item.keywords or "gui" in item.keywords:
                    item.add_marker(skip_no_tk)

# ОБЩИЕ ФИКСТУРЫ
@pytest.fixture
def tk_root():
    """Создает корневое окно tkinter для тестов (только если tkinter доступен)."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        yield root
        
        # Очистка
        try:
            root.destroy()
        except (tk.TclError, RuntimeError):
            pass
    except ImportError as e:
        pytest.skip(f"Tkinter не доступен: {e}")

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
    mock_tk.IntVar = Mock()
    mock_tk.BooleanVar = Mock()
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
    mock_tk.WORD = 'word'
    mock_tk.CHAR = 'char'
    
    return mock_tk

@pytest.fixture
def mock_tkinter_ttk():
    """Фикстура для мока ttk."""
    mock_ttk = Mock()
    mock_ttk.Frame = Mock()
    mock_ttk.Label = Mock()
    mock_ttk.Button = Mock()
    mock_ttk.LabelFrame = Mock()
    mock_ttk.Scrollbar = Mock()
    mock_ttk.Entry = Mock()
    mock_ttk.Combobox = Mock()
    mock_ttk.Radiobutton = Mock()
    mock_ttk.Checkbutton = Mock()
    mock_ttk.Treeview = Mock()
    mock_ttk.Style = Mock()
    return mock_ttk

@pytest.fixture
def mock_messagebox():
    """Фикстура для мока messagebox."""
    with patch('tkinter.messagebox') as mock_mb:
        mock_mb.askyesnocancel = Mock(return_value=True)
        mock_mb.showinfo = Mock()
        mock_mb.showerror = Mock()
        mock_mb.showwarning = Mock()
        mock_mb.askyesno = Mock(return_value=True)
        yield mock_mb

@pytest.fixture
def mock_filedialog():
    """Фикстура для мока filedialog."""
    with patch('tkinter.filedialog') as mock_fd:
        mock_fd.askdirectory = Mock(return_value="/test/path")
        mock_fd.askopenfilename = Mock(return_value="/test/file.py")
        mock_fd.asksaveasfilename = Mock(return_value="/test/save.py")
        yield mock_fd

# ФИКСТУРЫ ДЛЯ КОНКРЕТНЫХ КОМПОНЕНТОВ GUI
@pytest.fixture
def code_editor_view(tk_root):
    """Создает экземпляр CodeEditorView."""
    from gui.views.code_editor_view import CodeEditorView
    view = CodeEditorView(tk_root)
    yield view
    # Очистка
    try:
        view.destroy()
    except:
        pass

@pytest.fixture
def main_window_view(tk_root):
    """Создает экземпляр MainWindowView."""
    from gui.views.main_window_view import MainWindowView
    view = MainWindowView(tk_root)
    yield view
    # Очистка
    try:
        view.destroy()
    except:
        pass

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
    yield view
    # Очистка
    try:
        view.destroy()
    except:
        pass

# ВСПОМОГАТЕЛЬНЫЕ ФИКСТУРЫ
@pytest.fixture
def sample_project_structure():
    """Возвращает пример структуры проекта для тестов."""
    return {
        "modules": ["app", "tests", "gui", "utils"],
        "files": {
            "app/__init__.py": "",
            "app/main.py": "print('Hello, World!')",
            "app/utils.py": "def helper():\n    pass",
            "tests/__init__.py": "",
            "tests/test_app.py": "import pytest\n\ndef test_dummy():\n    assert True",
            "gui/__init__.py": "",
            "gui/views.py": "class View:\n    def __init__(self):\n        pass",
            "utils/__init__.py": "",
            "utils/helpers.py": "def calculate():\n    return 42",
            "requirements.txt": "pytest>=7.0.0\npytest-cov>=4.0.0",
            "README.md": "# Test Project\n\nThis is a test project.",
            ".gitignore": "*.pyc\n__pycache__/\n*.log",
        }
    }

@pytest.fixture
def mock_callback():
    """Создает mock для callback функций."""
    return Mock()

@pytest.fixture
def compare_tkinter_values():
    """Хелпер для сравнения значений Tkinter."""
    
    def compare(value1, value2):
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
    
    return compare

@pytest.fixture
def temp_project_dir(tmp_path):
    """Создает временную директорию для тестов проекта."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Создаем структуру каталогов
    for subdir in ["app", "tests", "gui", "utils"]:
        (project_dir / subdir).mkdir()
        (project_dir / subdir / "__init__.py").write_text("")
    
    # Создаем несколько тестовых файлов
    (project_dir / "app" / "main.py").write_text("print('Hello')")
    (project_dir / "tests" / "test_main.py").write_text("def test_dummy(): pass")
    (project_dir / "requirements.txt").write_text("pytest>=7.0.0")
    (project_dir / "README.md").write_text("# Test Project")
    
    yield project_dir
    
    # Очистка выполняется автоматически через tmp_path

@pytest.fixture
def mock_logger():
    """Создает mock для логгера."""
    mock_logger = Mock()
    mock_logger.debug = Mock()
    mock_logger.info = Mock()
    mock_logger.warning = Mock()
    mock_logger.error = Mock()
    mock_logger.critical = Mock()
    return mock_logger

# Настройка окружения для тестов
def pytest_sessionstart(session):
    """Выполняется в начале сессии тестирования."""
    os.environ.setdefault('PYTEST_GUI_TESTING', '1')
    
def pytest_sessionfinish(session, exitstatus):
    """Выполняется в конце сессии тестирования."""
    # Очищаем переменные окружения
    if 'PYTEST_GUI_TESTING' in os.environ:
        del os.environ['PYTEST_GUI_TESTING']