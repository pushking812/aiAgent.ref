# tests/run_optimized_tests.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Оптимизированный скрипт для запуска всех тестов с фокусом на покрытие.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_optimized_test_suite():
    """Запускает оптимизированный набор тестов."""
    
    # Основные тестовые файлы которые точно работают
    core_test_files = [
        "tests/test_main_window_view.py",
        "tests/test_code_editor_view.py", 
        "tests/test_project_tree_view.py",
        "tests/test_dialogs_view.py",  # Объединенный файл
        "tests/test_integration.py",
        "tests/test_basic.py",
    ]
    
    print("🚀 ЗАПУСК ОПТИМИЗИРОВАННОГО НАБОРА ТЕСТОВ")
    print("=" * 70)
    print(f"📋 Тестовых файлов: {len(core_test_files)}")
    print("🎯 Цель покрытия: 75%+")
    print("=" * 70)
    
    # Команда для запуска тестов
    cmd = [
        sys.executable, "-m", "pytest",
        *core_test_files,
        "-v",
        "--tb=no",  # Без детального traceback для чистоты
        "--disable-warnings",
        "--cov=gui.views",
        "--cov-report=term",
        "--cov-report=html:coverage_html",
        "--cov-fail-under=75",
        "--cov-branch",  # Включаем покрытие ветвей
        "-x",  # Останавливаться при первой ошибке
    ]
    
    print(f"▶  Команда: {' '.join(cmd[:5])} ...")
    print("-" * 70)
    
    # Запускаем тесты
    result = subprocess.run(cmd)
    
    print("=" * 70)
    
    # Анализируем результат
    if result.returncode == 0:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("🎉 ПОЗДРАВЛЯЮ! ЦЕЛЬ 75% ПОКРЫТИЯ ДОСТИГНУТА!")
    else:
        print(f"❌ Тесты завершились с кодом: {result.returncode}")
        print("💡 Анализируем проблемы...")
    
    # Всегда показываем детальный отчет
    print("\n📊 ДЕТАЛЬНЫЙ ОТЧЕТ О ПОКРЫТИИ ПО МОДУЛЯМ:")
    print("-" * 70)
    
    detail_cmd = [
        sys.executable, "-m", "coverage", "report",
        "--show-missing",
        "--omit=*test*,*__pycache__*",
        "--format=markdown"  # Более читаемый формат
    ]
    
    subprocess.run(detail_cmd)
    
    # Показываем итоговую статистику
    print("\n" + "=" * 70)
    print("📈 ИТОГОВАЯ СТАТИСТИКА ПОКРЫТИЯ")
    print("-" * 70)
    
    # Получаем общее покрытие
    total_cmd = [
        sys.executable, "-m", "coverage", "report",
        "--format=total",
        "--omit=*test*,*__pycache__*"
    ]
    
    total_result = subprocess.run(total_cmd, capture_output=True, text=True)
    if total_result.stdout:
        coverage_percent = total_result.stdout.strip()
        print(f"📊 ОБЩЕЕ ПОКРЫТИЕ: {coverage_percent}")
        
        # Проверяем достижение цели
        try:
            coverage_value = float(coverage_percent.rstrip('%'))
            if coverage_value >= 75:
                print("✅ ЦЕЛЬ 75% ДОСТИГНУТА!")
            else:
                print(f"⚠  ЦЕЛЬ 75% НЕ ДОСТИГНУТА (нужно: {75 - coverage_value:.1f}% больше)")
        except ValueError:
            print("⚠  Не удалось определить процент покрытия")
    
    print("=" * 70)
    
    # Рекомендации
    if result.returncode != 0:
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("1. Запустите проблемные тесты отдельно для отладки:")
        print("   python -m pytest tests/test_dialogs_view.py -v")
        print("2. Проверьте HTML отчет: открыть coverage_html/index.html")
        print("3. Добавьте тесты для строк, отмеченных как 'Missing' в отчете")
    
    return result.returncode


def run_quick_coverage_check():
    """Быстрая проверка покрытия без запуска всех тестов."""
    print("\n⚡ БЫСТРАЯ ПРОВЕРКА ПОКРЫТИЯ")
    print("-" * 50)
    
    # Используем существующий файл .coverage если есть
    if Path(".coverage").exists():
        cmd = [sys.executable, "-m", "coverage", "report", "--format=total"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout:
            print(f"Текущее покрытие: {result.stdout.strip()}")
        else:
            print("Файл .coverage не содержит данных")
    else:
        print("Файл .coverage не найден. Запустите тесты сначала.")
    
    print("-" * 50)


if __name__ == "__main__":
    # Показываем меню
    print("🎯 ТЕСТИРОВАНИЕ GUI МОДУЛЕЙ")
    print("=" * 50)
    print("1. Запустить полный набор тестов")
    print("2. Быстрая проверка покрытия")
    print("3. Выход")
    print("-" * 50)
    
    choice = input("Выберите опцию (1-3): ").strip()
    
    if choice == "1":
        sys.exit(run_optimized_test_suite())
    elif choice == "2":
        run_quick_coverage_check()
    elif choice == "3":
        print("Выход...")
        sys.exit(0)
    else:
        print("❌ Неверный выбор. Используйте 1, 2 или 3.")
        sys.exit(1)