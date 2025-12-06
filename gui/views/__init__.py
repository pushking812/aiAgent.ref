# gui/views/__init__.py

from .main_window_view import MainWindowView, IMainWindowView
from .code_editor_view import CodeEditorView, ICodeEditorView
from .dialogs_view import DialogsView, IDialogsView

# ProjectTreeView может быть временно отключен если есть проблемы с импортом
try:
    from .project_tree_view import ProjectTreeView, IProjectTreeView
    __all__ = [
        'MainWindowView',
        'IMainWindowView',
        'CodeEditorView',
        'ICodeEditorView',
        'ProjectTreeView',
        'IProjectTreeView',
        'DialogsView',
        'IDialogsView'
    ]
except ImportError as e:
    print(f"Warning: Could not import ProjectTreeView: {e}")
    __all__ = [
        'MainWindowView',
        'IMainWindowView',
        'CodeEditorView',
        'ICodeEditorView',
        'DialogsView',
        'IDialogsView'
    ]