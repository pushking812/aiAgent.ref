# tests/run_all_tests.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import os


def run_all_tests():
    """Запускает все тесты."""
    test_files = [
        "tests/test_main_window_view.py",
        "tests/test_code_editor_view.py", 
        "tests/test_dialogs_view.py",
        "tests/test_dialogs_view_additional.py",
        "tests/test_project_tree_view.py",
        "tests/test_project_tree_view_additional.py",
        "tests/test_integration.py",
        "tests/test_basic.py",
        "tests/test_real_tkinter.py",
    ]
    
    cmd = [
        sys.executable, "-m", "pytest", 
        *test_files,
        "-v", 
        "--tb=short", 
        "--disable-warnings",
        "--cov=gui.views",
        "--cov-report=term",
        "--cov-report=html:coverage_html",
        "--cov-fail-under=75",
        "--runslow"  # Запускаем медленные тесты тоже
    ]
    
    print("🚀 Запуск всех тестов...")
    print(f"📋 Количество тестовых файлов: {len(test_files)}")
    print("=" * 60)
    
    result = subprocess.run(cmd)
    
    print("=" * 60)
    if result.returncode == 0:
        print("✅ Все тесты пройдены успешно!")
    else:
        print(f"❌ Тесты завершились с ошибкой (код: {result.returncode})")
    
    # Показываем отчет о покрытии
    if result.returncode != 0:
        print("\n📊 Анализ покрытия кода:")
        print("-" * 60)
        coverage_cmd = [
            sys.executable, "-m", "coverage", "report", 
            "--omit=*test*", "--sort=cover"
        ]
        subprocess.run(coverage_cmd)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_all_tests())