# gui/views/__init__.py

from .code_editor_view import CodeEditorView, ICodeEditorView
from .dialogs_view import DialogsView, IDialogsView
from .main_window_view import IMainWindowView, MainWindowView

# ProjectTreeView может быть временно отключен если есть проблемы с импортом
try:
    from .project_tree_view import IProjectTreeView, ProjectTreeView
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
