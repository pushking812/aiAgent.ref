# check_files.py
import os

base_dir = "D:/1py/aiAgent.ref"
test_files = [
    "tests/conftest.py",
    "tests/pytest.ini",
    "tests/run_tests.py",
    "tests/unit/test_dialogs_view.py",
    "tests/unit/test_main_window_view.py",
    "tests/unit/test_code_editor_view.py",
    "tests/unit/test_project_tree_view.py",
    "tests/gui/test_gui_components.py",
    "tests/gui/test_real_tkinter.py",
    "tests/integration/test_gui_integration.py"
]

for file in test_files:
    path = os.path.join(base_dir, file)
    exists = os.path.exists(path)
    print(f"{'?' if exists else '?'} {file}: {exists}")