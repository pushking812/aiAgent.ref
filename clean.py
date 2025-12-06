import shutil
import os
import glob

def clean_cache():
    patterns = [
        "**/__pycache__",
        "**/.pytest_cache",
        "**/.coverage",
        "**/coverage_html",
        "**/htmlcov",
        "**/.mypy_cache",
        "**/.tox",
        "**/*.egg-info",
        "**/build",
        "**/dist"
    ]
    
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    print(f"Удалена папка: {path}")
                else:
                    os.remove(path)
                    print(f"Удален файл: {path}")
            except Exception as e:
                print(f"Ошибка при удалении {path}: {e}")

if __name__ == "__main__":
    clean_cache()
    print("Очистка завершена!")