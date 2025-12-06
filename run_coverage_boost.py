# tests/run_coverage_boost.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для быстрого повышения покрытия тестами.
Запускает только тесты для модулей с низким покрытием.
"""

import subprocess
import sys
import os


def run_coverage_boost():
    """Запускает тесты для повышения покрытия."""
    
    print("🚀 ЗАПУСК ТЕСТОВ ДЛЯ ПОВЫШЕНИЯ ПОКРЫТИЯ")
    print("=" * 60)
    
    # Тесты для модулей которые нужно улучшить
    coverage_test_files = [
        "tests/test_dialogs_coverage.py",      # Для dialogs_view.py (самый низкий)
        "tests/test_main_window_view.py",      # Уже хорошо, но добавили тесты
        "tests/test_code_editor_view.py",      # Добавили дополнительные тесты
        "tests/test_project_tree_view.py",     # Добавили дополнительные тесты
    ]
    
    cmd = [
        sys.executable, "-m", "pytest",
        *coverage_test_files,
        "-v",
        "--tb=no",
        "--disable-warnings",
        "--cov=gui.views",
        "--cov-report=term",
        "--cov-report=html:coverage_html",
        "--cov-fail-under=70",  # Временная цель
        "-x",
    ]
    
    print(f"Запуск {len(coverage_test_files)} тестовых файлов...")
    print("-" * 60)
    
    result = subprocess.run(cmd)
    
    print("=" * 60)
    
    # Показываем детальный отчет
    if result.returncode != 0:
        print("⚠  Были ошибки. Анализируем покрытие...")
    
    print("\n📊 ТЕКУЩЕЕ ПОКРЫТИЕ ПО МОДУЛЯМ:")
    print("-" * 60)
    
    detail_cmd = [
        sys.executable, "-m", "coverage", "report",
        "--show-missing",
        "--omit=*test*"
    ]
    
    subprocess.run(detail_cmd)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_coverage_boost())