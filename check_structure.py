# check_structure.py
import os

project_root = os.getcwd()
print(f"Корень проекта: {project_root}")

files_to_check = [
    ("pytest.ini", project_root),
    ("run_tests.py", project_root),
    ("tests/conftest.py", project_root),
    ("gui/views/__init__.py", project_root),
]

for file_name, base_dir in files_to_check:
    full_path = os.path.join(base_dir, file_name)
    exists = os.path.exists(full_path)
    print(f"{'?' if exists else '?'} {file_name}: {exists}")