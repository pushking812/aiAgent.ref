# tests/run_fixed_tests.py

#!/usr/bin/env python3
import subprocess
import sys
import os


def run_fixed_tests():
    """Запускает исправленные тесты."""
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_main_window_view.py",
        "tests/test_code_editor_view.py", 
        "tests/test_dialogs_view.py",
        "tests/test_project_tree_view.py",
        "tests/test_integration.py",
        "tests/test_basic.py",
        "-v", 
        "--tb=short", 
        "--disable-warnings",
        "--cov=gui.views",
        "--cov-report=term",
        "--cov-report=html:coverage_html",
        "--cov-fail-under=70"
    ]
    
    print(f"🚀 Запуск исправленных тестов...")
    print(f"📋 Команда: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd)
    
    print("=" * 60)
    if result.returncode == 0:
        print("✅ Все тесты пройдены успешно!")
    else:
        print(f"❌ Тесты завершились с ошибкой (код: {result.returncode})")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_fixed_tests())